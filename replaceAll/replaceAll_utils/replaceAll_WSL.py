#!/home/luciacev/Slicer-5.4.0-linux-amd64/bin/PythonSlicer
#/usr/bin/env pythonSlicer
# /usr/bin/env python-real
import os
import shutil
import argparse
import SimpleITK as sitk

def get_file_extension(source_path):
    name = os.path.basename(source_path)
    if name.count('.') > 1:
        return '.' + '.'.join(name.split('.')[1:])
    return os.path.splitext(source_path)[1]


def main(args):

    input_folder = args.input_folder
    replace = args.replace
    by = args.by
    output_folder = args.output_folder
    overwrite = args.overwrite
    log_path = args.log_path

    # For the progress bar display
    with open(log_path, 'w') as log_f:
        log_f.truncate(0)
    index = 0
    

    # Create new folder and copy the contents
    if overwrite == "False":
        for item in os.listdir(input_folder):
            source_path = os.path.join(input_folder, item)

            # Create directory if needed
            if not os.path.exists(output_folder):
                os.mkdir(output_folder)
            destination_path = os.path.join(output_folder, item)
            file_extension = get_file_extension(source_path)

            # Checks the extension of the file
            if file_extension == ".nii" or file_extension == ".nii.gz":
                image = sitk.ReadImage(source_path)
                sitk.WriteImage(image, destination_path)
            elif file_extension == ".vtk":
                shutil.copy2(source_path, destination_path)

            # For the progress bar display
            with open(log_path, 'r+') as log_f:
                log_f.write(str(index))
        
        index += 1

    # Rename the folder as specified
    for item in os.listdir(output_folder):
        if replace in item:
            new_name = item.replace(replace, by)
            os.rename(os.path.join(output_folder, item), os.path.join(output_folder, new_name))
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('input_folder',type=str)
    parser.add_argument('replace',type=str)
    parser.add_argument('by',type=str)
    parser.add_argument('output_folder',type=str)
    parser.add_argument('overwrite',type=str)
    parser.add_argument('log_path',type=str)

    args = parser.parse_args()
    main(args)
