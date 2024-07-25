import os

# Change this to your directory
directory = '/Users/lauavino/Desktop/HCR-Database/raw_data/'
files = os.listdir(directory)

# Process each file

limbs = []
for filename in files:
    if filename.startswith("."):
        continue
    # Split the filename at underscores
    split_name = filename.split('_')

    # Get the first three values
    first_three = split_name[:3]

    # Join the first three values with underscores
    new_name = '_'.join(first_three)

    # Print the new name
    limbs.append(new_name)
limbs = list(set(limbs))
limbs = sorted(limbs, key=lambda x: x.split()[0])

for limb in limbs:
    print(limb)
