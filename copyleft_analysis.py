"""
This script performs analysis of the copyleft results. It does so by performing the following tasks:

1. For a given large language model used, perform a border point analysis by calculating the accuracies of a rolling
   Majority-of-X vote. First it calculates the Majority-of-1 accuracy, then 3, then 5 and so on until all results are
   included. It then outputs a CSV file with the results, one LLM per row.
2. Choosing one value for X, output a table summarizing the results achieved in an HTML file for all LLM's with that
   value of X, putting it next to the OSADL results for comparison. It also renders accuracy.

A copyleft result is:
- Irrelevant if OSADL marks the license's copyleft state as "Questionable"
- Accurate if:
  - The LLM's result is True and OSADL marks the license as "Yes" or "Yes (restricted)"
  - The LLM's result is False and OSADL marks the license as "No"
- Inaccurate otherwise.

The total accuracy is the amount of accurate results divided by the amount of accurate + inaccurate results.

"""

import json
import utils
import os
from pprint import pprint

osadl_table = utils.get_osadl_copyleft_table()

def main():
    # Step 0: Enumerate all files in the results directory
    result_files_as_list = sorted([f for f in os.listdir('results') if f.endswith('_copyleft.json')])
    result_files = dict()  # llm_name -> run id -> filename, then llm_name -> filename sorted by run id afterwards
    for filename in result_files_as_list:
        llm_name = '-'.join(filename.split('-')[:-1])
        run_id = int(filename.split('-')[-1].replace('_copyleft.json', ''))
        if llm_name not in result_files:
            result_files[llm_name] = dict()
        result_files[llm_name][run_id] = os.path.join('results', filename)
    for llm_name in result_files:
        result_files[llm_name] = [result_files[llm_name][run_id] for run_id in sorted(result_files[llm_name].keys())]

    min_runs_available = min([len(runs) for runs in result_files.values()])

    # Helper lambda to get the first X runs for a given LLM.
    runs_for_majority_of_x = lambda x, llm_name: [run_file for run_file in result_files[llm_name]][:x]

    for i in range(15):
        i+=1
        print(i)
        pprint(runs_for_majority_of_x(i, "deepseek-r1-8b"))


def calculate_accuracy_by_majority(result_files):
    """
    Helper function to calculate the accuracy of a given set of result files by Majority-of-X voting.

    :param result_files: List of result files to use in calculation.
    """

if __name__ == "__main__":
    main()