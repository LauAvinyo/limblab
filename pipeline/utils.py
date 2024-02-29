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


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest
