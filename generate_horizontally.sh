#!/bin/bash

where_this_script_exist=`dirname ${0}`

#
# Hrizontal Summarization
#
#
#  generate_horizontally.sh
#    Infuse_Values_into_VTK_Files.py
#    PypythonScript_Make_Figure.py
#    MergePngHorizontally.py
#
#

# Infuse_Values_into_VTK_Files
trgt=./Infuse_Values_into_VTK_Files.ipynb
jupyter nbconvert --to script ${trgt} --output ${trgt%.ipynb}
python ./Infuse_Values_into_VTK_Files.py

return_code=$? # pythonスクリプト戻り値を取得

rm ./Infuse_Values_into_VTK_Files.py

if [ ! $return_code -eq 0 ]; then
    echo "Python script failed with return code $return_code."
    exit 1
fi

# arg 1: Laterality. "R" or "L".
# arg 2: View. "Lat" or "Med".
# arg 3: Orientation of ColorBar. "vertical" "horizontal", or "none".
# art 4: showPreview. "true" or "false". 
pvpython ./PvpythonScript_Make_Figure.py R Lat none false
pvpython ./PvpythonScript_Make_Figure.py R Med none false
pvpython ./PvpythonScript_Make_Figure.py L Med none false
pvpython ./PvpythonScript_Make_Figure.py L Lat vertical false


# MergePngHorizontally
trgt=./MergePngHorizontally.ipynb
jupyter nbconvert --to script ${trgt} --output ${trgt%.ipynb}
python ./MergePngHorizontally.py
rm ./MergePngHorizontally.py
