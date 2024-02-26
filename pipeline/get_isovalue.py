from vedo import Volume, grep
from vedo.applications import IsosurfaceBrowser
import os

# TODO: DO WE WANT TO MODIFY?
# file_path = "config.txt"
# tag_to_find = "Tag2"
# new_value = "NewValue"

# # Read the file and store the lines
# with open(file_path, 'r') as file:
#     lines = file.readlines()

# # Find the line with the tag and update its value
# for i, line in enumerate(lines):
#     if line.startswith(f"{tag_to_find}:"):
#         lines[i] = f"{tag_to_find}: {new_value}\n"
#         break

# # Write the modified content back to the file
# with open(file_path, 'w') as file:
#     file.writelines(lines)


# TODO: This should be the input
folder = "HCR12_8a_dapi_405"

# Get the paths
pipeline = os.path.join(folder, "pipeline.txt")
path_volume = grep(pipeline, "VOLUME")[0][1]
print(f"Reading volume: {path_volume}")

# Read the volume
vol = Volume(path_volume)

# IsosurfaceBrowser(Plotter) instance:
plt = IsosurfaceBrowser(vol, use_gpu=True, c="gold")
plt.show(axes=7, bg2="lb")

# Get the isosurface value
iso_value = plt.sliders[0][0].value
plt.close()

# Store the value
with open(pipeline, "a") as f:
    print("ISOVAL", iso_value, file=f)
