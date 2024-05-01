# coding=UTF-8
import os
import glob
import random
import logging
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Get all subfolders in a specified directory
def get_subfolders(path):
    """Retrieve subdirectories for a path."""
    subfolders = [os.path.join(path, o) for o in os.listdir(path)
                  if os.path.isdir(os.path.join(path, o))]
    return subfolders

# Delete non-image files in all subfolders of the specified directory
def delete_non_image_files(subfolder):
    """Delete files in subfolder that are not images."""
    allowed_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.jpe'}
    for file_name in os.listdir(subfolder):
        file_path = os.path.join(subfolder, file_name)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext not in allowed_exts:
                try:
                    os.remove(file_path)  # Delete the file if it's not an image format
                except Exception as e:
                    logger.error(f"Could not delete file {file_path}: {e}")

# Check for problems with images and log problematic images
def check_pic(path_pic, files_to_delete):
    """Check and handle problematic images."""
    try:
        img = Image.open(path_pic, 'r')
        img.verify()
    except (FileNotFoundError, OSError, Image.UnidentifiedImageError) as e:
        logger.error(f"Problem with image: {path_pic}: {e}")
        with open('False.txt', 'a+') as f:
            f.write(str(path_pic) + '\n')
        try:
            os.remove(path_pic)
        except PermissionError:
            logger.warning(f'File in Use: {path_pic}')
            files_to_delete.append(path_pic)
        except (FileNotFoundError, OSError) as e:
            logger.error(f"Failed to delete file {path_pic}: {e}")
        return False
    return True

# Rename image files in a subfolder
def rename_image_files_in_subfolder(subfolder, subfolder_name):
    """Rename image files in a subfolder while checking their integrity."""
    try:
        unique_index = 0
        files_to_delete = []  # List of files that need to be deleted
        for index, file_name in enumerate(sorted(os.listdir(subfolder))):
            file_path = os.path.join(subfolder, file_name)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.jpe']:
                    # Check for problems with the image before renaming
                    if check_pic(file_path, files_to_delete):
                        # Rename the file if there is no problem with the image
                        new_file_name = f"{subfolder_name}_{index + 1}{file_ext}"
                        new_file_path = os.path.join(subfolder, new_file_name)
                        while os.path.exists(new_file_path):
                            unique_index += 1
                            new_file_name = f"{subfolder_name}_{index + 1}_{unique_index}{file_ext}"
                            new_file_path = os.path.join(subfolder, new_file_name)
                        os.rename(file_path, new_file_path)
                        logger.info(f"Renamed {file_name} to {new_file_name}")
    except PermissionError:
        logger.error(f"Error: failed to rename files in subfolder {subfolder}")

# Handle all subfolders recursively
def rename_image_files_in_subfolders(path):
    """Recursively process and rename image files in all subfolders."""
    for subfolder in get_subfolders(path):
        delete_non_image_files(subfolder)
        rename_image_files_in_subfolder(subfolder, os.path.basename(subfolder))

# Main process
def main():
    """Process all operations on the images and their directories."""
    logger.info("Starting image processing script...")
    path = "."
    rename_image_files_in_subfolders(path)

    # Get all subdirectories except 'test'
    sub_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d != 'test']
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.jpe']

    val_list = []
    train_list = []

    class_id = 0
    # Traverse image files in subdirectories to construct relative paths
    for class_dir in sub_dirs:
        for format in supported_formats:
            reg_file = f"{class_dir}/*/*{format}"
            val_list_num = 0
            for imagePath in sorted(glob.glob(reg_file)):
                imagePath = imagePath.replace("\\", "/")  # Ensure consistent path format
                if val_list_num < 500:
                    val_list.append(imagePath + " " + str(class_id))
                    val_list_num += 1
                else:
                    train_list.append(imagePath + " " + str(class_id))
        class_id += 1

    # Shuffle the data for training
    random.shuffle(train_list)

    # Save the training data
    with open('train.txt', 'w') as train_file:
        for img_file in train_list:
            logger.info("[Training Set] Generating: " + img_file)
            train_file.write(img_file + "\n")

    # Save the validation data
    with open('val.txt', 'w') as val_file:
        for img_file in val_list:
            logger.info("[Validation Set] Generating: " + img_file)
            val_file.write(img_file + "\n")

    # Save the label list
    with open('label.txt', 'w') as label_file:
        cls_id = 0
        for cls_name in sub_dirs:
            logger.info("[Label] Generating: " + cls_name)
            label_file.write(str(cls_id) + " " + cls_name + "\n")
            cls_id += 1

if __name__ == "__main__":
    main()
