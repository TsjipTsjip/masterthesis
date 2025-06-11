"""
This script queries a model to test a leading and subordinate license combination against the definition of compatibility and incompatibility provided by OSADL.
"""

"""
This file implements a naive approach to determine compatibility of licenses.
"""
import json
import time

import ollama
import utils

MODEL_NAME="qwen3:8b"  # Model to use for inference
QUERY_TEMPLATE = """
=== LEADING LICENSE FULLTEXT ===

{leading_license_fulltext}

=== SUBORDINATE LICENSE FULLTEXT ===

{subordinate_license_fulltext}

=== DEFINITION OF COMPATIBILITY ===
Compatibility is assumed if:
- compatibility with the other license is explicitly ruled in a particular license, or
- the two licenses in question both do not contain a copyleft clause, or
- the leading license contains a copyleft clause and the other license does not and also does not impose any obligation that the first license does not allow to impose.

=== DEFINITION OF INCOMPATIBILITY ===
Incompatibility is assumed if:
- incompatibility with another license is explicitly ruled in a particular license, or
- one license imposes an obligation that the other license does not allow to impose, or
- the two licenses in question both contain a copyleft clause and no license contains an explicit compatibility clause for this license combination.

=== INSTRUCTION ===

You are a license compatibility expert. Determine whether the leading license is compatible or incompatible with the subordinate license based on the definitions above.
Begin your answer with the words: "Compatible", "Incompatible", "Both", or "Neither", followed by a space and a short explanation of your decision, to allow for easy parsing.
"""

def compatibility_check(leading_license_id, subordinate_license_id):
    """
    Determines whether the leading license is compatible with the subordinate license using a language model.

    :param leading_license_id: The ID of the leading license.
    :param subordinate_license_id: The ID of the subordinate license.
    :return: A tuple (compatible, incompatible, explanation) where compatible and incompatible are booleans, and explanation is a string.
    """
    leading_license_fulltext = utils.get_license_fulltext(leading_license_id)
    subordinate_license_fulltext = utils.get_license_fulltext(subordinate_license_id)

    if not leading_license_fulltext or not subordinate_license_fulltext:
        return False, "Full text of one or both licenses not found."

    query = QUERY_TEMPLATE.format(
        leading_license_fulltext=leading_license_fulltext,
        subordinate_license_fulltext=subordinate_license_fulltext
    )

    # Save query to a file for debugging
    with open(f"queries/COMPAT-LEADING-{leading_license_id}-SUBORDINATE-{subordinate_license_id}.txt", "w", encoding="utf-8") as f:
        f.write(query)

    response = ollama.generate(prompt=query, model=MODEL_NAME).response.strip()

    think_text = response.split("</think>")[0].replace("<think>", "").strip()
    answer_text = response.split("</think>")[-1].strip()

    compatible = answer_text[0].lower() == 'c' or answer_text[0].lower() == 'b'
    incompatible = answer_text[0].lower() == 'i' or answer_text[0].lower() == 'b'

    return compatible, incompatible, response



