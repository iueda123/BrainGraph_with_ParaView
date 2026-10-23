#!/usr/bin/env python
# coding: utf-8
"""
Compose_Figure.py

Draws the brain views with the ParaView renderer (generate_horizontally_without_cbar.sh) and assembles them into
one publication-style figure: column titles (Left lateral, ...), row labels, an optional group title over the
columns, a colour bar with tick labels, and a grey swatch that explains the colour of NA regions.

The generate_*.sh scripts call this when the settings file says  style = panel  (the default; see config_default.ini).
It can be run by hand, and another program can import make_figure().

USAGE (in this folder)
    python Compose_Figure.py [--direction h|v] [--cbar horizontal|vertical|none] [--out FILE] [--force]
    python Compose_Figure.py --print-style

Settings: [Settings] as for the other scripts, plus the optional [Figure] section (see config_default.ini).
  * With no rows in [Figure], one row is made from value_table_file. Cortical labels and deep-structure labels
    in that table are rendered separately (the deep structures need the translucent cortical shell behind them)
    and placed side by side.
  * --direction v stacks the views of each row in a column instead of side by side.
"""
import argparse
import configparser
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RENDER_SCRIPT = "generate_horizontally_without_cbar.sh"

VIEWS = ["L_Lat", "L_Med", "R_Med", "R_Lat"]  # the order in which they are shown
VIEW_TITLE = {"L_Lat": "Left lateral", "L_Med": "Left medial", "R_Med": "Right medial", "R_Lat": "Right lateral"}
GROUP_TITLE = {"cortex": "Cortex", "deep": "Deep structures"}
DEEP_LABEL = re.compile(r"^(?:[LR]_(?:thal|caud|put|pal|hippo|amyg|accumb|LatVent)|CC_\d)$")
NON_DATA_LABEL = re.compile(r"^[LR]_(?:Cortex|Empty_CC)$")

