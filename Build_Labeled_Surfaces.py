"""Build_Labeled_Surfaces.py

Paint-ready cortical surfaces: one continuous mesh per hemisphere whose faces carry an atlas label.

Why: drawing every label as its own mesh leaves gaps along the borders, because the meshes are cut
out of voxel segmentations and do not share edges. A single continuous surface has no gaps.

Run with pvpython from the folder that holds this script:
    pvpython Build_Labeled_Surfaces.py [--atlas DK] [--if-missing] [--check-report]

  --atlas         name of an atlas definition in ./atlases/<name>.ini (default: 'atlas' in config.ini, else DK)
  --if-missing    do nothing when the outputs already exist
  --check-report  after building, compare the report with ./expected/<name>_report.tsv and exit 1 on a mismatch

Steps (all deterministic: the same inputs and parameters give the same files)
  1. Read the whole-hemisphere surface, triangulate it (the vtk files hold triangle strips), smooth it
     (windowed sinc), and compute vertex normals.
  2. Give every vertex the label of the nearest vertex among the label meshes. Vertices farther than
     max_transfer_mm from every label mesh (the medial wall) stay unlabelled.
  3. Smooth the labels: label_smoothing_rounds rounds of majority vote over the mesh neighbours.
  4. A face takes the majority label of its three vertices. A face whose vertices disagree is a border face.

Outputs in ./vtk/labeled/<atlas>/
  Lt_surface.vtk, Rt_surface.vtk  surface; cell arrays LabelID (-1 = unlabelled) and IsBorder
  Lt_border.vtk, Rt_border.vtk    border faces lifted off the surface by border_offset_mm (drawn as a line layer)
  Lt_filler.vtk, Rt_filler.vtk    the medial-wall filler of the atlas definition, smoothed the same way (if defined)
  <atlas>_labels.tsv              LabelID, OBJECT_LABEL, HEMI
  <atlas>_report.tsv              faces per label and the parameters used; the reproducibility check

Parameters can be overridden in a [Labeling] section of config.ini (see config_default.ini).
"""
import argparse
import configparser
import os
import sys
from pathlib import Path

import numpy as np
from vtkmodules.util import numpy_support
from vtkmodules.vtkCommonCore import vtkObject, vtkSMPTools
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import (
    vtkExtractCells, vtkPolyDataNormals, vtkTriangleFilter, vtkWindowedSincPolyDataFilter,
)
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkCommonCore import vtkIdList
from vtkmodules.vtkCommonDataModel import vtkStaticPointLocator
from vtkmodules.vtkIOLegacy import vtkPolyDataReader, vtkPolyDataWriter

vtkObject.GlobalWarningDisplayOff()
vtkSMPTools.Initialize(1)  # one thread: threaded normals differ in the last float digits from run to run

HERE = Path(__file__).resolve().parent
CONFIG_PATH = Path(os.environ.get("BRAINGRAPH_CONFIG", HERE / "config.ini"))
MESH_DIR = HERE / "vtk" / "without_val"

DEFAULTS = {
    "max_transfer_mm": 3.0,
    "label_smoothing_rounds": 6,
    "mesh_smoothing_iterations": 25,
    "mesh_smoothing_passband": 0.08,
    "border_offset_mm": 0.12,
}


def load_parameters():
    params = dict(DEFAULTS)
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    if cfg.has_section("Labeling"):
        for key, default in DEFAULTS.items():
            if cfg.has_option("Labeling", key):
                params[key] = type(default)(cfg.get("Labeling", key).split("#")[0].strip())
    return params


def read_poly(path):
    r = vtkPolyDataReader()
    r.SetFileName(str(path))
    r.Update()
    return r.GetOutput()


def write_poly(poly, path):
    w = vtkPolyDataWriter()
    w.SetFileName(str(path))
    w.SetInputData(poly)
    w.SetFileTypeToBinary()
    w.Write()


def smoothed_surface(path, params):
    tri = vtkTriangleFilter()
    tri.SetInputData(read_poly(path))
    tri.PassLinesOff()
    tri.PassVertsOff()
    s = vtkWindowedSincPolyDataFilter()
    s.SetInputConnection(tri.GetOutputPort())
    s.SetNumberOfIterations(params["mesh_smoothing_iterations"])
    s.SetPassBand(params["mesh_smoothing_passband"])
    s.NonManifoldSmoothingOn()
    s.NormalizeCoordinatesOn()
    for flip in (False, True):
        n = vtkPolyDataNormals()
        n.SetInputConnection(s.GetOutputPort())
        n.SetFeatureAngle(80)
        n.SplittingOff()
        n.ComputePointNormalsOn()
        if flip:
            n.FlipNormalsOn()
        n.Update()
        out = n.GetOutput()
        if normals_point_outward(out):
            return out
    sys.exit(f"Could not orient the normals of {path} outward.")


