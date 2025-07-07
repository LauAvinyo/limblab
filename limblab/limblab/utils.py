import os
import re

import matplotlib.colors as mcolors
import numpy as np


def load_pipeline(folder):
    """Load pipeline configuration from experiment folder."""
    pipeline_file = os.path.join(folder, "pipeline.log")
    return file2dic(pipeline_file)


# TODO: Extract this
styles = {
    0: ("#9ce4f3", "#128099"),
    1: ("#ec96f2", "#c90dd6"),
    "postions": {
        "number": ([0.1, 0.25], [0.2, 0.25]),
        "values": ([0.1, 0.1], [0.2, 0.1])
    },
    "channel_0": {
        "color": "#B0DB43"
    },
    "channel_1": {
        "color": "#db43b0"
    },
    "channel_2": {
        "color": "#43b0db"
    },
    "limb": {
        "alpha": 0.1,
        "color": "#FF7F11"
    },
    "reference": {
        "alpha": 1,
        "color": 1
    },
    "isosurfaces": {
        "alpha": 0.3,
        "alpha-unique": 0.8
    },
    "ui": {
        "primary": "#0d1b2a",
        "secondary": "#fb8f00"
    }
}


def file2dic(file):
    """Read a key-value file and return as dictionary."""
    with open(file, "r", encoding="utf-8") as f:
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
    with open(filename, "w", encoding="utf-8") as file:
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

current_path = os.path.abspath(__file__)

REFERENCE_LIMB_FOLDER = os.path.join(os.path.dirname(current_path), "limb")

files = [
    file for file in os.listdir(REFERENCE_LIMB_FOLDER)
    if os.path.isfile(os.path.join(REFERENCE_LIMB_FOLDER, file))
    and not file.startswith(".DS") or file.startswith("-")
]
reference_stages = [int(file.split(".")[0].split("_")[1]) for file in files]


def get_reference_limb(stage: int) -> str:
    """From the stage, get the reference limb path"""
    file = os.path.join(REFERENCE_LIMB_FOLDER,
                        "Limb-rec_" + str(stage) + ".vtk")
    if os.path.isfile(file):
        return file
    return False


# Regular expression pattern to match RF, LF, RH, LH
PATTERN = r'\b(RF|LF|RH|LH)\b'


def get_side_position(file):
    """Extract side and position from filename."""
    matches = re.findall(PATTERN, file.replace("_", " "))

    if len(matches) == 1:
        side = matches[0][0]
        position = matches[0][1]
        return side, position
    return None


def interpolate_colors(color1, color2, num_values):
    # Convert input colors to RGB
    rgb1 = np.array(mcolors.to_rgb(color1))
    rgb2 = np.array(mcolors.to_rgb(color2))

    # Generate linearly spaced values between the two colors
    interpolated_colors = [
        rgb1 + (rgb2 - rgb1) * i / (num_values - 1) for i in range(num_values)
    ]

    # Convert RGB values back to hexadecimal format
    interpolated_colors_hex = [
        mcolors.to_hex(color) for color in interpolated_colors
    ]

    return interpolated_colors_hex


def _pick_isovalues(arr, min_val, max_val, num_values):
    # Ensure the array is sorted
    arr = np.sort(arr)

    # Find the closest values to min_val and max_val
    min_idx = (np.abs(arr - min_val)).argmin()
    max_idx = (np.abs(arr - max_val)).argmin()

    # Ensure min_idx is less than max_idx
    if min_idx > max_idx:
        min_idx, max_idx = max_idx, min_idx

    # Generate indices for evenly spaced values
    indices = np.linspace(min_idx, max_idx, num=num_values, dtype=int)

    # Pick the values from the array
    picked_values = arr[indices]

    return picked_values


def pick_evenly_distributed_values(arr, num_values=20, resolution=None):
    if resolution is not None:
        # Determine the number of values to pick (10% of the filtered array length)
        num_values = max(1, int(len(arr) * resolution))
        # Ensure the number of values is at least 1
        if num_values < 1:
            num_values = 1

    # Generate indices for evenly spaced values
    indices = np.linspace(0, len(arr) - 1, num=num_values, dtype=int)
    # Pick the values from the filtered array
    picked_values = arr[indices]
    return picked_values