FONT_CANDIDATES = {
    "r": ["/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "b": ["/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "i": ["/usr/share/fonts/truetype/msttcorefonts/Arial_Italic.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"],
}

FIG_W = 2100            # px; about 178 mm at 300 dpi
FONT_PX = 29            # 7 pt at 300 dpi
GAP, GROUP_GAP = 14, 70


# ---- settings --------------------------------------------------------------------------------------
def read_config(path=None):
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str
    cfg.read(path or os.environ.get("BRAINGRAPH_CONFIG", "./config.ini"), encoding="utf-8")
    return cfg


def clean(value):
    return value.split("#")[0].strip().strip("'\"")


def figure_option(cfg, key, default=""):
    if cfg.has_option("Figure", key):
        return cfg.get("Figure", key).split("#")[0].strip() if key not in ("cbar_label", "na_label") else cfg.get("Figure", key).strip()
    return default


def parse_markup(text):
    """'Cohen's *d* (patient)' -> [(text, 'r' | 'i')]; *...* is italic."""
    parts = []
    for i, chunk in enumerate(re.split(r"\*", text)):
        if chunk:
            parts.append((chunk, "i" if i % 2 else "r"))
    return parts


def is_deep(label):
    return bool(DEEP_LABEL.match(label))


def read_value_table(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.rstrip("\n").split("\t")
        if cols[0] == "OBJECT_LABEL":
            continue
        rows.append((cols[0], cols[1] if len(cols) > 1 else ""))
    return rows


def split_table(path, work, tag):
    """Split a value table into its cortical part and its deep-structure part. Returns {kind: path}."""
    out = {}
    rows = [r for r in read_value_table(path) if not NON_DATA_LABEL.match(r[0])]
    for kind, keep in (("cortex", lambda l: not is_deep(l)), ("deep", is_deep)):
        part = [r for r in rows if keep(r[0])]
        if part:
            p = work / "tables" / f"{tag}_{kind}.tsv"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("".join(f"{k}\t{v}\n" for k, v in part), encoding="utf-8")
            out[kind] = p
    return out


# ---- running the renderer --------------------------------------------------------------------------
def tool_state():
    def git(*a):
        return subprocess.run(["git", "-C", str(HERE), *a], capture_output=True, text=True).stdout.strip()
    return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--untracked-files=no"))}


def render_views(tag, table, kind, cfg, work, image_scale, border_opacity, force):
    """Run the renderer for one value table; return {view: png path}. Results are cached by content."""
    settings = {k: v for k, v in cfg.items("Settings")}
    settings.update({"ValueName": "'Value'", "Unit": "''", "image_scale": str(image_scale),
                     "border_opacity": str(border_opacity if kind == "cortex" else 0.0)})
    body = Path(table).read_text(encoding="utf-8")
    other = {s: dict(cfg.items(s)) for s in cfg.sections() if s not in ("Settings", "Figure")}
    key = hashlib.sha1((body + json.dumps([settings, other], sort_keys=True) + tool_state()["commit"]).encode()).hexdigest()[:8]
    run_dir = work / "runs" / f"{tag}__{key}"
    views = {v: run_dir / "views" / f"{tag}_Value_{v}.png" for v in VIEWS}
    if not force and all(p.exists() for p in views.values()):
        return views
    shutil.rmtree(run_dir, ignore_errors=True)
    (run_dir / "views").mkdir(parents=True)
    table_copy = run_dir / f"{tag}.tsv"
    table_copy.write_text(body, encoding="utf-8")
    settings.update({"value_table_file": f"'{table_copy}'", "output_folder": f"'{run_dir / 'views'}'"})
    ini = configparser.ConfigParser(interpolation=None)
    ini.optionxform = str
    ini["Settings"] = settings
    for s, items in other.items():
        ini[s] = items
    ini_path = run_dir / "config.ini"
    with open(ini_path, "w", encoding="utf-8") as f:
        ini.write(f)
    r = subprocess.run(["bash", RENDER_SCRIPT], cwd=HERE, capture_output=True, text=True,
                       env={**os.environ, "BRAINGRAPH_CONFIG": str(ini_path), "BRAINGRAPH_RENDER_ONLY": "1"})
    (run_dir / "log.txt").write_text(r.stdout + r.stderr)
    if r.returncode != 0 or not all(p.exists() for p in views.values()):
        sys.exit(f"The renderer failed for {tag}; see {run_dir / 'log.txt'}")
    return views


def sample_lut(lut, invert, vmin, vmax, work):
    """256 RGB samples (0-1) of the ParaView colour map, so that the colour bar matches the brains."""
    work.mkdir(parents=True, exist_ok=True)
    out = work / f"lut_{re.sub(r'[^A-Za-z0-9]+', '', lut)}_{invert}_{vmin}_{vmax}.json"
    if not out.exists():
        script = work / "sample_lut.py"
        script.write_text(
            "import json, sys\nfrom paraview.simple import *\n"
            "name, inv, lo, hi, out = sys.argv[1], sys.argv[2] == 'True', float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]\n"
            "lut = GetColorTransferFunction('probe')\nlut.RescaleTransferFunction(lo, hi)\nlut.ApplyPreset(name, True)\n"
            "if inv:\n    lut.InvertTransferFunction()\nobj = lut.GetClientSideObject()\n"
            "cols = []\nfor i in range(256):\n    rgb = [0.0, 0.0, 0.0]\n    obj.GetColor(lo + (hi - lo) * i / 255.0, rgb)\n    cols.append(list(rgb))\n"
            "json.dump(cols, open(out, 'w'))\n")
        r = subprocess.run(["pvpython", str(script), lut, str(invert), str(vmin), str(vmax), str(out)],
                           capture_output=True, text=True)
        if not out.exists():
            sys.exit("Could not sample the colour map:\n" + r.stderr[-800:])
    return json.loads(out.read_text())


# ---- composing -------------------------------------------------------------------------------------
def load_fonts(size):
    fonts = {}
    for k, candidates in FONT_CANDIDATES.items():
        path = next((c for c in candidates if Path(c).exists()), None)
        if path is None:
            sys.exit("No usable font found; add one to FONT_CANDIDATES in Compose_Figure.py")
        fonts[k] = ImageFont.truetype(path, size)
    return fonts


def content_box(path):
    """Bounding box (full-size pixels) of everything that is not white."""
    small = Image.open(path).convert("RGB").reduce(4)
    box = small.point(lambda x: 255 if x < 246 else 0).convert("L").getbbox()
    return None if box is None else tuple(4 * v for v in box)


def text_width(d, parts, fonts):
    return sum(d.textlength(t, font=fonts[f]) for t, f in parts)


def draw_text(d, xy, parts, fonts, fill="black"):
    x, y = xy
    for t, f in parts:
        d.text((x, y), t, fill=fill, font=fonts[f])
        x += d.textlength(t, font=fonts[f])


def vertical_text(canvas, center, parts, fonts):
    """Draw text rotated by 90 degrees (reading bottom to top), centred on `center`."""
    d = ImageDraw.Draw(canvas)
    w, h = int(text_width(d, parts, fonts)) + 4, FONT_PX + 12
    strip = Image.new("RGB", (w, h), "white")
    draw_text(ImageDraw.Draw(strip), (2, 2), parts, fonts)
    strip = strip.rotate(90, expand=True)
    canvas.paste(strip, (int(center[0] - strip.width / 2), int(center[1] - strip.height / 2)))


def na_color():
    return tuple(int(255 * 0.74) for _ in range(3))


def compose(grid, col_titles, row_labels, groups, lut_colors, vmin, vmax, ticks, cbar_label, na_label,
            cbar, out, fig_w=FIG_W):
    """
    grid[r][c]      (png path, view) of each cell
    col_titles[c]   text over each column (None for none)
    row_labels[r]   text left of each row ('\\n' breaks lines; '' for none)
    groups          [(title, number of columns)] drawn over the columns, or None
    cbar            'horizontal', 'vertical' or 'none'
    """
    fonts = load_fonts(FONT_PX)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    nrows, ncols = len(grid), len(grid[0])
    boxes = {}
    for row in grid:
        for path, view in row:
            b = content_box(path)
            if b:
                u = boxes.get(view)
                boxes[view] = b if u is None else (min(u[0], b[0]), min(u[1], b[1]), max(u[2], b[2]), max(u[3], b[3]))
    label_w = 0
    if any(row_labels):
        label_w = int(max(probe.textlength(line, font=fonts["b"]) for lab in row_labels for line in lab.split("\n")) + 24)
    bar_w, bar_h = 620, 26
    right_w = 0
    if cbar == "vertical":
        right_w = bar_h + 8 + 10 + int(max(probe.textlength(f"−{abs(t):g}", font=fonts["r"]) for t in ticks)) + 30 + FONT_PX + 20
    several = bool(groups) and len(groups) > 1
    extra = GROUP_GAP - GAP if several else 0
    slot = [max(boxes[g[c][1]][2] - boxes[g[c][1]][0] for g in grid if len(g) > c) for c in range(ncols)]
    scale = (fig_w - label_w - right_w - GAP * (ncols - 1) - extra - 20) / sum(slot)
    slot_px = [int(w * scale) for w in slot]
    row_h = int(max(b[3] - b[1] for b in boxes.values()) * scale)
    has_titles = any(col_titles)
    y_group = 4
    y_title = 4 + (FONT_PX + 10 if several else 0)
    head_h = y_title + (int(FONT_PX * 1.3) if has_titles else 0)
    foot_h = 150 if cbar == "horizontal" else (60 if na_label else 10)
    foot_h = max(foot_h, 60) if na_label else foot_h
    H = head_h + nrows * (row_h + GAP) + foot_h
    if cbar == "vertical":  # the bar needs room for its label, which runs along it
        need = int(text_width(probe, cbar_label, fonts)) + 80 if cbar_label else 300
        H = max(H, head_h + max(need, 300) + 40)
    canvas = Image.new("RGB", (fig_w, H), "white")
    d = ImageDraw.Draw(canvas)

    xs, x, boundary = [], label_w, set()
    if several:
        s = 0
        for _, n in groups[:-1]:
            s += n
            boundary.add(s - 1)
    for c in range(ncols):
        xs.append(x)
        x += slot_px[c] + GAP + (extra if c in boundary else 0)
    for c, title in enumerate(col_titles):
        if title:
            t = [(title, "r")]
            draw_text(d, (xs[c] + (slot_px[c] - text_width(d, t, fonts)) / 2, y_title), t, fonts)
    if several:
        s = 0
        for name, n in groups:
            x0, x1 = xs[s], xs[s + n - 1] + slot_px[s + n - 1]
            t = [(name, "b")]
            draw_text(d, ((x0 + x1 - text_width(d, t, fonts)) / 2, y_group), t, fonts)
            s += n

    y = head_h
    for r, row in enumerate(grid):
        lines = row_labels[r].split("\n") if row_labels[r] else []
        for k, line in enumerate(lines):
            d.text((6, y + row_h / 2 - FONT_PX * (len(lines) / 2 - k) - 2), line, fill="black", font=fonts["b"])
        for c, (path, view) in enumerate(row):
            im = Image.open(path).convert("RGB").crop(boxes[view])
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            canvas.paste(im, (xs[c] + (slot_px[c] - im.width) // 2, y + (row_h - im.height) // 2))
        y += row_h + GAP

    def tick_label(t):
        return (f"{t:g}" if t else "0").replace("-", "−")

    right_edge = fig_w - right_w
    if cbar == "horizontal":
        bx, by = (right_edge - bar_w) // 2, y + 14
        for i in range(bar_w):
            rgb = lut_colors[round(i / (bar_w - 1) * 255)]
            d.line([(bx + i, by), (bx + i, by + bar_h)], fill=tuple(int(255 * c) for c in rgb))
        d.rectangle([bx, by, bx + bar_w, by + bar_h], outline="black", width=1)
        for t in ticks:
            tx = bx + (t - vmin) / (vmax - vmin) * bar_w
            d.line([(tx, by + bar_h), (tx, by + bar_h + 8)], fill="black", width=2)
            lab = [(tick_label(t), "r")]
            draw_text(d, (tx - text_width(d, lab, fonts) / 2, by + bar_h + 10), lab, fonts)
        if cbar_label:
            draw_text(d, ((right_edge - text_width(d, cbar_label, fonts)) / 2, by + bar_h + 10 + FONT_PX + 6), cbar_label, fonts)
        na_xy = (bx - 380, by)
    elif cbar == "vertical":
        bh = int(min(H - head_h - 40, max(0.6 * (H - head_h), 300)))
        bx, by = right_edge + 24, head_h + ((H - head_h) - bh) // 2
        for j in range(bh):
            rgb = lut_colors[round((1 - j / (bh - 1)) * 255)]
            d.line([(bx, by + j), (bx + bar_h, by + j)], fill=tuple(int(255 * c) for c in rgb))
        d.rectangle([bx, by, bx + bar_h, by + bh], outline="black", width=1)
        for t in ticks:
            ty = by + bh - (t - vmin) / (vmax - vmin) * bh
            d.line([(bx + bar_h, ty), (bx + bar_h + 8, ty)], fill="black", width=2)
            d.text((bx + bar_h + 12, ty - FONT_PX * 0.6), tick_label(t), fill="black", font=fonts["r"])
        if cbar_label:
            lab_x = bx + bar_h + 12 + max(probe.textlength(tick_label(t), font=fonts["r"]) for t in ticks) + 14 + FONT_PX / 2
            vertical_text(canvas, (lab_x, by + bh / 2), cbar_label, fonts)
        na_xy = (max(label_w, 10), y + 14)
    else:
        na_xy = (max(label_w, 10), y + 14)
    if na_label:
        sx, sy = na_xy
        d.rectangle([sx, sy, sx + bar_h, sy + bar_h], fill=na_color(), outline="black")
        draw_text(d, (sx + bar_h + 10, sy - 1), na_label, fonts)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(300, 300))
    print("wrote", out, canvas.size)
    return Path(out)


# ---- figure -----------------------------------------------------------------------------------------
def make_figure(cfg, rows, columns, group_titles, ticks, cbar_label, na_label, out, work, direction="h", cbar="horizontal",
                image_scale=3, force=False, fig_w=FIG_W):
    """
    cfg           ConfigParser holding the [Settings] (and optional [Labeling]) the renderer is run with
    rows          [(label, {'cortex': table path or None, 'deep': table path or None})], or with a third element
                  [(kind, view)] when that row shows other views than `columns`
    columns       [(kind, view)] shown in each row, e.g. [('cortex', 'L_Lat'), ..., ('deep', 'L_Lat')]
    group_titles  [(title, number of columns)] over the columns, or None
    """
    settings = cfg["Settings"]
    lut = clean(settings.get("LUT", "Cool to Warm"))
    invert = clean(settings.get("lut_invert", "false")).lower() == "true"
    vmin = float(clean(settings["value_range_ll_on_figure"]))
    vmax = float(clean(settings["value_range_ul_on_figure"]))
    if vmax < vmin:
        vmin, vmax = vmax, vmin
    border = float(clean(settings.get("border_opacity", "0")))
    if not ticks:
        ticks = [vmin + (vmax - vmin) * i / 4 for i in range(5)]
    work = Path(work)
    images = {}
    row_cells = [row[2] if len(row) > 2 else [(k, v) for k, v in columns if row[1].get(k)] for row in rows]
    rows = [(row[0], row[1]) for row in rows]
    for r, (_, tables) in enumerate(rows):
        for kind in dict.fromkeys(k for k, _ in row_cells[r]):
            if tables.get(kind):
                images[(r, kind)] = render_views(f"row{r}_{kind}", tables[kind], kind, cfg, work, image_scale, border, force)
                print(f"  row {r + 1} {kind}: done", flush=True)
    grid = [[(images[(r, kind)][view], view) for kind, view in row_cells[r] if (r, kind) in images] for r in range(len(rows))]
    labels = [lab for lab, _ in rows]
    longest = max(row_cells, key=len)
    col_titles = [VIEW_TITLE[v] for _, v in longest]
    columns = longest
    if direction == "v":
        # transpose: one column per original row, one row per original column
        t_grid = [[grid[r][c] for r in range(len(grid))] for c in range(len(grid[0]))]
        several = bool(group_titles) and len(group_titles) > 1
        t_labels, c = [], 0
        for g, (title, n) in enumerate(group_titles or [("", len(columns))]):
            for _ in range(n):
                v = columns[c][1]
                t_labels.append(VIEW_TITLE[v] if not several else f"{title}\n{VIEW_TITLE[v]}")
                c += 1
        grid, col_titles, labels, group_titles = t_grid, labels, t_labels, None
        fig_w = min(fig_w, 560 * len(grid[0]) + 520)  # a column of views is narrow
        if not any(col_titles):
            col_titles = [None] * len(grid[0])
    lut_colors = sample_lut(lut, invert, vmin, vmax, work)
    return compose(grid, col_titles, labels, group_titles, lut_colors, vmin, vmax, ticks, parse_markup(cbar_label),
                   parse_markup(na_label) if na_label else None, cbar, out, fig_w)


def figure_from_config(cfg, direction, cbar, out, force):
    work = Path(clean(cfg.get("Settings", "output_folder"))) / ".braingraph_work"
    table = Path(clean(cfg.get("Settings", "value_table_file")))
    image_scale = int(figure_option(cfg, "image_scale", "3"))
    value_name = clean(cfg.get("Settings", "ValueName"))
    rows_text = figure_option(cfg, "rows")
    rows = []
    if rows_text.strip():
        for line in cfg.get("Figure", "rows").splitlines():
            if not line.strip():
                continue
            label, cortex, deep = [x.strip() for x in (line.split("|") + ["", ""])[:3]]
            rows.append((label.replace("\\n", "\n"), {"cortex": cortex or None, "deep": deep or None}))
    else:
        tables = split_table(table, work, table.stem)
        rows.append(("", {k: str(p) for k, p in tables.items()}))
    kinds = [k for k in ("cortex", "deep") if any(t.get(k) for _, t in rows)]
    default_views = {"cortex": "L_Lat L_Med R_Med R_Lat", "deep": "L_Lat R_Lat"}
    columns, groups = [], []
    for k in kinds:
        views = figure_option(cfg, f"views_{k}", default_views[k]).split()
        columns += [(k, v) for v in views]
        groups.append((GROUP_TITLE[k], len(views)))
    titles = figure_option(cfg, "group_titles")
    if titles:
        groups = [(t.strip(), n) for t, (_, n) in zip(titles.split(","), groups)]
    if len(groups) < 2:
        groups = None
    ticks = [float(x) for x in figure_option(cfg, "ticks").split()]
    cbar_label = figure_option(cfg, "cbar_label", value_name)
    unit = clean(cfg.get("Settings", "Unit", fallback=""))
    if cbar_label == value_name and unit:
        cbar_label = f"{value_name} ({unit})"
    na_label = figure_option(cfg, "na_label")
    if not out:
        stem = table.stem if not rows_text.strip() else "Figure"
        out = Path(clean(cfg.get("Settings", "output_folder"))) / f"{stem}_{value_name.replace(' ', '')}.png"
    return make_figure(cfg, rows, columns, groups, ticks, cbar_label, na_label, out, work, direction, cbar, image_scale, force)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--direction", choices=["h", "v"], default="h")
    ap.add_argument("--cbar", choices=["horizontal", "vertical", "none"], default="horizontal")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--force", action="store_true", help="re-run the renderer even when its output exists")
    ap.add_argument("--print-style", action="store_true", help="print the 'style' setting (panel or classic) and exit")
    args = ap.parse_args()
    cfg = read_config()
    if args.print_style:
        print(figure_option(cfg, "style", "panel"))
        return
    figure_from_config(cfg, args.direction, args.cbar, args.out, args.force)


if __name__ == "__main__":
    main()
