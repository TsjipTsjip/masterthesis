import json
import os


def get_license_fulltext(license_id, fulltext_dir="spdx"):
    """
    Retrieves the full text of a license from a local file.
    :param license_id: The ID of the license to retrieve.
    :param fulltext_dir: The directory where the full text files are stored.
    :return: The full text of the license or None if not found.
    """
    try:
        with open(f"{fulltext_dir}/{license_id}.txt", 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Full text for license {license_id} not found in {fulltext_dir}.")
        return None

def get_osadl_matrix(matrix_filename="osadl/matrixseqexpl.json"):
    """
    Loads the OSADL matrix from a JSON file.
    :param matrix_filename: The filename of the OSADL matrix JSON file.
    :return: The OSADL matrix as a dictionary or None if not found.
    """
    try:
        with open(matrix_filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"OSADL matrix file {matrix_filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {matrix_filename}.")
        return None

def parse_osadl_compat_matrix(matrix):
    """
    Parses the OSADL matrix to extract license compatibility information.
    :param matrix: The OSADL matrix as a dictionary.
    :return: A dictionary mapping leading licenses to their subordinate licenses.
    """
    compat_matrix = {}
    for entry in matrix.get("licenses", []):
        leading_license = entry.get("name")
        if leading_license:
            compat_matrix[leading_license] = {}

            for compatibility in entry.get("compatibilities", []):
                subordinate_license = compatibility.get("name")
                if subordinate_license:
                    compat_matrix[leading_license][subordinate_license] = {
                        "compatibility": compatibility.get("compatibility"),
                        "explanation": compatibility.get("explanation")
                    }
    return compat_matrix

def get_osadl_copyleft_table(copyleft_filename="osadl/copyleft.json"):
    """
    Loads the OSADL copyleft table from a JSON file.
    :param copyleft_filename: The filename of the OSADL copyleft table JSON file.
    :return: The OSADL copyleft table as a dictionary or None if not found.
    """
    try:
        with open(copyleft_filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"OSADL copyleft table file {copyleft_filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {copyleft_filename}.")
        return None

def get_osadl_dictionary(category: str):
    """
    Retrieves the OSADL dictionary for a specific category.
    :param category: The category of the dictionary to retrieve (e.g., 'actions', 'language', 'terms').
    :return: A dictionary containing the OSADL language objects for the specified category or None if not found.
    """
    directory_location = f"osadl/{category}"
    # Check if the directory exists
    if not os.path.exists(directory_location):
        print(f"Directory {directory_location} does not exist.")
        return None

    # Initialize an empty dictionary to hold the language objects
    osadl_language_objects = {}

    # Loop over all .txt files in the specified directory
    for filename in os.listdir(directory_location):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_location, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    # Use the filename without extension as the key
                    key = os.path.splitext(filename)[0].split('/')[-1].strip()  # Get the last part of the filename
                    osadl_language_objects[key] = content
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return osadl_language_objects


def get_osadl_language_object():
    """
    Loads the OSADL language objects from .txt files in the 'osadl' directory.
    There is three subdirectories which we expect to exist: actions, language, terms
    :return: A dictionary containing the OSADL language objects or None if not found.
    """

    language_objects = {
        "actions": get_osadl_dictionary("actions"),
        "language": get_osadl_dictionary("language"),
        "terms": get_osadl_dictionary("terms")
    }

    if not all(language_objects.values()):
        print("One or more OSADL language object categories could not be loaded.")

    return language_objects if all(language_objects.values()) else None
