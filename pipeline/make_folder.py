import os

filename = "../data/HCR/HCR12_8a_dapi_405.tif"

# Create a working folderx
folder = os.path.splitext(os.path.basename(filename))[0]

if os.path.exists(folder):
    print("Folder already exists!")
    # TODO ask her if things stuff
    exit()

os.mkdir(folder)

# Create the pipeline file
pipeline = os.path.join(folder, "pipeline.txt")
with open(pipeline, "w") as f:
    print("FOLDER", folder, file=f)
    # TODO
    # Get the other channels!
