import os


def get_integer_basename(filename):
    basename, _ = os.path.splitext(filename)
    try:
        return int(basename)
    except ValueError:
        return None
