#!/usr/bin/env python

#import sys
#args = sys.argv
#print("arg1: " + args[1])

# ------------------------


import pandas as pd


# ------------------------


#
# Load VTK File Tbale
#
vtkfile_table_file = "./LabelTables/Label_File_Table.tsv"
df_file_table = pd.read_csv(vtkfile_table_file, header=None, names=['OBJECT_LABEL', 'VTK_FILE'], sep="\t")
#print(df_file_table)


# ------------------------


#
# Load Value Tbale
#
#value_table_file = "./ValueTables/DKSurf_DivergingValues_68.tsv"
#value_table_file = "./ValueTables/DKSurf_DivergingValues_L35.tsv"
value_table_file = "./ValueTables/ScRLV_DivergingValues_L7.tsv"
#value_table_file = "./ValueTables/DKSurf_QualitativeValues_68.tsv"
#value_table_file = "./ValueTables/DKSurf_SequentialValues_68.tsv"
#value_table_file = "./ValueTables/ScRLV_DivergingValues_16.tsv"
#value_table_file = "./ValueTables/ScRLV_QualitativeValues_16.tsv"
#value_table_file = "./ValueTables/ScRLV_SequentialValues_16.tsv"

df_value_table = pd.read_csv(value_table_file, header=None, names=['OBJECT_LABEL', 'VALUE'], sep="\t")
print(df_value_table)


# ------------------------


#
# Range Setting
#

# Sequential Values
# 0〜+100
# 0〜+1
# 0〜+X
#
# Diverging Values
# -1〜+1
# -100〜+100
# -X〜+X

# Qualitative Values
# 1, 2, 3, 4, ....
# 1, 3, 5, 7, .... 
# A, Y, Q, ...

isDiverging=True

isSequential=False

value_range_ul_on_table = 1
value_range_ll_on_table = -1

#value_range_ul_on_table = 1
#value_range_ll_on_table = 0

value_range_ul_on_vtkfile = 50
value_range_ll_on_vtkfile = -50

#vlue_range_ul_on_vtkfile = 1
#value_range_ll_on_vtkfile = -1

#value_range_ul_on_vtkfile = 100
#value_range_ll_on_vtkfile = 0


# ## Define Functions

# ------------------------


