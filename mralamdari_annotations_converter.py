import os
import cv2
import shutil
import numpy as np
from tqdm import tqdm

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
    coords[-4] = x/w
    coords[-3] = y/h
    coords[-2] = width/w
    coords[-1] = height/h
    os.chdir("Label")
    return coords

classes = {}
ROOT_DIR = os.getcwd()
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
        for CLASS_ID, CLASS_DIR in enumerate(CLASS_DIRS):
            cls_dir = CLASS_DIR.replace('_', ' ')
            classes[cls_dir] = str(CLASS_ID)
            if os.path.isdir(CLASS_DIR):
                os.chdir(CLASS_DIR)
                print(f"Converting annotations for class: {CLASS_DIR}")
                
                # Step into Label folder where annotations are generated
                os.chdir("Label")

                for filename in tqdm(os.listdir(os.getcwd())):
                    if filename.endswith(".txt"):
                        filename_str = filename[:-4]
                        annotations = []
                        with open(filename) as f:
                            for line in f:
                                labels = line.split()
                                coords = np.asarray([float(labels[-4]), float(labels[-3]), float(labels[-2]), float(labels[-1])])
                                coords = convert(filename_str, coords)
                                class_index = classes.get(' '.join(labels[:-4]))
                                
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
                #Remove Label after getting out of it.
                shutil.rmtree(os.path.join(os.getcwd(), "Label"))
                os.chdir("..")
        os.chdir("..")
	

    dir_path = os.path.dirname(ROOT_DIR)
    data_path = os.path.join(dir_path, "data")
    obj_path = os.path.join(data_path, "obj")
    images_path = os.path.join(ROOT_DIR,"OID", "Dataset", DIR)
    #make darknet/data/ directory if it doesn't exists already
    os.makedirs(data_path, exist_ok=True)

    #make darknet/data/obj directory if it doesn't exists already
    os.makedirs(obj_path, exist_ok=True)


    #Create obj.names in darknet/data/ 
    with open(f'{data_path}\obj.names', 'w+') as cls_text:
        for cls_name in classes:
            cls_text.write(f'{cls_name}\n')

    #Move Train/Test folder to darknet/data/obj/{train/test}
    target_images_path = os.path.join(obj_path, DIR)
    os.rename(images_path, target_images_path)

    #Create train.txt And/Or test.txt in darknet/data/ 
    with open(f'{data_path}\{DIR}.txt', 'w+') as data_file:
        for cls_name in classes:
            image_folder_path = os.path.join(target_images_path, cls_name)
            for image_file in os.listdir(image_folder_path):
                if image_file.endswith('.jpg'):
                    data_file.write(f'{os.path.join(image_folder_path, image_file)}\n')
    data_file.close()
