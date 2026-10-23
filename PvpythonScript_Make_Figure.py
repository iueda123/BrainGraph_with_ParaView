# PvpythonScript

print("")
print("#################################")
print("# PvpythonScript_Make_Figure.py #")
print("#################################")
print("")

#
# ver 20251030
# 
# --------------------------------------------------------------
#

# Main Settings from args
#
# arg 1: Laterality. "R" or "L".
# arg 2: View. "Lat" or "Med".
# arg 3: Orientation of ColorBar. "vertical" "horizontal", or "none".
# arg 4: shouldForcelyHideEmptySubcorticalStructures. "true" or "false".
# art 5: showPreview. "true" or "false". 

# arg 4 について
# 強制的に値０の皮質下領域を非表示にしたい場合は "true" を指定する

import sys
args = sys.argv
#print(len(args))
if len(args) == 6:
    
    Laterality = args[1]
    
    View = args[2]
    
    # Orientation of ColorBar
    orientation_of_color_bar = args[3].lower()
    if orientation_of_color_bar == "vertical": 
        displayColorBarAndLegend = True
        makeBarOrientationHorizontal = False
    elif orientation_of_color_bar == "horizontal": 
        displayColorBarAndLegend = True
        makeBarOrientationHorizontal = True
    elif orientation_of_color_bar == "none": 
        displayColorBarAndLegend = False
        makeBarOrientationHorizontal = True
    else: 
        import sys
        sys.stderr.write('Error occurred! Plese specify \"vertical\", \"horizontal\", or \"none\" for ColorBarOrientation.')
        sys.exit(1)

    # shouldForcelyHideEmptySubcorticalStructures
    if args[4].lower() == "true": 
        shouldForcelyHideEmptySubcorticalStructures = True
    else: 
        shouldForcelyHideEmptySubcorticalStructures = False

    # showPreview
    if args[5].lower() == "true": 
        showPreview = True
    else: 
        showPreview = False
        
else: 
    Laterality = "L"
    View = "Lat"
    displayColorBarAndLegend = True
    makeBarOrientationHorizontal = True   
    shouldForcelyHideEmptySubcorticalStructures = False
    showPreview = True
    

print("Laterality: " + Laterality)
print("View: " + View)
print("displayColorBarAndLegend: " + str(displayColorBarAndLegend))
print("makeBarOrientationHorizontal: " + str(makeBarOrientationHorizontal) )
print("shouldForcelyHideEmptySubcorticalStructures: " + str(shouldForcelyHideEmptySubcorticalStructures))
print("showPreview: " + str(showPreview))

# --------------------------------------------------------------
#
# Other Settings from config.ini
# 
#

import configparser
config = configparser.ConfigParser()
import os
# BRAINGRAPH_CONFIG: path of the settings file (default ./config.ini); lets a caller run the tool without editing config.ini
config.read(os.environ.get('BRAINGRAPH_CONFIG', './config.ini'), encoding='utf-8')

# UL_on_Fig, LL_on_Fig
UL_on_Fig = float( config.get('Settings', 'value_range_ul_on_figure') )
LL_on_Fig = float( config.get('Settings', 'value_range_ll_on_figure') )
if UL_on_Fig < LL_on_Fig: 
    tmp = LL_on_Fig
    LL_on_Fig = UL_on_Fig
    UL_on_Fig = tmp
print("UL_on_Fig: " + str(UL_on_Fig))
print("LL_on_Fig: " + str(LL_on_Fig))

# LUT
LUT = config.get('Settings', 'LUT')
LUT = LUT.replace("\"", "").replace("\'", "")
print("LUT: " + LUT)

# ValueName
ValueName = config.get('Settings', 'ValueName')
ValueName = ValueName.replace("\"", "").replace("\'", "")
print("ValueName: " + ValueName)

# Unit
Unit = config.get('Settings', 'Unit')
Unit = Unit.replace("\"", "").replace("\'", "")
print("Unit: " + Unit)


# SPECULAR
SPECULAR = float( config.get('Settings', 'SPECULAR') )
print("SPECULAR: " + str(SPECULAR))

# --- Settings added with the painted-surface mode (all optional; the defaults keep the old behaviour) ---
def get_optional_setting(key, default):
    if config.has_option('Settings', key):
        return config.get('Settings', key).split('#')[0].strip().replace("\"", "").replace("\'", "")
    return default

