#!/bin/bash

python ./20240125_Infuse_Values_into_VTK_Files.py
pvpython PvpythonScript_Make_Figure.py R Lat False
pvpython PvpythonScript_Make_Figure.py R Med False
pvpython PvpythonScript_Make_Figure.py L Med False
pvpython PvpythonScript_Make_Figure.py L Lat True

