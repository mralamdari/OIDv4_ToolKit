import os
import cv2
import numpy as np
from tqdm import tqdm
import argparse
import fileinput

# function that turns XMin, YMin, XMax, YMax coordinates to normalized yolo format
def convert(filename_str, coords):
    os.chdir("..")
    image = cv2.imread(filename_str + ".jpg")
    x_min, y_min, x_max, y_max = coords[:4]
    width = x_max - x_min
    height= y_max - y_min
    x = x_min + (width/2)
    y = y_min + (height/2)
    h, w = image.shape[:-1]   #Height, Width, 3
    coords[-4] = round(x/w, 4)
    coords[-3] = round(y/h, 4)
    coords[-2] = round(width/w, 4)
    coords[-1] = round(height/h, 4)
    os.chdir("Label")
    return coords

ROOT_DIR = os.getcwd()

# create dict to map class names to numbers for yolo
classes = {}
with open("classes.txt", "r") as myFile:
    for num, line in enumerate(myFile, 0):
        line = line.rstrip("\n")
        classes[line] = str(num)
    myFile.close()
# step into dataset directory
os.chdir(os.path.join("OID", "Dataset"))
DIRS = os.listdir(os.getcwd())

# for all train, validation and test folders
for DIR in DIRS:
    if os.path.isdir(DIR):
        os.chdir(DIR)
        print(f"Currently in subdirectory: {DIR}")
        
        CLASS_DIRS = os.listdir(os.getcwd())
        # for all class folders step into directory to change annotations
        for CLASS_DIR in CLASS_DIRS:
            if os.path.isdir(CLASS_DIR):
                os.chdir(CLASS_DIR)
                print(f"Converting annotations for class: {CLASS_DIR}")
                
                # Step into Label folder where annotations are generated
                os.chdir("Label")

                for filename in tqdm(os.listdir(os.getcwd())):
                    filename_str = str.split(filename, ".")[0]
                    if filename.endswith(".txt"):
                        annotations = []
                        with open(filename) as f:
                            for line in f:
                                labels = line.split()
                                coords = np.asarray([float(labels[-4]), float(labels[-3]), float(labels[-2]), float(labels[-1])])
                                coords = convert(filename_str, coords)
                                class_index = class_dic.get(' '.join(labels[:-4]))
                                newline = f'{class_index} {coords[0]} {coords[1]} {coords[2]} {coords[3]}'
                                line = line.replace(line, newline)
                                annotations.append(line)
                            f.close()
                        os.chdir("..")
                        with open(filename, "w") as outfile:
                            for line in annotations:
                                outfile.write(line)
                                outfile.write("\n")
                            outfile.close()
                        os.chdir("Label")
                os.chdir("..")
                os.chdir("..")
        os.chdir("..")