# surface_mode: 'parcels' draws every label as its own mesh (the former behaviour).
#               'painted' paints one continuous cortical surface per hemisphere (needs Build_Labeled_Surfaces.py).
SURFACE_MODE = get_optional_setting('surface_mode', 'parcels')
ATLAS = get_optional_setting('atlas', 'DK')
# border_opacity: opacity of the thin lines drawn where the label changes (0 = no lines). painted mode only.
BORDER_OPACITY = float(get_optional_setting('border_opacity', '0'))
BORDER_COLOR = [float(x) for x in get_optional_setting('border_color', '0.25, 0.25, 0.25').split(',')]
# na_color: colour of cortical labels that have no value in the value table. painted mode only.
NA_COLOR = [float(x) for x in get_optional_setting('na_color', '0.74, 0.74, 0.74').split(',')]
# representation: how the deep structures are drawn. 'Wireframe' (former behaviour) or 'Surface'.
REPRESENTATION = get_optional_setting('representation', 'Wireframe')
# surface_specular: specular of the painted cortical surface and (when representation = Surface) the deep structures.
SURFACE_SPECULAR = float(get_optional_setting('surface_specular', '0.12'))
# lut_invert: reverse the colour map. ParaView's single-hue presets (Reds, Blues, ...) run from dark (low) to light (high).
LUT_INVERT = get_optional_setting('lut_invert', 'false').lower() == 'true'
print("SURFACE_MODE: " + SURFACE_MODE)
print("ATLAS: " + ATLAS)
print("BORDER_OPACITY: " + str(BORDER_OPACITY))
print("NA_COLOR: " + str(NA_COLOR))
print("REPRESENTATION: " + REPRESENTATION)

# OUTPUT_FOLDER
OUTPUT_FOLDER = config.get('Settings', 'output_folder')
OUTPUT_FOLDER = OUTPUT_FOLDER.replace("\"", "").replace("\'", "")
print("OUTPUT_FOLDER: " + OUTPUT_FOLDER)

# OUTPUT_FILE_NAME_PREFIX
value_table_file = config.get('Settings', 'value_table_file')
import pathlib
OUTPUT_FILE_NAME_PREFIX = pathlib.Path(value_table_file).stem
print("OUTPUT_FILE_NAME_PREFIX: " + OUTPUT_FILE_NAME_PREFIX)


# --------------------------------------------------------------


# trace generated using paraview version 5.12.0-RC1
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 12

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'Legacy VTK Reader'





#
# 値ありVTKファイルをロードして生成したオブジェクトを配列に格納 
#

Folder_Roi_with_Val = "./vtk/with_val"

load_taraget_vtk_file_names = []

def get_file_names_with_extension(folder_path, target_extension):
    file_names = []
    import os
    for filename in os.listdir(folder_path):
        if filename.endswith(target_extension):
            file_names.append(filename)
    return file_names

#load_taraget_vtk_file_names = get_file_names_with_extension(Folder_Roi_with_Val, ".vtk") # 全てをロード

def get_SurfaceAreaVtkFileNames(folder_path, lat):
    """
    指定されたフォルダから皮質領域のVTKファイル名を取得する関数

    Args:
        folder_path (str): VTKファイルが格納されているフォルダパス
        lat (str): 側性を指定。"L"（左半球）または "R"（右半球）

    Returns:
        list: 条件に一致するVTKファイル名のリスト
              左半球の場合は "-lh-" を含むファイル名、
              右半球の場合は "-rh-" を含むファイル名を返す
    """
    file_names = []
    import re    
    import os
    # For Surface Areas
    for filename in os.listdir(folder_path):
        #filename = "048_ctx-rh-middletemporal.vtk"
        if lat == "L":
            rgx_str = r'^[0-9]+.+(-lh-).+vtk$'
        else: 
            rgx_str = r'^[0-9]+.+(-rh-).+vtk$'

        regex = re.compile(rgx_str)
        so = regex.search(filename) # search()は最初のマッチング結果のみに対応するオブジェクトを生成
        #print(so)  # マッチしなかったらNoneが返ってくる
        if so != None:
            file_names.append(filename)    
    return file_names


def get_SubcorticalAreaVtkFileNames(folder_path, lat):
    file_names = []
    import re    
    import os
    # For Subcortical Areas
    for filename in os.listdir(folder_path):
        #filename = "074_Left-Thalamus.vtk"
        if lat == "L":
            rgx_str = r'^[0-9]+.+(_Left-).+vtk$'
        else: 
            rgx_str = r'^[0-9]+.+(_Right-).+vtk$'

        regex = re.compile(rgx_str)
        so = regex.search(filename) # search()は最初のマッチング結果のみに対応するオブジェクトを生成
        #print(so)  # マッチしなかったらNoneが返ってくる
        if so != None:
            file_names.append(filename)         
    return file_names


