"""
This file implements a naive approach to determine compatibility of licenses.
"""
import json
import time

import ollama
import utils

QUERY_TEMPLATE = """
=== DEFINITION OF COMPATIBILITY ===

Compatibility of a particular first (leading) license with another (subordinate) license becomes an issue when a work that is licensed under the other license is to be integrated into a common work and to be compliantly copied and distributed under the leading license.

Such compatibility is assumed, if

- compatibility with the other license is explicitly ruled in a particular license, or
- the two licenses in question both do not contain a copyleft clause, or
- the leading license contains a copyleft clause and the other license does not and also does not impose any obligation that the first license does not allow to impose.

=== LEADING LICENSE ===

{leading_license_id}

=== SUBORDINATE LICENSE ===

{subordinate_license_id}

=== INSTRUCTION ===

You are a license compatibility expert. Determine whether the leading license is compatible with the subordinate license based on the definitions above.
It is more costly to answer "yes" incorrectly, than to answer "no" incorrectly.
Start your answer with the lowercase word "yes" or "no", followed by a space and a short explanation of your decision, to allow for easy parsing.
"""

def naive_compatibility_check(leading_license_id, subordinate_license_id):
    """
    Determines whether the leading license is compatible with the subordinate license using a language model.

    :param leading_license_id: The ID of the leading license.
    :param subordinate_license_id: The ID of the subordinate license.
    :return: A tuple (is_compatible, explanation) where is_compatible is a boolean and explanation is a string.
    """
    #leading_license_fulltext = utils.get_license_fulltext(leading_license_id)
    #subordinate_license_fulltext = utils.get_license_fulltext(subordinate_license_id)

    #if not leading_license_fulltext or not subordinate_license_fulltext:
    #    return False, "Full text of one or both licenses not found."

    query = QUERY_TEMPLATE.format(
        leading_license_id=leading_license_id,
        subordinate_license_id=subordinate_license_id
    )

    # Save query to a file for debugging
    with open(f"queries/NAIVE-LEADING-{leading_license_id}-SUBORDINATE-{subordinate_license_id}.txt", "w", encoding="utf-8") as f:
        f.write(query)

    response = ollama.generate(prompt=query, model="llama3")

    if response.response.startswith("yes"):
        return True, response.response[3:].strip()
    else:
        return False, response.response[2:].strip()

if __name__ == "__main__":
    # Get the matrix of licenses
    matrix = utils.get_osadl_matrix()
    matrix_as_dict = utils.parse_osadl_compat_matrix(matrix)

    if not matrix:
        print("OSADL matrix not found or could not be loaded.")
        exit(1)

    inference_times = []

    num_licenses = len(matrix["licenses"])
    num_pairs = num_licenses * num_licenses
    print(f"Found {num_licenses} licenses in the OSADL matrix, checking {num_pairs} pairs of leading and subordinate licenses.")

    work_sequence_number = 0

    result_matrix = {
        # ISO timestamp of the current time
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "licenses": []
    }

    for entry in matrix["licenses"]:
        leading_license_id = entry.get("name")
        if not leading_license_id:
            continue

        # Add leading license to the result matrix
        result_matrix["licenses"].append({
            "name": leading_license_id,
            "compatibilities": []
        })

        for subordinate_entry in matrix["licenses"]:
            subordinate_license_id = subordinate_entry.get("name")
            if not subordinate_license_id:
                continue

            # Add compatibility entry
            result_matrix["licenses"][-1]["compatibilities"].append({
                "name": subordinate_license_id,
                "is_compatible": None,
                "explanation": None
            })

            work_sequence_number += 1

            if leading_license_id == subordinate_license_id:
                # If both licenses are the same, they are trivially compatible
                result_matrix["licenses"][-1]["compatibilities"][-1]["compatibility"] = "Same"
                result_matrix["licenses"][-1]["compatibilities"][-1]["explanation"] = "n.a."
                continue

            # Run inference
            time_start = time.time()
            is_compatible, explanation = naive_compatibility_check(leading_license_id, subordinate_license_id)
            time_end = time.time()

            # Set results
            result_matrix["licenses"][-1]["compatibilities"][-1]["compatibility"] = "Yes" if is_compatible else "No"
            result_matrix["licenses"][-1]["compatibilities"][-1]["explanation"] = explanation

            # Calculate inference time and keep track of the last 10 times
            inference_time = time_end - time_start
            inference_times.append(inference_time)
            inference_times = inference_times[-10:]  # Keep only the last 10 times for averaging
            avg_inference_time = sum(inference_times) / len(inference_times)

            # Check is OSADL matrix agrees with the inference
            is_osadl_compatible = matrix_as_dict.get(leading_license_id, {}).get(subordinate_license_id, {}).get("compatibility", None)

            print(f"Work {work_sequence_number}/{num_pairs}: {leading_license_id} vs {subordinate_license_id} - "
                  f"Inference Time: {inference_time:.2f}s, Avg Inference Time: {avg_inference_time:.2f}s, Time remaining: {(num_pairs-work_sequence_number)*avg_inference_time}s - "
                  f"OSADL {'agrees' if (is_compatible and (is_osadl_compatible == 'Yes')) or (not is_compatible and (is_osadl_compatible == 'No')) else 'DISAGREES'}")

            # Save the result matrix to a json file
            json.dump(result_matrix, open("../naive_compatibility.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
