#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#MergePngHorizontally.py" data-toc-modified-id="MergePngHorizontally.py-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>MergePngHorizontally.py</a></span><ul class="toc-item"><li><span><a href="#MergePngVertically.py" data-toc-modified-id="MergePngVertically.py-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>MergePngVertically.py</a></span></li></ul></li></ul></div>

# ## MergePngHorizontally.py

# In[22]:


#
# MergePngHorizontally.py
#
from PIL import Image

def merge_four_images_horizontally(image_paths, output_path):
    # Open the images
    images = [Image.open(image_path) for image_path in image_paths]

    # Get the size of the first image
    width, height = images[0].size

    # Ensure all images have the same height
    if any(img.size[1] != height for img in images[1:]):
        raise ValueError("All images must have the same height for horizontal merging.")

    # Calculate the new width
    new_width = width * len(images)

    # Create a new image with the calculated size
    merged_image = Image.new("RGB", (new_width, height))

    # Paste each image side by side
    for i, img in enumerate(images):
        merged_image.paste(img, (i * width, 0))

    # Save the result
    merged_image.save(output_path)


#------------------------------
    
import configparser
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

# OUTPUT_FILE_NAME_PREFIX
value_table_file = config.get('Settings', 'value_table_file')
import pathlib
OUTPUT_FILE_NAME_PREFIX = pathlib.Path(value_table_file).stem
print("OUTPUT_FILE_NAME_PREFIX: " + OUTPUT_FILE_NAME_PREFIX)

# ValueName
ValueName = config.get('Settings', 'ValueName')
ValueName = ValueName.replace("\"", "").replace("\'", "")
print("ValueName: " + ValueName)

# OUTPUT_FOLDER
OUTPUT_FOLDER = config.get('Settings', 'output_folder')
OUTPUT_FOLDER = OUTPUT_FOLDER.replace("\"", "").replace("\'", "")
print("OUTPUT_FOLDER: " + OUTPUT_FOLDER)

#
# OUTPUT_FILE_NAME
#
OUTPUT_FILE_NAME = OUTPUT_FILE_NAME_PREFIX + "_" + ValueName.replace(" ", "") + ".png"

#
# Construct PNG File Path Array
#
source_png_files = []

laterality = "R"
view = "Lat"
output_file_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME_PREFIX + "_" + ValueName.replace(" ", "") + "_" + laterality + "_" + view + ".png"
source_png_files.append(output_file_path)
view = "Med"
output_file_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME_PREFIX + "_" + ValueName.replace(" ", "") + "_" + laterality + "_" + view + ".png"
source_png_files.append(output_file_path)

laterality = "L"
view = "Med"
output_file_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME_PREFIX + "_" + ValueName.replace(" ", "") + "_" + laterality + "_" + view + ".png"
source_png_files.append(output_file_path)
view = "Lat"
output_file_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME_PREFIX + "_" + ValueName.replace(" ", "") + "_" + laterality + "_" + view + ".png"
source_png_files.append(output_file_path)

print(source_png_files)


#------------------------------

output_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME
merge_four_images_horizontally(source_png_files, output_path)


# ------
