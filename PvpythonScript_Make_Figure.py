#PvpythonScript


#import sys
#args = sys.argv
#print("arg1: " + args[1])

# --------------------------------------------------------------

Laterality = "L"
#Laterality = "R"

#View = "Med"
View = "Lat"

UL_on_Fig = +50
LL_on_Fig = -50

#LUT = 'Fast'
#LUT = 'Cool to Warm'
#LUT = 'Black-Body Radiation'
#LUT = 'Inferno (matplotlib)'
#LUT = 'Blue Orange (divergent)'
LUT = 'Cold and Hot'
#LUT = 'Rainbow Desaturated'
#LUT = 'Rainbow Uniform'
#LUT = 'Turbo'
#LUT = 'Cool to Warm (Extended)'
#LUT = 'X Ray'
#LUT = 'Black, Blue and White'
#LUT = 'Viridis (matplotlib)'
#LUT = 'Linear Green (Gr4L)'
#LUT = 'Blue - Green - Orange'
#LUT = 'Yellow - Gray - Blue'

SPECULAR = 1.0 # 輝き

ValueName = "Sample Value"
Unit = "Point"


#displayColorBarAndLegendOnlyOnRtLat = False
displayColorBarAndLegend = True

makeBarOrientationHorizontal = False

showPreview = True

# --------------------------------------------------------------

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


# 値なしVTKファイルをロード
Folder_Roi_without_Val = "./vtk/without_val"
ribbonvtk = None
if Laterality == "L": 
    ribbonvtk = LegacyVTKReader(registrationName='Lt_ribbon.vtk', FileNames=[Folder_Roi_without_Val + '/Lt_ribbon.vtk'])
elif Laterality == "R": 
    ribbonvtk = LegacyVTKReader(registrationName='Rt_ribbon.vtk', FileNames=[Folder_Roi_without_Val + '/Rt_ribbon.vtk'])


# 値ありVTKファイルをロードして生成したオブジェクトを配列に格納 

Folder_Roi_with_Val = "./vtk/with_val"


import os

def get_file_names_with_extension(folder_path, target_extension):
    file_names = []
    for filename in os.listdir(folder_path):
        if filename.endswith(target_extension):
            file_names.append(filename)
    return file_names

vtk_file_names = get_file_names_with_extension(Folder_Roi_with_Val, ".vtk")



Regions_with_Val = []
for vtk_file_name in vtk_file_names:
    Regions_with_Val.append( LegacyVTKReader(registrationName=vtk_file_name, FileNames=[Folder_Roi_with_Val + '/' + vtk_file_name]) )



# set active source
SetActiveSource(ribbonvtk)

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view
ribbonvtkDisplay = Show(ribbonvtk, renderView1, 'GeometryRepresentation')

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



#
# 透明度の調整
#
# Properties modified on rt_ribbonvtkDisplay
ribbonvtkDisplay.Opacity = 0.05
#rt_ribbonvtkDisplay.Opacity = 0.05




normalsLUTColorBar = None


for REGION in Regions_with_Val: 

    # set active source
    SetActiveSource(REGION)

    # show data in view
    REGION = Show(REGION, renderView1, 'GeometryRepresentation')

    # trace defaults for the display properties.
    #REGION.Representation = 'Surface'

    # set scalar coloring
    ColorBy(REGION, ('POINTS', 'normals', 'X'))

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

renderView1.ResetActiveCameraToPositiveX()
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
        renderView1.CameraViewAngle = 24  # 拡大率？
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
        renderView1.CameraViewAngle = 26  # 拡大率？
        
elif Laterality == "R": 
    if View == "Lat": 
        # For Lat
        renderView1.CameraPosition = [470, -17, 15.5]
        renderView1.CameraFocalPoint = [-36, -17, 15.5]
        renderView1.CameraViewUp = [0.0, 0.0, 1.0]
        renderView1.CameraViewAngle = 24  # 拡大率？

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
        renderView1.CameraViewAngle = 26  # 拡大率？


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
os.makedirs("./png", exist_ok=True)



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
Interact()
#
## Save a screenshot of the active view

SaveScreenshot("./png/" + ValueName.replace(" ", "_") + "_" + Laterality + "_" + View + ".png")

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