def get_CCVtkFileNames(folder_path, lat):
    file_names = []
    import re    
    import os
    # For CC
    for filename in os.listdir(folder_path):
        #filename = "069_CC_Posterior.vtk"
        rgx_str = r'^[0-9]+.+(_CC_).+vtk$'
        regex = re.compile(rgx_str)
        so = regex.search(filename) # search()は最初のマッチング結果のみに対応するオブジェクトを生成
        #print(so)  # マッチしなかったらNoneが返ってくる
        if so != None:
            file_names.append(filename)
    return file_names


def get_LatVentVtkFileNames(folder_path, lat):
    file_names = []
    import re    
    import os
    # For LatVent
    for filename in os.listdir(folder_path):
        #filename = "Lt_LatVent.vtk"
        if lat == "L":
            rgx_str = r'^Lt_LatVent\.vtk$'
        else: 
            rgx_str = r'^Rt_LatVent\.vtk$'
    
        regex = re.compile(rgx_str)
        so = regex.search(filename) # search()は最初のマッチング結果のみに対応するオブジェクトを生成
        #print(so)  # マッチしなかったらNoneが返ってくる
        if so != None:
            file_names.append(filename)
    return file_names


# 
# painted mode: which labels of the atlas does the value table contain for this hemisphere?
#
PAINTED = (SURFACE_MODE == 'painted')
LABELED_DIR = "./vtk/labeled/" + ATLAS
painted_values = {}   # label ID -> value
painted_active = False
import os
if PAINTED:
    import csv
    label_ids = {}
    with open(LABELED_DIR + "/" + ATLAS + "_labels.tsv") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["HEMI"] == Laterality:
                label_ids[row["OBJECT_LABEL"]] = int(row["LabelID"])
    value_table_path = value_table_file.replace("\"", "").replace("\'", "")
    with open(value_table_path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            if cols[0] in label_ids and len(cols) > 1 and cols[1].strip() not in ("", "NA", "NaN", "nan"):
                painted_values[label_ids[cols[0]]] = float(cols[1])
    # A hemisphere is painted when the table names at least one of its labels (a label with NA counts).
    with open(value_table_path) as f:
        painted_active = any(l.split("\t")[0] in label_ids for l in f if not l.startswith("#") and l.strip())
print("PAINTED: " + str(PAINTED) + " / painted_active: " + str(painted_active))

load_taraget_vtk_file_names = []
if not painted_active:
    load_taraget_vtk_file_names = get_SurfaceAreaVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード
load_taraget_vtk_file_names = load_taraget_vtk_file_names  +  get_SubcorticalAreaVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード
load_taraget_vtk_file_names = load_taraget_vtk_file_names  +  get_CCVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード
load_taraget_vtk_file_names = load_taraget_vtk_file_names  +  get_LatVentVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード


# Load Target VTK Files
# The values are stored in the "normals" array of these files (see Infuse_Values_into_VTK_Files.py), and ParaView
# also takes that array as the surface normals for lighting. With representation = Surface that makes the
# shading wrong, so the mesh is smoothed and given real normals ("SurfaceNormals"); "normals" stays a plain value array.
SMOOTH_AND_RENORMAL_SCRIPT = """
import numpy as np
from vtkmodules.util import numpy_support
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals, vtkTriangleFilter, vtkWindowedSincPolyDataFilter
src = self.GetInput()
values = src.GetPointData().GetArray("normals")
tri = vtkTriangleFilter(); tri.SetInputData(src); tri.PassLinesOff(); tri.PassVertsOff()
sm = vtkWindowedSincPolyDataFilter(); sm.SetInputConnection(tri.GetOutputPort())
sm.SetNumberOfIterations(25); sm.SetPassBand(0.08); sm.NonManifoldSmoothingOn(); sm.NormalizeCoordinatesOn()
nm = vtkPolyDataNormals(); nm.SetInputConnection(sm.GetOutputPort())
nm.SetFeatureAngle(80); nm.SplittingOff(); nm.ComputePointNormalsOn(); nm.Update()
out = self.GetOutput()
out.ShallowCopy(nm.GetOutput())
out.GetPointData().GetNormals().SetName("SurfaceNormals")
keep = numpy_support.numpy_to_vtk(numpy_support.vtk_to_numpy(values).copy(), deep=True)
keep.SetName("normals")
out.GetPointData().AddArray(keep)
"""

def load_region_with_val(vtk_file_name, folder=Folder_Roi_with_Val):
    reader = LegacyVTKReader(registrationName=vtk_file_name, FileNames=[folder + '/' + vtk_file_name])
    if REPRESENTATION != 'Surface':
        return reader
    smoothed = ProgrammableFilter(registrationName=vtk_file_name + "_smoothed", Input=reader)
    smoothed.OutputDataSetType = 'vtkPolyData'
    smoothed.Script = SMOOTH_AND_RENORMAL_SCRIPT
    return smoothed

Regions_with_Val = []
for vtk_file_name in load_taraget_vtk_file_names:
    Regions_with_Val.append( load_region_with_val(vtk_file_name) )

#
# painted mode: deep structures that the value table lists with an empty or NA value are drawn in na_color
# (they have no with_val file, so their plain meshes are used)
#
Folder_Roi_without_Val_Early = "./vtk/without_val"
na_deep_regions = []
if PAINTED:
    label_to_file = {}
    with open("./VtkfileTable.tsv") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            label_to_file[cols[0]] = cols[1]
    deep_names = get_SubcorticalAreaVtkFileNames(Folder_Roi_without_Val_Early, Laterality) + get_LatVentVtkFileNames(Folder_Roi_without_Val_Early, Laterality)
    with open(value_table_path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            is_na = len(cols) < 2 or cols[1].strip() in ("", "NA", "NaN", "nan")
            if is_na and label_to_file.get(cols[0]) in deep_names:
                na_deep_regions.append(load_region_with_val(label_to_file[cols[0]], folder=Folder_Roi_without_Val_Early))



#
# 値なしVTKファイルをロード
#
Folder_Roi_without_Val = "./vtk/without_val"

ribbonvtk = None
empty_ccvtk = None
hippo_vtk = None
amygdala_vtk = None

shouldLoadEmptySubcorticalStructures = None
if( painted_active or len(get_SurfaceAreaVtkFileNames(Folder_Roi_with_Val, Laterality)) > 0 ): 
    # ./vtk/with_val フォルダ内に皮質領域のVTKファイルが1つ以上存在する場合
    shouldLoadEmptySubcorticalStructures = True
else: 
    # ./vtk/with_val フォルダ内に皮質領域のVTKファイルが1つも存在しない場合
    shouldLoadEmptySubcorticalStructures = False


if shouldForcelyHideEmptySubcorticalStructures:
    shouldLoadEmptySubcorticalStructures = False   # 強制的に値０の皮質下領域を非表示にする

# painted mode: the surface itself covers the cortex, so only the medial-wall filler (Empty_CC) is kept as context
loadHippoAndAmygdala = shouldLoadEmptySubcorticalStructures and not painted_active
    

if Laterality == "L": 
    ribbonvtk = LegacyVTKReader(registrationName='Lt_ribbon.vtk', FileNames=[Folder_Roi_without_Val + '/Lt_ribbon.vtk'])
    if shouldLoadEmptySubcorticalStructures and not painted_active: 
        empty_ccvtk = LegacyVTKReader(registrationName='Lt_Empty_CC.vtk', FileNames=[Folder_Roi_without_Val + '/Lt_Empty_CC.vtk'])
        if loadHippoAndAmygdala:
            hippo_vtk = LegacyVTKReader(registrationName='086_Left-Hippocampus.vtk', FileNames=[Folder_Roi_without_Val + '/078_Left-Hippocampus.vtk'])
            amygdala_vtk = LegacyVTKReader(registrationName='079_Left-Amygdala.vtk.vtk', FileNames=[Folder_Roi_without_Val + '/079_Left-Amygdala.vtk'])
elif Laterality == "R": 
    ribbonvtk = LegacyVTKReader(registrationName='Rt_ribbon.vtk', FileNames=[Folder_Roi_without_Val + '/Rt_ribbon.vtk'])
    if shouldLoadEmptySubcorticalStructures and not painted_active: 
        empty_ccvtk = LegacyVTKReader(registrationName='Rt_Empty_CC.vtk', FileNames=[Folder_Roi_without_Val + '/Rt_Empty_CC.vtk'])
        if loadHippoAndAmygdala:
            hippo_vtk = LegacyVTKReader(registrationName='086_Right-Hippocampus.vtk', FileNames=[Folder_Roi_without_Val + '/086_Right-Hippocampus.vtk'])
            amygdala_vtk = LegacyVTKReader(registrationName='087_Right-Amygdala.vtk', FileNames=[Folder_Roi_without_Val + '/087_Right-Amygdala.vtk'])
        


# -------------------------------------------------------------




# set active source
SetActiveSource(ribbonvtk)

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view

ribbonvtkDisplay = Show(ribbonvtk, renderView1, 'GeometryRepresentation')
ribbonvtkDisplay.Opacity = 0.05 # 透明度の調整

if not empty_ccvtk == None: 
    empty_ccvtkDisplay = Show(empty_ccvtk, renderView1, 'GeometryRepresentation')
    empty_ccvtkDisplay.Opacity = 0.8

if not hippo_vtk == None: 
    hippo_vtkDisplay = Show(hippo_vtk, renderView1, 'GeometryRepresentation')
    hippo_vtkDisplay.Opacity = 0.8
    
if not amygdala_vtk == None: 
    amygdala_vtkDisplay = Show(amygdala_vtk, renderView1, 'GeometryRepresentation')
    amygdala_vtkDisplay.Opacity = 0.8
    
# trace defaults for the display properties.
ribbonvtkDisplay.Representation = 'Surface'

if painted_active:
    # the painted surface is the same mesh as the ribbon; drawing both would only make them fight over the pixels
    Hide(ribbonvtk, renderView1)

# get the material library
materialLibrary1 = GetMaterialLibrary()

# reset view to fit data
renderView1.ResetCamera(False, 0.9)

# set active source
#SetActiveSource(rt_ribbonvtk)

# show data in view
#rt_ribbonvtkDisplay = Show(rt_ribbonvtk, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
#rt_ribbonvtkDisplay.Representation = 'Surface'




normalsLUTColorBar = None
valueLUTColorBar = None

if painted_active:
    import numpy as np
    from vtkmodules.util import numpy_support
    from vtkmodules.vtkIOLegacy import vtkPolyDataReader

    prefix = "Lt" if Laterality == "L" else "Rt"
    reader = vtkPolyDataReader()
    reader.SetFileName(LABELED_DIR + "/" + prefix + "_surface.vtk")
    reader.Update()
    painted_poly = reader.GetOutput()

    # one value per face: the value of its label, NaN where the label has no value (or the face has no label)
    face_label = numpy_support.vtk_to_numpy(painted_poly.GetCellData().GetArray("LabelID"))
    value_of_label = np.full(max(painted_values.keys(), default=0) + 2, np.nan)
    for label_id, value in painted_values.items():
        value_of_label[label_id] = value
    in_range = (face_label >= 0) & (face_label < len(value_of_label))
    face_value = np.full(len(face_label), np.nan)
    face_value[in_range] = value_of_label[face_label[in_range]]
    value_array = numpy_support.numpy_to_vtk(face_value, deep=True)
    value_array.SetName("Value")
    painted_poly.GetCellData().AddArray(value_array)

    paintedSurface = TrivialProducer(registrationName=prefix + "_painted_surface")
    paintedSurface.GetClientSideObject().SetOutput(painted_poly)
    paintedSurface.UpdatePipeline()

    paintedDisplay = Show(paintedSurface, renderView1, 'GeometryRepresentation')
    paintedDisplay.Representation = 'Surface'
    ColorBy(paintedDisplay, ('CELLS', 'Value'))
    paintedDisplay.Specular = SURFACE_SPECULAR

    valueLUT = GetColorTransferFunction('Value')
    valueLUT.RescaleTransferFunction(LL_on_Fig, UL_on_Fig)
    valueLUT.ApplyPreset(LUT, True)
    if LUT_INVERT:
        valueLUT.InvertTransferFunction()
    valueLUT.NanColor = NA_COLOR
    valueLUTColorBar = GetScalarBar(valueLUT, renderView1)
    # when deep structures are drawn too, their colour bar (below) is the one that is shown
    paintedDisplay.SetScalarBarVisibility(renderView1, displayColorBarAndLegend and len(Regions_with_Val) == 0)

    # medial wall: a smoothed, opaque filler instead of the raw (voxel-edged) Empty_CC mesh
    if os.path.exists(LABELED_DIR + "/" + prefix + "_filler.vtk"):
        fillerMesh = LegacyVTKReader(registrationName=prefix + "_filler.vtk", FileNames=[LABELED_DIR + "/" + prefix + "_filler.vtk"])
        fillerDisplay = Show(fillerMesh, renderView1, 'GeometryRepresentation')
        fillerDisplay.ColorArrayName = ['POINTS', '']  # solid colour
        fillerDisplay.AmbientColor = NA_COLOR
        fillerDisplay.DiffuseColor = NA_COLOR
        fillerDisplay.Specular = 0.0

    if BORDER_OPACITY > 0:
        borderLayer = LegacyVTKReader(registrationName=prefix + "_border.vtk", FileNames=[LABELED_DIR + "/" + prefix + "_border.vtk"])
        borderDisplay = Show(borderLayer, renderView1, 'GeometryRepresentation')
        borderDisplay.ColorArrayName = ['POINTS', '']  # solid colour
        borderDisplay.AmbientColor = BORDER_COLOR
        borderDisplay.DiffuseColor = BORDER_COLOR
        borderDisplay.Opacity = BORDER_OPACITY
        borderDisplay.Specular = 0.0


for NA_REGION in na_deep_regions:
    naDisplay = Show(NA_REGION, renderView1, 'GeometryRepresentation')
    naDisplay.ColorArrayName = ['POINTS', '']  # solid colour
    naDisplay.AmbientColor = NA_COLOR
    naDisplay.DiffuseColor = NA_COLOR
    if REPRESENTATION == 'Wireframe':
        naDisplay.SetRepresentationType('Wireframe')
        naDisplay.RenderLinesAsTubes = 1
        naDisplay.LineWidth = 3.0
    else:
        naDisplay.Representation = 'Surface'
        naDisplay.Specular = SURFACE_SPECULAR


for REGION in Regions_with_Val: 

    # set active source
    SetActiveSource(REGION)

    # show data in view
    REGION = Show(REGION, renderView1, 'GeometryRepresentation')

    # trace defaults for the display properties.
    #REGION.Representation = 'Surface'

    # set scalar coloring
    #ColorBy(REGION, ('POINTS', 'normals', 'X'))
    #ColorBy(REGION, ('POINTS', 'normals', 'Y'))
    ColorBy(REGION, ('POINTS', 'normals', 'Z'))
    #ColorBy(REGION, ('POINTS', 'normals', 'Magnitude'))

    # rescale color and/or opacity maps used to include current data range
    #REGION.RescaleTransferFunctionToDataRange(True, False)
    REGION.RescaleTransferFunctionToDataRange(False, False)

    # get 2D transfer function for 'normals'
    normalsTF2D = GetTransferFunction2D('normals')

    # get color transfer function/color map for 'normals'
    normalsLUT = GetColorTransferFunction('normals')
    normalsLUT.TransferFunction2D = normalsTF2D
    normalsLUT.RGBPoints = [0.7350675094279284, 0.231373, 0.298039, 0.752941, 1.724394240868277, 0.865003, 0.865003, 0.865003, 2.713720972308626, 0.705882, 0.0156863, 0.14902]
    normalsLUT.ScalarRangeInitialized = 1.0

    # get opacity transfer function/opacity map for 'normals'
    normalsPWF = GetOpacityTransferFunction('normals')
    normalsPWF.Points = [0.7350675094279284, 0.0, 0.5, 0.0, 2.713720972308626, 1.0, 0.5, 0.0]
    normalsPWF.ScalarRangeInitialized = 1
    
    #
    # Color Scale Adjustments
    # 
    # Rescale transfer function
    normalsLUT.RescaleTransferFunction(LL_on_Fig, UL_on_Fig)
    normalsPWF.RescaleTransferFunction(LL_on_Fig, UL_on_Fig)
    normalsTF2D.RescaleTransferFunction(LL_on_Fig, UL_on_Fig, 0.0, 1.0)
    
    # 
    # LUT指定
    #
    normalsLUT.ApplyPreset(LUT, True)
    if LUT_INVERT:
        normalsLUT.InvertTransferFunction()
    
    #
    # 輝き度合い
    #
    REGION.Specular = SPECULAR
    
    #
    # ワイヤーフレーム化
    #
    if REPRESENTATION == 'Wireframe':
        REGION.SetRepresentationType('Wireframe')
        REGION.RenderLinesAsTubes = 1
        REGION.LineWidth = 3.0
    else:
        REGION.SetRepresentationType('Surface')
        REGION.Specular = SURFACE_SPECULAR
    
    #
    # 後に使うため Color Legend Object の確保
    #
    # get color legend/bar for normalsLUT in view renderView1
    normalsLUTColorBar = GetScalarBar(normalsLUT, renderView1)

    
    #
    # Switch hide color bar/color legend
    #
    #if displayColorBarAndLegendOnlyOnRtLat: 
    #    if Laterality == "R" and View == "Lat": 
    #        REGION.SetScalarBarVisibility(renderView1, True) 
    #    else: 
    #        REGION.SetScalarBarVisibility(renderView1, False) 
    #else: 
    #    REGION.SetScalarBarVisibility(renderView1, True) 
    if displayColorBarAndLegend: 
        REGION.SetScalarBarVisibility(renderView1, True) 
    else: 
        REGION.SetScalarBarVisibility(renderView1, False) 
    
    


# 背景色
renderView1.UseColorPaletteForBackground = 0
renderView1.BackgroundColorMode = 'Single Color'
#renderView1.Background = [0.9372549019607843, 0.9372549019607843, 0.9372549019607843] # 灰色
renderView1.Background = [1.0, 1.0, 1.0]  # 白色


#
# Color Bar and Legend の調整
#

# the colour bar that is formatted below: the deep structures' bar if there is one, else the painted surface's
colorBar = normalsLUTColorBar if normalsLUTColorBar is not None else valueLUTColorBar
if colorBar is None:
    colorBar = GetScalarBar(GetColorTransferFunction('normals'), renderView1)  # nothing coloured: formatting is harmless

# 文字を黒化
colorBar.TitleColor = [0.0, 0.0, 0.0]
colorBar.LabelColor = [0.0, 0.0, 0.0]

# 文字を入れる
colorBar.Title = ValueName # タイトル


if Unit != "": 
    colorBar.ComponentTitle = '[' + Unit + ']' # 単位あり 
else: 
    colorBar.ComponentTitle = '' # 単位なし
    
# 最大値、最小値の表示
# colorBar.DrawDataRange = 1


# 
# ColorBarの方向（水平と垂直でサイズ感も変える）
# 
if makeBarOrientationHorizontal == True: 
    # 水平
    colorBar.WindowLocation = 'Lower Center'
    colorBar.AutoOrient = 0 # マニュアル
    colorBar.Orientation = 'Horizontal' # バー水平
    colorBar.HorizontalTitle = 1 # 文字列水平
    colorBar.TextPosition = 'Ticks right/top, annotations left/bottom' # テキスト位置を右や上
    colorBar.ScalarBarThickness = 24 #ColorBarの太さ
    colorBar.ScalarBarLength = 0.90 #ColorBarの長さ
    colorBar.TitleFontSize = 24 #タイトルフォントサイズ
    colorBar.LabelFontSize = 24 #ラベルフォントサイズ
else: 
     # 垂直
    colorBar.WindowLocation = 'Lower Right Corner'
    colorBar.AutoOrient = 0 # マニュアル
    colorBar.Orientation = 'Vertical' # バー垂直
    colorBar.HorizontalTitle = 0 # 文字列垂直
    colorBar.TextPosition = 'Ticks left/bottom, annotations right/top' # テキスト位置を左や下
    #colorBar.TextPosition = 'Ticks right/top, annotations left/bottom' # テキスト位置を右や上
    #colorBar.HorizontalTitle = 1 # タイトルを横書き
    colorBar.ScalarBarThickness = 36 #ColorBarの太さ
    colorBar.ScalarBarLength = 0.28 #ColorBarの長さ
    colorBar.TitleFontSize = 20 #タイトルフォントサイズ
    colorBar.LabelFontSize = 20 #ラベルフォントサイズ



#
# カメラ位置の調整
#

#renderView1.ResetActiveCameraToPositiveX()
#renderView1.ResetActiveCameraToNegativeX()
#renderView1.ResetActiveCameraToPositiveY()
#renderView1.ResetActiveCameraToNegativeY()
#renderView1.ResetActiveCameraToPositiveZ()
#renderView1.ResetActiveCameraToNegativeZ()
#renderView1.ApplyIsometricView()
#renderView1.AdjustRoll(-90.0)


#左内側面やや見上げるような視点
#renderView1.CameraPosition = [382.4574629734836, 2.1418897650197493, -105.43962831812819]
#renderView1.CameraViewUp = [0.3465715223268946, 0.005496338233884001, 0.938007446760439]


#
# ズームイン・アウト（X方向）
#
# CameraViewAngleについて
# * 呼び出す前にResetCamera()がないとダメ
# * 値↑ズームアウト、値↓ズームイン

renderView1.ResetCamera(True, 0.9) 

if Laterality == "L": 
    if View == "Lat": 
        # For Lat
        renderView1.CameraPosition = [-467, -18, 15.5]
        renderView1.CameraFocalPoint = [-34, -18, 15.5]
        renderView1.CameraViewUp = [0.0, 0.0, 1.0]
        #renderView1.CameraViewAngle = 24  # 拡大率？
        renderView1.CameraViewAngle = 23  # 拡大率？
        #renderView1.CameraViewAngle = 21  # 拡大率？
    else: 
        ## For Med (真横から)
        #renderView1.CameraPosition = [400, -18, 15.5]
        #renderView1.CameraFocalPoint = [-34, -18, 15.5]
        #renderView1.CameraViewUp = [0.0, 0.0, 1.0]
        #renderView1.CameraViewAngle = 19.5
        # For Med (少し見上げる)
        renderView1.CameraPosition = [373, -18, -133]
        renderView1.CameraFocalPoint = [-34, -18, 15.5]
        renderView1.CameraViewUp = [0.34, 0.0, 0.94]
        #renderView1.CameraViewAngle = 26  # 拡大率？
        renderView1.CameraViewAngle = 25  # 拡大率？
        #renderView1.CameraViewAngle = 23  # 拡大率？
        
elif Laterality == "R": 
    if View == "Lat": 
        # For Lat
        renderView1.CameraPosition = [470, -17, 15.5]
        renderView1.CameraFocalPoint = [-36, -17, 15.5]
        renderView1.CameraViewUp = [0.0, 0.0, 1.0]
        #renderView1.CameraViewAngle = 24  # 拡大率？
        renderView1.CameraViewAngle = 23  # 拡大率？
        #renderView1.CameraViewAngle = 21  # 拡大率？

    else: 
        # For Med (真横から)
        #renderView1.CameraPosition = [-399, -17, 15.5]
        #renderView1.CameraFocalPoint = [-35, -17, 15.5]
        #renderView1.CameraViewUp = [0.0, 0.0, 1.0]
        #renderView1.CameraViewAngle = 19.6
        # For Med (少し見上げる)
        renderView1.CameraPosition = [-394, -15, -58]
        renderView1.CameraFocalPoint = [33, -15, 17]
        renderView1.CameraViewUp = [-0.17, 0.0, 0.98]
        #renderView1.CameraViewAngle = 26  # 拡大率？
        renderView1.CameraViewAngle = 25  # 拡大率？
        #renderView1.CameraViewAngle = 23  # 拡大率？


#
# 光源
#
# 前から後ろの光
isFrontLightON = False
if isFrontLightON: 
    light1 = AddLight(view=renderView1)
    ShowInteractiveWidgets(proxy=light1)
    #light1.Radius = 10.0
    #light1.Intensity = 1.5
    light1.Position = [30, 0, 0]
    light1.FocalPoint = [20, 0, 0]

# 後ろから前の光
isBackLightON = False
if isBackLightON: 
    light2 = AddLight(view=renderView1)
    ShowInteractiveWidgets(proxy=light2)
    #light2.Radius = 10.0
    #light1.Intensity = 1.5
    light2.Position = [-30, 0, 0]
    light2.FocalPoint = [-20, 0, 0]


#
# Hide orientation axes
#
renderView1.OrientationAxesVisibility = 0



# Properties modified on renderView1
#renderView1.EnableRayTracing = 1 #影あり（滑らかさあり、ぼかし感あり）
renderView1.EnableRayTracing = 0 #影なし（滑らかさなし、ぼかし感なし）



import os
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



#================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
#================================================================

# get layout
layout1 = GetLayout()

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(938, 781)

#-----------------------------------
# saving camera placements for views

# current camera placement for renderView1
#renderView1.CameraPosition = [494.1295612982507, -17.5, 15.5]
#renderView1.CameraFocalPoint = [0.6165504455566406, -17.5, 15.5]
#renderView1.CameraViewUp = [0.0, 0.0, 1.0]
#renderView1.CameraParallelScale = 127.73056621456422


##--------------------------------------------
## You may need to add some code at the end of this python script depending on your usage, eg:
#
## Render all views to see them appears
RenderAllViews()
#
## Interact with the view, usefull when running from pvpython

if showPreview: 
    Interact()


#
## Save a screenshot of the active view



output_file_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME_PREFIX + "_" + ValueName.replace(" ", "") + "_" + Laterality + "_" + View + ".png"

SaveScreenshot(output_file_path)
print(output_file_path + " was generated.")

#
## Save a screenshot of a layout (multiple splitted view)
#SaveScreenshot("./png/screenshot_mul.png", GetLayout())

#
## Save all "Extractors" from the pipeline browser
# SaveExtracts()
#
## Save a animation of the current active view
# SaveAnimation()
#
## Please refer to the documentation of paraview.simple
## https://kitware.github.io/paraview-docs/latest/python/paraview.simple.html
##--------------------------------------------