def normals_point_outward(poly):
    """True when the normals point away from the centroid (these are roughly convex hemispheres)."""
    p = numpy_support.vtk_to_numpy(poly.GetPoints().GetData()).astype(np.float64)
    n = numpy_support.vtk_to_numpy(poly.GetPointData().GetNormals()).astype(np.float64)
    return float(np.mean(np.sum(n * (p - p.mean(axis=0)), axis=1))) > 0


def triangles_of(poly):
    """(n_faces, 3) vertex ids; the surface is already triangulated."""
    cells = numpy_support.vtk_to_numpy(poly.GetPolys().GetConnectivityArray())
    return cells.reshape(-1, 3).astype(np.int64)


def nearest_label(points, label_points, label_ids, max_dist):
    pd = vtkPolyData()
    from vtkmodules.vtkCommonCore import vtkPoints
    vp = vtkPoints()
    vp.SetData(numpy_support.numpy_to_vtk(label_points.astype(np.float32), deep=True))
    pd.SetPoints(vp)
    loc = vtkStaticPointLocator()
    loc.SetDataSet(pd)
    loc.BuildLocator()
    out = np.full(len(points), -1, dtype=np.int64)
    for v in range(len(points)):
        j = loc.FindClosestPoint(points[v])
        d = points[v] - label_points[j]
        if float(d @ d) <= max_dist * max_dist:
            out[v] = label_ids[j]
    return out


def smooth_labels(lab, tris, n_labels, rounds):
    """Majority vote over mesh neighbours (own label included). Index 0 = unlabelled."""
    n = len(lab)
    lab = lab + 1  # shift so that -1 -> 0
    src = np.concatenate([tris[:, 0], tris[:, 1], tris[:, 2], tris[:, 1], tris[:, 2], tris[:, 0]])
    dst = np.concatenate([tris[:, 1], tris[:, 2], tris[:, 0], tris[:, 0], tris[:, 1], tris[:, 2]])
    for _ in range(rounds):
        counts = np.zeros((n, n_labels + 1), dtype=np.int32)
        np.add.at(counts, (src, lab[dst]), 1)
        counts[np.arange(n), lab] += 1
        best = counts.max(axis=1)
        keep = counts[np.arange(n), lab] == best  # a tie keeps the current label
        lab = np.where(keep, lab, counts.argmax(axis=1))
    return lab - 1


def face_labels(vlab, tris):
    a, b, c = vlab[tris[:, 0]], vlab[tris[:, 1]], vlab[tris[:, 2]]
    face = np.where((a == b) | (a == c), a, np.where(b == c, b, a))
    border = ~((a == b) & (b == c))
    return face, border


def border_layer(surface, is_border, offset):
    ids = vtkIdList()
    for c in np.nonzero(is_border)[0]:
        ids.InsertNextId(int(c))
    ex = vtkExtractCells()
    ex.SetInputData(surface)
    ex.SetCellList(ids)
    g = vtkGeometryFilter()
    g.SetInputConnection(ex.GetOutputPort())
    g.Update()
    out = vtkPolyData()
    out.DeepCopy(g.GetOutput())
    pts = numpy_support.vtk_to_numpy(out.GetPoints().GetData())
    nrm = numpy_support.vtk_to_numpy(out.GetPointData().GetNormals())
    pts += (nrm * offset).astype(pts.dtype)
    out.GetCellData().Initialize()
    return out


