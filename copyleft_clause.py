"""
This file contains an LLM-backed approach to determine whether a single license contains a copyleft clause.
"""
import json
import time

import ollama
import utils

MODEL_NAME = "llama3"  # Model to use for inference
QUERY_TEMPLATE = """
=== LICENSE FULL TEXT ===

{license_fulltext}

=== INSTRUCTION ===

You are a license compatibility expert. Does the license contain a copyleft clause? A copyleft clause is a provision that requires derivative works to be distributed under the same license terms as the original work, ensuring that the freedoms granted by the license are preserved in derivative works.
Begin your answer with a yes or a no for easy parsing.
"""

def contains_copyleft_clause(license_id):
    """
    Determines whether the license contains a copyleft clause using a language model.

    :param license_id: The ID of the license.
    :return: A tuple (contains_copyleft, explanation) where contains_copyleft is a boolean and explanation is a string.
    """
    license_fulltext = utils.get_license_fulltext(license_id)

    query = QUERY_TEMPLATE.format(license_fulltext=license_fulltext)

    # Save query to a file for debugging
    with open(f"queries/CONTAINS-COPYLEFT-{license_id}.txt", "w", encoding="utf-8") as f:
        f.write(query)

    response = ollama.generate(prompt=query, model=MODEL_NAME)

    print(response.response.strip())

    # Parse the response, begins with a think block sometimes, if it does, skip over it. Take the last section.
    # Now we assume the response starts with "yes" or "no" followed by a space and an explanation.
    result = response.response.strip().split("</think>")[-1].strip().split(" ", 1)[0].lower()[0] == "y"

    return result, response.response.strip()

if __name__ == "__main__":
    # Get the matrix of licenses
    matrix = utils.get_osadl_matrix()
    osadl_copyleft_table = utils.get_osadl_copyleft_table()

    if not matrix:
        print("OSADL matrix not found or could not be loaded.")
        exit(1)

    inference_times = []
    times_agreed = 0

    num_licenses = len(matrix["licenses"])

    result_table = {
        "llm": MODEL_NAME,
        "copyleft": {},
    }

    for i, license_entry in enumerate(matrix["licenses"]):
        license_id = license_entry["name"]

        # Run inference
        time_start = time.time()
        contains_copyleft, explanation = contains_copyleft_clause(license_id)
        time_end = time.time()
        inference_time = time_end - time_start

        # Aggregate timing results
        inference_times.append(inference_time)
        inference_times = inference_times[-20:] # Keep only the last 20 entries for averaging
        avg_inference_time = sum(inference_times) / len(inference_times)

        # Store results
        result_table["copyleft"][license_id] = {
            "result": contains_copyleft,
            "explanation": explanation
        }

        # Check OSADL's evaluation
        osadl_result = osadl_copyleft_table["copyleft"].get(license_id)

        # Check if our result and OSADL's result agree
        agree_boolean = ((osadl_result[0] == "Y") == contains_copyleft)
        if agree_boolean:
            times_agreed += 1

        # Print progress
        print(f"{i + 1}/{num_licenses} - {license_id}: "
              f"LLM: {contains_copyleft}, OSADL: {osadl_result[0]}, "
              f"Agree: {agree_boolean}, "
              f"Inference Time: {inference_time:.2f}s, "
              f"Avg Time: {avg_inference_time:.2f}s, "
              f"Accuracy: {times_agreed / (i + 1) * 100:.2f}%, "
              f"Time remaining: {(num_licenses - i - 1) * avg_inference_time:.2f}s")

        # Save results to a file
        with open(f"{MODEL_NAME.replace(":","-")}_copyleft.json", "w", encoding="utf-8") as f:
            json.dump(result_table, f, indent=4)