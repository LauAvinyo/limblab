import os
import re

def file2dic(file):
    with open(file, "r") as f:
        pipeline = {}
        # Read each line in the file
        for line in f:
            # Split each line into key and value based on whitespace
            parts = line.strip().split(" ")
            # Assign key-value pairs to the dictionary
            pipeline[parts[0]] = " ".join(parts[1:])
    return pipeline


def dic2file(data_dict, filename):
    """
    Write a dictionary to a file in the format:
    key1 value1
    key2 value2
    ...
    """
    with open(filename, "w") as file:
        for key, value in data_dict.items():
            file.write(f"{key} {value}\n")


def closest_value(input_list: list, target: int) -> int:
    """"Get the closest value of the list to our target."""
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest



REFERENCE_LIMB_FOLDER = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/data/limb"

files = [file for file in os.listdir(REFERENCE_LIMB_FOLDER)
         if os.path.isfile(os.path.join(REFERENCE_LIMB_FOLDER, file))
         and not file.startswith(".DS") or file.startswith("-")]
reference_stages = [int(file.split(".")[0].split("_")[1]) for file in files]

def get_reference_limb(stage: int) -> str:
    """From the stage, get the refernce limb path"""
    file = os.path.join(REFERENCE_LIMB_FOLDER, "Limb-rec_"+str(stage)+".vtk")
    if os.path.isfile(file):
        return file
    return False



# Regular expression pattern to match RF, LF, RH, LH
PATTERN = r'\b(RF|LF|RH|LH)\b'

def get_side_postion(file):
    matches = re.findall(PATTERN, file.replace("_", " "))

    if len(matches) == 1:
        side = matches[0][0]
        position = matches[0][1]
        return side, position
    return None