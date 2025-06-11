"""
This script locates non-trivial combinations in the license compatibility matrix.

We recall the definition of compatibility:
- compatibility with the other license is explicitly ruled in a particular license, or
- the two licenses in question both do not contain a copyleft clause, or
- the leading license contains a copyleft clause and the other license does not and also does not impose any obligation that the first license does not allow to impose.

We recall the definition of incompatibility:
- incompatibility with another license is explicitly ruled in a particular license, or
- one license imposes an obligation that the other license does not allow to impose, or
- the two licenses in question both contain a copyleft clause and no license contains an explicit compatibility clause for this license combination.

The non-trivial combinations are those that are not resolved by clauses 1 and 2 of the compatibility definition,
or clauses 1 and 3 of the incompatibility definition.
"""
import license_compatibility
import utils
import json

LICENSE_EVALUATION_WHITELIST = [
    "MIT",
    "Apache-2.0",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "BSD-3-Clause",
    "GPL-2.0-only",
    "CC0-1.0",
    "Unlicense",
    "MPL-2.0",
    "BSD-2-Clause",
    "CC-BY-4.0",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "CC-BY-SA-4.0",
    "ISC",
    "MIT-0",
    "BSD-3-Clause-Clear",
    "EPL-2.0",
    "WTFPL",
    "EUPL-1.2",
    "0BSD",
    "BSL-1.0",
    "Zlib",
    "EPL-1.0",
    "MulanPSL-2.0",
    "UPL-1.0",
    "OFL-1.1",
    "Artistic-2.0",
]

def evaluate_licenses(leading_license_id, subordinate_license_id):
    """
    Evaluates the compatibility of two licenses based on the OSADL matrix, and their reported copyleft clause presence.
    :param leading_license_id: The ID of the leading license.
    :param subordinate_license_id: The ID of the subordinate license.
    :return: A tuple (trivially_compatible, trivially_incompatible).
    """
    # Load the copyleft table provided by OSADL
    copyleft_table = utils.get_osadl_copyleft_table()
    if not copyleft_table:
        print("OSADL copyleft table not found or could not be loaded.")
        return None, None

    leading_has_copyleft = True if copyleft_table["copyleft"][leading_license_id].lower()[:3] == "yes" else False
    subordinate_has_copyleft = True if copyleft_table["copyleft"][subordinate_license_id].lower()[:3] == "yes" else False

    triv_compat = False
    triv_incompat = False

    if leading_has_copyleft and subordinate_has_copyleft:
        triv_incompat = True
    #elif leading_has_copyleft and not subordinate_has_copyleft:
    #    triv_compat = True
    elif not leading_has_copyleft and subordinate_has_copyleft:
        triv_compat = True
    elif not leading_has_copyleft and not subordinate_has_copyleft:
        # If both licenses do not have a copyleft clause, they are trivially compatible.
        triv_compat = True

    return triv_compat, triv_incompat

