import os
import shutil
import sys

data_path = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/data/HCR"

if len(sys.argv) != 2:
    print("Usage: python dapi")

dapi = sys.argv[1]

experiment = "_".join(os.path.basename(dapi).split("_")[:3]).upper()

# Create the folder
folder = os.path.splitext(os.path.basename(experiment))[0]
folder = os.path.join(data_path, folder)
if os.path.exists(folder):
    print("Folder already exists!")
    answer = input(
        "Do you want to rm and create a new one? [y/n]").strip().lower()
    if answer == "y":
        shutil.rmtree(folder)
    else:
        exit()
os.mkdir(folder)

# Create the pipeline file
pipeline = os.path.join(folder, "pipeline.log")
with open(pipeline, "w") as f:
    print("BASE", dapi, file=f)
