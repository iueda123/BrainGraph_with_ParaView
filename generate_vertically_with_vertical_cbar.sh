#!/bin/bash

function usage() {
    echo ""
    echo "=================================================================="
    echo ""
    echo "${0}"
    echo ""
    echo "version: 20250527"
    echo ""
    echo "USAGE:"
    echo "    ${0} "
#    echo "        --direction=<h or v> "
    echo "        [--development]"
    echo "        [--verbose]"
    echo ""
    echo "DESCRIPTION: "
    echo "    This code is for generating brain graphs. "
    echo ""
#    echo "    The 'direction' option should be followed by 'h' or 'v'."
#    echo ""
    echo "    The 'development' option should be specified when you want to develop."
    echo ""
    echo "    The 'verbose' option should be specified when you want to show "
    echo "    debug messages."
    echo ""
    echo "NOTE:"
    echo ""
    echo "Flow Overview"
    echo ""
    echo "  generate_horizontally.sh or generate_vertically.sh"
    echo "   ↓"
    echo "  Infuse_Values_into_VTK_Files.py"
    echo "   ↓"
    echo "  PypythonScript_Make_Figure.py"
    echo "   ↓"
    echo "  MergePngHorizontally.py or MergePngVertically.py"
    echo ""
    echo ""
    echo "=================================================================="
    echo ""
    exit
}

function get_batch_options() {
    local arguments=("$@")

    unset HELP
    unset DIRECTION
    unset DEVELOPMENT
    unset VERBOSE

    local index=0
    local numArgs=${#arguments[@]}
    echo "The number of arguments: ${numArgs}"
    local argument

    while [ ${index} -lt ${numArgs} ]; do
        argument=${arguments[index]}

        echo "\${argument}: ${argument}"

        case ${argument} in
            --help | -h)
                HELP="TRUE"
                index=$(( index + 1 ))
                ;;
            #--direction=*)
            #    DIRECTION=${argument#*=}
            #    index=$(( index + 1 ))
               # ;;
            --development | --d)
                DEVELOPMENT=true
                index=$(( index + 1 ))
                ;;
            --verbose | --v)
                VERBOSE=true
                index=$(( index + 1 ))
                ;;
             *)
                  echo ""
                  echo "ERROR: Unrecognized Option: ${argument}"
                  echo ""
                  exit 1
                  ;;
        esac
    done
}

get_batch_options "$@"

echo ""
if [ ! -z ${VERBOSE} ]; then echo "\${HELP}=${HELP}"; fi
#if [ ! -z ${VERBOSE} ]; then echo "\${DIRECTION}=${DIRECTION}"; fi
if [ ! -z ${VERBOSE} ]; then echo "\${DEVELOPMENT}=${DEVELOPMENT}"; fi
if [ ! -z ${VERBOSE} ]; then echo "\${VERBOSE}=${VERBOSE}"; fi
echo ""

if [ ! -z ${HELP} ]; then
         usage
         exit 1
fi

#if [ -z ${DIRECTION} ]; then
#         echo "\${DIRECTION} is empty."
#         echo "Please specify '--direction' argument."
#         usage
#         exit 1
#fi

if [ -z ${DEVELOPMENT} ]; then
         echo "\${DEVELOPMENT} is empty."
         DEVELOPMENT=false
fi

if [ -z ${VERBOSE} ]; then
         echo "\${VERBOSE} is empty."
         VERBOSE=false
fi

##########################################
# The start of the main routine. #
##########################################

where_this_script_exist=`dirname ${0}`

echo ""
echo "Infuse_Values_into_VTK_Files"
echo ""
if [[ ${DEVELOPMENT} == true ]]; then
    echo ""
    echo "This is the development mode..."
    echo "" 
    trgt=./Infuse_Values_into_VTK_Files.ipynb
    /home/$USER/.pyenv/shims/jupyter nbconvert --to script ${trgt} --output ${trgt%.ipynb}
fi

python ${where_this_script_exist}/Infuse_Values_into_VTK_Files.py
return_code=$? # pythonスクリプト戻り値を取得

if [[ ${DEVELOPMENT} == true ]]; then
    #rm ./Infuse_Values_into_VTK_Files.py
    echo ""
fi

if [ ! $return_code -eq 0 ]; then
    echo "Python script failed with return code $return_code."
    exit 1
fi


echo ""
echo "Call pypython"
echo ""
# arg 1: Laterality. "R" or "L".
# arg 2: View. "Lat" or "Med".
# arg 3: Orientation of ColorBar. "vertical" "horizontal", or "none".
# art 4: showPreview. "true" or "false". 
pvpython ${where_this_script_exist}/PvpythonScript_Make_Figure.py R Lat none false
pvpython ${where_this_script_exist}/PvpythonScript_Make_Figure.py R Med none false
pvpython ${where_this_script_exist}/PvpythonScript_Make_Figure.py L Med none false
pvpython ${where_this_script_exist}/PvpythonScript_Make_Figure.py L Lat horizontal false



echo ""
echo "MergePngVertically"
echo ""
if [[ ${DEVELOPMENT} == true ]]; then
    trgt=./MergePngVertically.ipynb
    /home/$USER/.pyenv/shims/jupyter nbconvert --to script ${trgt} --output ${trgt%.ipynb}
fi

python ${where_this_script_exist}/MergePngVertically.py

if [[ ${DEVELOPMENT} == true ]]; then
    echo ""
    #rm ./MergePngVertically.py
fi



###########################
# The end of this script. #
###########################
echo ""
echo "The processing was finished."
echo ""

 
#GenerateBrainGraph \
#    --direction=h \
#    --development \
#    --verbose