def build(atlas, params):
    ini = configparser.ConfigParser()
    ini.read(HERE / "atlases" / f"{atlas}.ini", encoding="utf-8")
    a = ini["Atlas"]
    if a["source_type"] != "parcel-vtk":
        sys.exit(f"source_type '{a['source_type']}' is not implemented (see atlases/{atlas}.ini)")
    rows = []
    with open(HERE / a["labels_table"]) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            lab, hemi, vtk_file = line.rstrip("\n").split("\t")[:3]
            rows.append((lab, hemi, vtk_file))
    label_id = {lab: i for i, (lab, _, _) in enumerate(rows)}  # 0-based, shared by both hemispheres

    out_dir = HERE / "vtk" / "labeled" / atlas
    out_dir.mkdir(parents=True, exist_ok=True)
    report = []
    for hemi, prefix in (("L", "Lt"), ("R", "Rt")):
        surface = smoothed_surface(MESH_DIR / a[f"surface_{hemi}"], params)
        pts = numpy_support.vtk_to_numpy(surface.GetPoints().GetData()).astype(np.float64)
        tris = triangles_of(surface)

        lp, li = [], []
        for lab, h, vtk_file in rows:
            if h != hemi:
                continue
            p = numpy_support.vtk_to_numpy(read_poly(MESH_DIR / vtk_file).GetPoints().GetData())
            lp.append(p.astype(np.float64))
            li.append(np.full(len(p), label_id[lab], dtype=np.int64))
        vlab = nearest_label(pts, np.concatenate(lp), np.concatenate(li), params["max_transfer_mm"])
        vlab = smooth_labels(vlab, tris, len(rows), params["label_smoothing_rounds"])
        flab, fborder = face_labels(vlab, tris)

        surface.GetCellData().AddArray(_int_array(flab, "LabelID"))
        surface.GetCellData().AddArray(_int_array(fborder.astype(np.int64), "IsBorder"))
        write_poly(surface, out_dir / f"{prefix}_surface.vtk")
        write_poly(border_layer(surface, fborder, params["border_offset_mm"]), out_dir / f"{prefix}_border.vtk")
        if a.get(f"filler_{hemi}"):
            write_poly(smoothed_surface(MESH_DIR / a[f"filler_{hemi}"], params), out_dir / f"{prefix}_filler.vtk")

        report.append((hemi, "(unlabelled)", int((flab < 0).sum()), int(((flab < 0) & fborder).sum())))
        for lab, h, _ in rows:
            if h == hemi:
                m = flab == label_id[lab]
                report.append((hemi, lab, int(m.sum()), int((m & fborder).sum())))

    with open(out_dir / f"{atlas}_labels.tsv", "w") as f:
        f.write("LabelID\tOBJECT_LABEL\tHEMI\n")
        for lab, h, _ in rows:
            f.write(f"{label_id[lab]}\t{lab}\t{h}\n")
    with open(out_dir / f"{atlas}_report.tsv", "w") as f:
        for k in DEFAULTS:
            f.write(f"# {k} = {params[k]}\n")
        f.write("HEMI\tOBJECT_LABEL\tN_FACES\tN_BORDER_FACES\n")
        for r in report:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"Wrote {out_dir}")
    return out_dir


def _int_array(values, name):
    arr = numpy_support.numpy_to_vtk(np.ascontiguousarray(values, dtype=np.int32), deep=True)
    arr.SetName(name)
    return arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas", default=None)
    ap.add_argument("--if-missing", action="store_true")
    ap.add_argument("--check-report", action="store_true")
    args = ap.parse_args()
    if args.atlas is None:
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_PATH, encoding="utf-8")
        args.atlas = cfg.get("Settings", "atlas", fallback="DK").split("#")[0].strip().strip("'\"")

    out_dir = HERE / "vtk" / "labeled" / args.atlas
    needed = [out_dir / n for n in ("Lt_surface.vtk", "Rt_surface.vtk", "Lt_border.vtk", "Rt_border.vtk",
                                    f"{args.atlas}_labels.tsv")]
    ini = configparser.ConfigParser()
    ini.read(HERE / "atlases" / f"{args.atlas}.ini", encoding="utf-8")
    needed += [out_dir / f"{p}_filler.vtk" for h, p in (("L", "Lt"), ("R", "Rt")) if ini["Atlas"].get(f"filler_{h}")]
    if args.if_missing and all(p.exists() for p in needed):
        print(f"{out_dir} already exists (--if-missing). Nothing to do.")
        return
    build(args.atlas, load_parameters())

    if args.check_report:
        expected = HERE / "expected" / f"{args.atlas}_report.tsv"
        if not expected.exists():
            sys.exit(f"{expected} does not exist.")
        if expected.read_text() != (out_dir / f"{args.atlas}_report.tsv").read_text():
            sys.exit(f"MISMATCH: {out_dir / (args.atlas + '_report.tsv')} differs from {expected}")
        print("The report matches the expected report.")


if __name__ == "__main__":
    main()
