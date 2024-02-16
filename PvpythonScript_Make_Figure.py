# PvpythonScript

#
# ver 20240127
# 
# arg1: Laterality. L or R.
# arg2: View. Med or Lat.
# arg3: displayColorBarAndLegend. True or False.
#
#

# 
# --------------------------------------------------------------

# Main Settings from args
#
# arg 1: Laterality. "R" or "L".
# arg 2: View. "Lat" or "Med".
# arg 3: Orientation of ColorBar. "vertical" "horizontal", or "none".
# art 4: showPreview. "true" or "false". 

import sys
args = sys.argv
#print(len(args))
if len(args) == 5:
    
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

    # showPreview
    if args[4].lower() == "true": 
        showPreview = True
    else: 
        showPreview = False
        
else: 
    Laterality = "L"
    View = "Lat"
    displayColorBarAndLegend = True
    makeBarOrientationHorizontal = True   
    showPreview = True

print("Laterality: " + Laterality)
print("View: " + View)
print("displayColorBarAndLegend: " + str(displayColorBarAndLegend))
print("makeBarOrientationHorizontal: " + str(makeBarOrientationHorizontal) )
print("showPreview: " + str(showPreview))

# --------------------------------------------------------------
#
# Other Settings from config.ini
# 
#

import configparser
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

# UL_on_Fig, LL_on_Fig
UL_on_Fig = float( config.get('Figure', 'value_range_ul_on_figure') )
LL_on_Fig = float( config.get('Figure', 'value_range_ll_on_figure') )
if UL_on_Fig < LL_on_Fig: 
    tmp = LL_on_Fig
    LL_on_Fig = UL_on_Fig
    UL_on_Fig = tmp
print("UL_on_Fig: " + str(UL_on_Fig))
print("LL_on_Fig: " + str(LL_on_Fig))

# LUT
LUT = config.get('Figure', 'LUT')
LUT = LUT.replace("\"", "").replace("\'", "")
print("LUT: " + LUT)

# ValueName
ValueName = config.get('Figure', 'ValueName')
ValueName = ValueName.replace("\"", "").replace("\'", "")
print("ValueName: " + ValueName)

# Unit
Unit = config.get('Figure', 'Unit')
Unit = Unit.replace("\"", "").replace("\'", "")
print("Unit: " + Unit)


# SPECULAR
SPECULAR = float( config.get('Figure', 'SPECULAR') )
print("SPECULAR: " + str(SPECULAR))

# OUTPUT_FOLDER
OUTPUT_FOLDER = config.get('Figure', 'output_folder')
OUTPUT_FOLDER = OUTPUT_FOLDER.replace("\"", "").replace("\'", "")
print("OUTPUT_FOLDER: " + OUTPUT_FOLDER)

# OUTPUT_FILE_NAME_PREFIX
value_table_file = config.get('Value', 'value_table_file')
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


load_taraget_vtk_file_names = get_SurfaceAreaVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード
load_taraget_vtk_file_names = load_taraget_vtk_file_names  +  get_SubcorticalAreaVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード
load_taraget_vtk_file_names = load_taraget_vtk_file_names  +  get_CCVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード
load_taraget_vtk_file_names = load_taraget_vtk_file_names  +  get_LatVentVtkFileNames(Folder_Roi_with_Val, Laterality) # 片脳のみロード


# Load Target VTK Files
Regions_with_Val = []
for vtk_file_name in load_taraget_vtk_file_names:
    Regions_with_Val.append( LegacyVTKReader(registrationName=vtk_file_name, FileNames=[Folder_Roi_with_Val + '/' + vtk_file_name]) )



#
# 値なしVTKファイルをロード
#
Folder_Roi_without_Val = "./vtk/without_val"

ribbonvtk = None
empty_ccvtk = None
hippo_vtk = None
amygdala_vtk = None

