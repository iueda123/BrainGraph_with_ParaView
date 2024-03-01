#
# MergePngVertically
#
from PIL import Image

def merge_four_images_vertically(image_paths, output_path):
    # Open the images
    images = [Image.open(image_path) for image_path in image_paths]

    # Get the size of the first image
    width, height = images[0].size

    # Ensure all images have the same width
    if any(img.size[0] != width for img in images[1:]):
        raise ValueError("All images must have the same width for vertical merging.")

    # Calculate the new height
    new_height = height * len(images)

    # Create a new image with the calculated size
    merged_image = Image.new("RGB", (width, new_height))

    # Paste each image one below the other
    for i, img in enumerate(images):
        merged_image.paste(img, (0, i * height))

    # Save the result
    merged_image.save(output_path)

#-----------------------------

import configparser
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

# OUTPUT_FILE_NAME_PREFIX
value_table_file = config.get('Value', 'value_table_file')
import pathlib
OUTPUT_FILE_NAME_PREFIX = pathlib.Path(value_table_file).stem
print("OUTPUT_FILE_NAME_PREFIX: " + OUTPUT_FILE_NAME_PREFIX)

# ValueName
ValueName = config.get('Figure', 'ValueName')
ValueName = ValueName.replace("\"", "").replace("\'", "")
print("ValueName: " + ValueName)

# OUTPUT_FOLDER
OUTPUT_FOLDER = config.get('Figure', 'output_folder')
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

#--------------------------------

output_path = OUTPUT_FOLDER + "/" + OUTPUT_FILE_NAME
merge_four_images_vertically(source_png_files, output_path)

