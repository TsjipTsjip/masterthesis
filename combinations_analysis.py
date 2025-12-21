import os
import json
import itertools


def assess_combination(license1, license2, status1, status2):
    """Function to assess combined copyleft status."""
    match (status1, status2):
        case (False, False): # Permissive-Permissive
            return True
        case (False, True): # Permissive-Copyleft
            return False
        case (True, False): # Copyleft-Permissive
            return True
        case (True, True): #Copyleft-Copyleft
            return False


def osadl_accurate_for_combination(license1, license2, first_result):
    """Placeholder function to check accuracy of first function's result."""
    # This will be implemented later
    return True


def process_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    licenses = list(data.keys())
    total_combinations = len(licenses) * (len(licenses) - 1) // 2
    correct_count = 0

    for license1, license2 in itertools.combinations(licenses, 2):
        status1 = data[license1]
        status2 = data[license2]

        # Call first placeholder function
        first_result = assess_combination(license1, license2, status1, status2)

        # Call second placeholder function
        second_result = osadl_accurate_for_combination(license1, license2, first_result)

        if second_result:
            correct_count += 1

    accuracy = (correct_count / total_combinations) * 100 if total_combinations > 0 else 0
    return accuracy, correct_count


def main():
    directory = 'results/autogen'
    accuracies = []
    file_paths = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_paths.append(file_path)

    for file_path in sorted(file_paths):
        accuracy, correct = process_json_file(file_path)
        accuracies.append((file_path.split('/')[-1], accuracy, correct))

    for file, acc, correct in accuracies:
        print(f"File: {file}, Accuracy: {acc:.2f}%, Correct Assessments: {correct}")


if __name__ == "__main__":
    main()