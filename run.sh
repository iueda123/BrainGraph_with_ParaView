#!/bin/bash


python ./Infuse_Values_into_VTK_Files.py

#
# Vertical Summarization
#

# arg 1: Laterality. "R" or "L".
# arg 2: View. "Lat" or "Med".
# arg 3: Orientation of ColorBar. "vertical" "horizontal", or "none".
# art 4: showPreview. "true" or "false". 
pvpython PvpythonScript_Make_Figure.py R Lat none false
pvpython PvpythonScript_Make_Figure.py R Med none false
pvpython PvpythonScript_Make_Figure.py L Med none false
pvpython PvpythonScript_Make_Figure.py L Lat horizontal false

python ./MergePngVertically.py


#
# Hrizontal Summarization
#

## arg 1: Laterality. "R" or "L".
## arg 2: View. "Lat" or "Med".
## arg 3: Orientation of ColorBar. "vertical" "horizontal", or "none".
## art 4: showPreview. "true" or "false". 
#pvpython PvpythonScript_Make_Figure.py R Lat none false
#pvpython PvpythonScript_Make_Figure.py R Med none false
#pvpython PvpythonScript_Make_Figure.py L Med none false
#pvpython PvpythonScript_Make_Figure.py L Lat vertical false

#python ./MergePngHorizontally.py
