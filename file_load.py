import json


def read_file(file_path):

    if file_path is None:
        raise ValueError("ANNOTATION_PATH environment variable not set")

    with open(file_path, 'r') as f:
        data = json.load(f)

    return data



def write_file(data, output_path):

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)