shouldLoadEmptyCC = None
if( len(get_SurfaceAreaVtkFileNames(Folder_Roi_with_Val, Laterality)) > 0 ): 
    shouldLoadEmptyCC = True
else: 
    shouldLoadEmptyCC = False

if Laterality == "L": 
    ribbonvtk = LegacyVTKReader(registrationName='Lt_ribbon.vtk', FileNames=[Folder_Roi_without_Val + '/Lt_ribbon.vtk'])
    if shouldLoadEmptyCC: 
        empty_ccvtk = LegacyVTKReader(registrationName='Lt_Empty_CC.vtk', FileNames=[Folder_Roi_without_Val + '/Lt_Empty_CC.vtk'])
        hippo_vtk = LegacyVTKReader(registrationName='086_Left-Hippocampus.vtk', FileNames=[Folder_Roi_without_Val + '/078_Left-Hippocampus.vtk'])
        amygdala_vtk = LegacyVTKReader(registrationName='079_Left-Amygdala.vtk.vtk', FileNames=[Folder_Roi_without_Val + '/079_Left-Amygdala.vtk'])
elif Laterality == "R": 
    ribbonvtk = LegacyVTKReader(registrationName='Rt_ribbon.vtk', FileNames=[Folder_Roi_without_Val + '/Rt_ribbon.vtk'])
    if shouldLoadEmptyCC: 
        empty_ccvtk = LegacyVTKReader(registrationName='Rt_Empty_CC.vtk', FileNames=[Folder_Roi_without_Val + '/Rt_Empty_CC.vtk'])
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
    
    #
    # 輝き度合い
    #
    REGION.Specular = SPECULAR
    
    #
    # ワイヤーフレーム化
    #
    REGION.SetRepresentationType('Wireframe')
    REGION.RenderLinesAsTubes = 1
    REGION.LineWidth = 3.0
    
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
renderView1.Background = [0.9372549019607843, 0.9372549019607843, 0.9372549019607843]


#
# Color Bar and Legend の調整
#

# 文字を黒化
normalsLUTColorBar.TitleColor = [0.0, 0.0, 0.0]
normalsLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

# 文字を入れる
normalsLUTColorBar.Title = ValueName # タイトル
normalsLUTColorBar.ComponentTitle = '[' + Unit + ']' # 単位 
    
# 最大値、最小値の表示
# normalsLUTColorBar.DrawDataRange = 1


# 
# バーの方向
# 
if makeBarOrientationHorizontal == True: 
    # 水平
    normalsLUTColorBar.WindowLocation = 'Lower Center'
    normalsLUTColorBar.AutoOrient = 0 # マニュアル
    normalsLUTColorBar.Orientation = 'Horizontal' # バー水平
    normalsLUTColorBar.HorizontalTitle = 1 # 文字列水平
    normalsLUTColorBar.TextPosition = 'Ticks right/top, annotations left/bottom' # テキスト位置を右や上
else: 
     # 垂直
    normalsLUTColorBar.WindowLocation = 'Lower Right Corner'
    normalsLUTColorBar.AutoOrient = 0 # マニュアル
    normalsLUTColorBar.Orientation = 'Vertical' # バー垂直
    normalsLUTColorBar.HorizontalTitle = 0 # 文字列垂直
    normalsLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top' # テキスト位置を左や下


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
        renderView1.CameraViewAngle = 21  # 拡大率？
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
        renderView1.CameraViewAngle = 23  # 拡大率？
        
elif Laterality == "R": 
    if View == "Lat": 
        # For Lat
        renderView1.CameraPosition = [470, -17, 15.5]
        renderView1.CameraFocalPoint = [-36, -17, 15.5]
        renderView1.CameraViewUp = [0.0, 0.0, 1.0]
        #renderView1.CameraViewAngle = 24  # 拡大率？
        renderView1.CameraViewAngle = 21  # 拡大率？

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
        renderView1.CameraViewAngle = 23  # 拡大率？


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