if __name__ == '__main__':
    allow_nonbinary_decisions = False  # Set to True to calculate statistics for non-binary decisions.
    llm_passthrough_for_unknowns = False
    # Get the matrix of licenses
    matrix = utils.get_osadl_matrix()

    if not matrix:
        print("OSADL matrix not found or could not be loaded.")
        exit(1)

    # Parse the OSADL compatibility matrix
    compat_matrix = utils.parse_osadl_compat_matrix(matrix)

    results = {
        "licenses": [],
    }
    stat_per_category_count = {}
    stat_correct_per_category_count = {}

    license_eval_whitelist = {}
    for license_id in LICENSE_EVALUATION_WHITELIST:
        license_eval_whitelist[license_id] = False

    # Iterate through compat_matrix["licenses"], the "name" field is the leading license ID.
    for leading_license_id, leading_license_entry in compat_matrix.items():
        if leading_license_id not in LICENSE_EVALUATION_WHITELIST:
            continue
        license_eval_whitelist[leading_license_id] = True  # Mark this license as evaluated.

        result_object = {
            "name": leading_license_id,
            "compatibilities": [],
        }
        results["licenses"].append(result_object)

        # Now select each subordinate license from leading_license_entry
        for subordinate_license_id, combination_object in leading_license_entry.items():
            if subordinate_license_id not in LICENSE_EVALUATION_WHITELIST:
                continue
            license_eval_whitelist[subordinate_license_id] = True  # Mark this license as evaluated.
            if allow_nonbinary_decisions is False and (combination_object["compatibility"] not in ["Yes", "No", "Same"]):
                # If the combination is already resolved in the OSADL matrix, we can skip it.
                continue

            decision = None

            # If both licenses are the same, store 'Same', report trivially compatible and not trivially incompatible.
            if leading_license_id == subordinate_license_id:
                result_object["compatibilities"].append({
                    "name": subordinate_license_id,
                    "trivially_compatible": True,
                    "trivially_incompatible": False,
                    "compatibility": "Same",
                    "explanation": "n/a"
                })
                decision = "Same"
            else:
                # Evaluate the compatibility of the two licenses
                trivially_compatible, trivially_incompatible = evaluate_licenses(leading_license_id, subordinate_license_id)

                # 4-state matrix. If either trivially_compatible or trivially_incompatible is True but not the other, we register this compatibility.
                # If both are True, we register 'CONFLICTING', if both are False, we register 'UNKNOWN'.
                decision = (
                    "Yes" if (trivially_compatible and not trivially_incompatible) else
                    "No" if (trivially_incompatible and not trivially_compatible) else
                    "CONFLICTING" if (trivially_compatible and trivially_incompatible) else
                    "UNKNOWN"
                )

                reason = "Trivial check."

                if decision == "UNKNOWN" and llm_passthrough_for_unknowns:
                    # If we are allowed to pass through unknown decisions to the LLM, we do so.
                    print(f"==== LLM PASSTHROUGH FOR NON-TRIVIAL DECISION (Leading: {leading_license_id}, subordinate: {subordinate_license_id}) ====")
                    compatible, incompatible, reason = license_compatibility.compatibility_check(leading_license_id, subordinate_license_id)
                    print(f"Reasoning: {reason}")
                    decision = (
                        "Yes" if (compatible and not incompatible) else
                        "No" if (incompatible and not compatible) else
                        "CONFLICTING" if (compatible and incompatible) else
                        "UNKNOWN"
                    )
                    print(f"Decision: {decision}, OSADL Decision: {combination_object['compatibility']}, Agreed: {decision == combination_object['compatibility']}")
                    print("==========================================")


                result_object["compatibilities"].append({
                    "name": subordinate_license_id,
                    "trivially_compatible": trivially_compatible,
                    "trivially_incompatible": trivially_incompatible,
                    "compatibility": decision,
                    "explanation": reason
                })

            # Add to statistics.
            if decision not in stat_per_category_count:
                stat_per_category_count[decision] = 0
            stat_per_category_count[decision] += 1
            if decision == "Yes" or decision == "No":
                osadl_decision = combination_object["compatibility"]
                if decision == osadl_decision:
                    if decision not in stat_correct_per_category_count:
                        stat_correct_per_category_count[decision] = 0
                    stat_correct_per_category_count[decision] += 1
                else:
                    print(f"Discrepancy found for {leading_license_id} and {subordinate_license_id}: "
                          f"Decision: {decision}, OSADL Decision: {osadl_decision}")
                    print(f"-> Explanation: {combination_object['explanation']}")

            # Save the results to a file
            with open(f"results/matrix_trivial_with_llm_passthrough.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4)

    # Print statistics
    if any(license_eval_whitelist.values()):
        print("\nWhitelisted licenses not evaluated:")
        for license_id, evaluated in license_eval_whitelist.items():
            if not evaluated:
                print(f"- {license_id}")
    print("\nStatistics:")
    print(f"Total combinations evaluated: {sum(stat_per_category_count.values())}")
    for category, count in stat_per_category_count.items():
        print(f"{category}: {count}", end="")
        if category in stat_correct_per_category_count:
            correct_count = stat_correct_per_category_count[category]
            print(f" (Correct: {correct_count}, Accuracy: {correct_count / count:.2%})")
        else:
            print()  # Flush the line anyways.