#
# Function for adding a value to the specified vtk file.
#
def infuseValueIntoAVtkFile(input_roi_vtk_file_path, output_destination, val_on_table, verbose):
    print("------------------------ addValueToAVtkFile() has been called ------------------------")
    
    print('input_roi_vtk_file_path: ' + input_roi_vtk_file_path)
    
    #
    # === Preparing output destinations ===
    #
    print('output_destination: ' + output_destination)
    
    import pathlib
    input_file_name = pathlib.Path(input_roi_vtk_file_path).name
    input_file_parent =  pathlib.Path(input_roi_vtk_file_path).parent
    ouput_file_path = "./" + str(pathlib.Path(output_destination)) + "/" +input_file_name
    output_file_parent = pathlib.Path(ouput_file_path).parent
    
    import os
    if not os.path.isfile(input_roi_vtk_file_path): 
        print("The input file does not exist. (do nothing)")
        return
    
    if output_file_parent == input_file_parent: 
        print("The parent of the specified output file is identical to the parent of the input file. Check arguments. (do nothing) ")
        return
    
    if verbose == True:
        print("input_file_name: " + input_file_name)
        print("ouput_file_path: " + ouput_file_path)
    
    output_folder=os.path.dirname(ouput_file_path)
    if  os.path.exists(output_folder): 
        print("    '" + output_folder + "' already exists.")
    else: 
        os.makedirs(output_folder, exist_ok=True)
        print("    '" + output_folder + "' was created.")
    

    # 
    # === Load A VTK File ===
    #
    input_file_path = input_roi_vtk_file_path

    f = open(input_file_path)
    lines = f.readlines() # 1行毎にファイル終端まで全て読む(改行文字も含まれる)
    f.close()
    
    # lines: リスト。要素は1行の文字列データ
    
    if verbose == True:
        for line in lines:
            print(line, end="")
        print()
    
    #
    # === Search the First Line of Data Field ===
    #
    start_line_num_of_data = 0
    for line_num in range(1, len(lines)): 
        if "NORMALS normals float\n" == lines[line_num]: 
            start_line_num_of_data = line_num + 1

    print( "The first line number of Data Field is "  + str(start_line_num_of_data) )

    if verbose == True:
        print("The first line of Data Filed: " + lines[start_line_num_of_data])
        print()
    
    #
    # === Add A Number to the Data Field ===
    #
    new_data_lines = [] 
    print("Now processing the line ", end="")
    for line_num in range( start_line_num_of_data, len(lines)): 
        print( str(line_num) + ". ", end="")
        line_editing = lines[line_num]
        line_editing = line_editing.rstrip('\n')
        values = line_editing.split(" ")
        #print(values)
        values.remove('')
        #print(values)
        values = [float(i) for i in values]
        #print(values)
        new_values = []
        
        #############################################
        

        
        
        if isDiverging: 
            scale_factor_1 = (value_range_ul_on_table - 0)
            scale_factor_2 = (value_range_ul_on_vtkfile - 0)
        
        if isSequential:
            scale_factor_1 = (value_range_ul_on_table - value_range_ll_on_table)
            scale_factor_2 = value_range_ul_on_vtkfile - value_range_ll_on_vtkfile
        
        for value in values: 
            new_value = ( value / (100/scale_factor_1) ) + ( (val_on_table/scale_factor_1) * scale_factor_2 )
            #new_value = value + ( (val_on_table/scale_factor_1) * scale_factor_2 )
            #new_value = ( value + (val_on_table/scale_factor_1)) * scale_factor_2
            #new_value = value + val_on_table * 100
            #new_values.append( value + val_on_table )
            #new_values.append( new_value ) # -100 〜 +100
            #new_values.append( new_value / 100 ) # -1 〜 +1
            new_values.append( new_value )

            
        #############################################
        
        new_values = [str(i) for i in new_values]
        #new_values = new_values.append(" ")
        #new_values = new_values.append("\n")
        new_values = ' '.join(new_values)
        new_values = new_values + " \n"
        #print(new_values)
        new_data_lines.append(new_values)
    print("...done.")
    
    if verbose == True:
        print("")
        print("new_data_lines: ")
        print(new_data_lines)
        print("")
    
    print()
    
    #
    # === Output As A New File ===
    #
    print("Start output...")
    new_lines = []
    new_lines.append('# vtk DataFile Version 4.0\n')
    for line_num in range(1, len(lines)): 
        #print(str(line_num) + ": ", end="")
        if line_num < start_line_num_of_data: 
            #print(lines[line_num])
            new_lines.append(lines[line_num])
        elif line_num >= start_line_num_of_data: 
            j = line_num - start_line_num_of_data
            #print(new_data_lines[j])
            new_lines.append(new_data_lines[j])
    print("")
    
    if verbose == True:
        print("new_lines: ")
        print(new_lines)
        print()
    
    
    with open(ouput_file_path, mode='w') as f:
        f.writelines(new_lines)
    
    print("'" + ouput_file_path + "' was generated. (Infused Value: " + str(val_on_table) + ")" )
    print("--------------------------------------------------------------------------------------")
    print()
    
            
#infuseValueIntoAVtkFile(
#    input_roi_vtk_file_path="./vtk/Lt_Brain_NonCortical/074_Left-Thalamus.vtk", 
#    output_destination="./vtk/Lt_Brain_NonCortical_with_Val", 
#    val_on_table=10, verbose=True)


# ------------------------


#df_value_file_table = pd.merge(df_file_table, df_value_table, on="OBJECT_LABEL", how="left") #file_tableにあるもの
df_value_file_table = pd.merge(df_file_table, df_value_table, on="OBJECT_LABEL", how="right") #value_tableにあるもの
#df_value_file_table = pd.merge(df_file_table, df_value_table, on="OBJECT_LABEL", how="outer") #両方にあるものを把握
df_value_file_table


# ------------------------


#
# 脳領域に値を流し込む
#
src_vtk_folder = "./vtk/without_val"
dest_vtk_folder = "./vtk/with_val"

import os
if os.path.isdir(dest_vtk_folder): 
    import shutil
    shutil.rmtree(dest_vtk_folder)
    os.mkdir(dest_vtk_folder)

for r in range(0, len(df_value_file_table)):
    #print(r)
    dest_vtk_file = df_value_file_table["VTK_FILE"][r]
    obj_val = df_value_file_table["VALUE"][r]
    print("Infuse " + str(obj_val) + " into " + dest_vtk_file)
    infuseValueIntoAVtkFile(
        input_roi_vtk_file_path=src_vtk_folder + "/" + dest_vtk_file, 
        output_destination=dest_vtk_folder, 
        val_on_table=obj_val, verbose=False)


# In[ ]:


#
# Join PNGs
#

