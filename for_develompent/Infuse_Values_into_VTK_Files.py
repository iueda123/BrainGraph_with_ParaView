#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Load-Settings" data-toc-modified-id="Load-Settings-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Load Settings</a></span></li><li><span><a href="#Load-Tables" data-toc-modified-id="Load-Tables-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Load Tables</a></span></li><li><span><a href="#Define-Functions" data-toc-modified-id="Define-Functions-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Define Functions</a></span></li></ul></div>

# In[4]:


# 2024.12.18 引用符のありなしでtsv読込に失敗するのでCustomConfigParserを導入


# ## Load Settings

# In[5]:


import configparser

# 引用符の扱いがtsvの読込を邪魔をするのでCustomConfigParserを用意
class CustomConfigParser(configparser.ConfigParser):
    def get(self, section, option, **kwargs):
        value = super().get(section, option, **kwargs)
        # 先頭と末尾の引用符を削除（必要に応じて追加）
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value

# ConfigParserオブジェクトを作成
config = CustomConfigParser()
# ファイルを読み込む
config.read('./config.ini', encoding='utf-8')

# セクションとオプションから値を取得
value_name = config.get('Settings', 'ValueName')
value_table_file = config.get('Settings', 'value_table_file')
output_folder = config.get('Settings', 'output_folder')
#value_type = config.get('ForDebug', 'value_type')
value_range_ul_on_figure = float( config.get('Settings', 'value_range_ul_on_figure') )
value_range_ll_on_figure = float( config.get('Settings', 'value_range_ll_on_figure') )
if value_range_ul_on_figure < value_range_ll_on_figure: 
    tmp = value_range_ll_on_figure
    value_range_ll_on_figure = value_range_ul_on_figure
    value_range_ul_on_figure = tmp

print("ValueName: " + value_name)
print("value_table_file: " + value_table_file)
print("output_folder: " + output_folder)
#print("value_type: " + value_type)
print("value_range_ul_on_figure: " + str(value_range_ul_on_figure))
print("value_range_ll_on_figure: " + str(value_range_ll_on_figure))


# In[ ]:


import os
import sys

file_path = value_table_file  # 確認したいファイルのパス

# ファイルの存在を確認
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' does not exist.")
    sys.exit(1)  # スクリプトを終了 (終了コード1を返す)

print(f"File '{file_path}' exists. Continuing script...")


# ## Load Tables

# In[5]:


import pandas as pd


# In[17]:


#
# Load "OBJECT_LABEL-VALUE" Tbale
#
#    OBJECT_LABEL: VtkfileTableと橋渡しするためのラベル
#    VALUE: 各オブジェクトに与えたい値
#



df_value_table = pd.read_csv(value_table_file, header=None, names=['OBJECT_LABEL', 'VALUE'], sep="\t")
print(df_value_table)


# In[4]:


#
# Load "OBJECT_LABEL-VTKFILE" Table (VtkfileTable.tsv)。
# VtkfileTable.tsv は "OBJECT_LABEL" と ”VTK_FILE” の対応関係を記している表を格納している。
#
#     OBJECT_LABEL: ValueTableと橋渡しするためのラベル
#     VTK_FILE: ./vtk/without_val 下に存在するファイル
#
vtkfile_table_file = "./VtkfileTable.tsv"
df_file_table = pd.read_csv(vtkfile_table_file, header=0, names=['OBJECT_LABEL', 'VTK_FILE'], sep="\t")
print(df_file_table)


# ## Define Functions

# In[5]:


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
    infused_values = []
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
        # Sequential Values
        # e.g.: 0〜+100; 0〜+1; 0〜+X
        #
        # Diverging Values
        # e.g.: -1〜+1; -100〜+100; -X〜+X

        # Qualitative Values
        # e.g.: 1, 2, 3, 4, ...; 1, 3, 5, 7, ...; A, Y, Q, ...
        if value_range_ul_on_figure > 0 and value_range_ll_on_figure < 0:
            value_type = "DIVERGING"
        else:
            value_type = "SEQUENTIAL"
        
        if value_type == "DIVERGING": 
            base_range_on_figure = value_range_ul_on_figure - 0
            fluctuation_factor = base_range_on_figure / 5
            for value in values: 
                new_value =  val_on_table + value * fluctuation_factor
                new_values.append( new_value )
        elif value_type == "SEQUENTIAL": 
            base_range_on_figure = (value_range_ul_on_figure - value_range_ll_on_figure)
            fluctuation_factor = base_range_on_figure / 5
            for value in values: 
                new_value =  val_on_table  + ( value * fluctuation_factor)
                new_values.append( new_value )
        elif value_type == "QUALITAIVE": 
            print("Error. Not yet coded.")
            import sys; sys.exit()
        else: 
            print("Error. Please check 'value_type'.")
            import sys; sys.exit()
        
        #
        # For Infused Value Check
        #
        #print(new_values)
        #if len(new_values) > 1:
        #    import statistics
        #    print(str(statistics.mean(new_values)) + "±" + (str(statistics.stdev(new_values))) )
        for new_value in new_values: 
            infused_values.append(new_value)
            
        #############################################
        
        new_values_str = [str(i) for i in new_values]
        #new_values_str = new_values_str.append(" ")
        #new_values_str = new_values_str.append("\n")
        new_values_str = ' '.join(new_values_str)
        new_values_str = new_values_str + " \n"
        #print(new_values_str)
        new_data_lines.append(new_values_str)
        

        
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
    
    
    import statistics
    infused_value_stats = str(statistics.mean(infused_values)) + "±" + (str(statistics.stdev(infused_values)))
    
    
    print("'" + ouput_file_path + "' was generated. (Infused Value: " + infused_value_stats + ")" )
    print("--------------------------------------------------------------------------------------")
    print()
    
            
#infuseValueIntoAVtkFile(
#    input_roi_vtk_file_path="./vtk/Lt_Brain_NonCortical/074_Left-Thalamus.vtk", 
#    output_destination="./vtk/Lt_Brain_NonCortical_with_Val", 
#    val_on_table=10, verbose=True)


# In[6]:


#df_value_file_table = pd.merge(df_file_table, df_value_table, on="OBJECT_LABEL", how="left") #file_tableにあるもの
df_value_file_table = pd.merge(df_file_table, df_value_table, on="OBJECT_LABEL", how="right") #value_tableにあるもの
#df_value_file_table = pd.merge(df_file_table, df_value_table, on="OBJECT_LABEL", how="outer") #両方にあるものを把握
df_value_file_table


# In[7]:


#
# Infuse Values into Vtk Files
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

