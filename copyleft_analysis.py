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
    runs_for_majority_of_x_for_llm = lambda x, llm_name: [run_file for run_file in result_files[llm_name]][:x]
    runs_for_majority_of_x = lambda x: [run_file for llm_name in result_files.keys() for run_file in runs_for_majority_of_x_for_llm(x, llm_name)]

    # Step 1: Collate accuracy results for Majority-of-X for X = 1, 3, 5, ..., min_runs_available
    accuracies = dict()  # llm_name -> X -> accuracy, accurate, inaccurate, majority_results
    for i in range(0, min_runs_available, 2):
        i+=1
        maj_of_x_results = runs_for_majority_of_x(i)
        accuracy_results, majority_results = calculate_accuracy_by_majority(maj_of_x_results)
        for llm_name, accuracy_data in accuracy_results.items():
            if llm_name not in accuracies:
                accuracies[llm_name] = dict()
            accuracies[llm_name][i] = {
                "accuracy": accuracy_data["accuracy"],
                "accurate": accuracy_data["accurate"],
                "inaccurate": accuracy_data["inaccurate"],
                # "majorities": majority_results[llm_name]
            }

    # Step 2: Write rolling accuracies tables to .tex files
    num_columns = (min_runs_available // 2 + 1)  # All for Majority-of-X results

    with open('paper/autogen/copyleft_majority_accuracies_rollingx_perc.tex', 'w', encoding='utf-8') as f:
        # Header: Begin tabular
        f.write('\\begin{tabular}{|l|' + 'c' * num_columns + '|}\\hline\n')
        # Header: Column titles
        f.write('\t & \\multicolumn{' + str(num_columns) + '}{|c|}{\\textbf{Majority-of-X accuracy}}\\\\\n')
        # Header: Sub-column titles (X=1, 3, 5, ...)
        f.write('\t\\textbf{X = $\\ldots$} & ')
        f.write(' & '.join(['\\textbf{' + str(x) + '}' for x in range(1, min_runs_available + 1, 2)]))
        f.write(' \\\\\\hline\n')

        # Rows: One per LLM
        for llm_name, llm_accuracies in accuracies.items():
            f.write('\t\\textbf{' + llm_name.replace('_', '\\_') + '} & ')
            f.write(' & '.join([f"{llm_accuracies[x]['accuracy']:.2f}\\%" for x in range(1, min_runs_available + 1, 2)]))
            f.write(' \\\\\\hline\n')

        # Footer: End tabular
        f.write('\\end{tabular}\n')

    with open('paper/autogen/copyleft_majority_accuracies_rollingx_absolute.tex', 'w', encoding='utf-8') as f:
        # Header: Begin tabular
        f.write('\\begin{tabular}{|l|' + 'c' * num_columns + '|}\\hline\n')
        # Header: Column titles
        f.write('\t & \\multicolumn{' + str(num_columns) + '}{|c|}{\\textbf{Majority-of-X \\# accurate results}}\\\\\n')
        # Header: Sub-column titles (X=1, 3, 5, ...)
        f.write('\t\\textbf{X = $\\ldots$} & ')
        f.write(' & '.join(['\\textbf{' + str(x) + '}' for x in range(1, min_runs_available + 1, 2)]))
        f.write(' \\\\\\hline\n')

        # Rows: One per LLM
        for llm_name, llm_accuracies in accuracies.items():
            f.write('\t\\textbf{' + llm_name.replace('_', '\\_') + '} & ')
            f.write(' & '.join([f"{llm_accuracies[x]['accurate']}" for x in range(1, min_runs_available + 1, 2)]))
            f.write(' \\\\\\hline\n')

        # Footer: End tabular
        f.write('\\end{tabular}\n')

    # Step 3: Write summary tables for all Majority-of-X results
    for X in range(1, min_runs_available + 1, 2):
        maj_of_x_results = runs_for_majority_of_x(X)
        accuracy_results, majority_results = calculate_accuracy_by_majority(maj_of_x_results)

        for llm_name in accuracy_results.keys():
            # Write a LaTeX table for this LLM and X value that shows a confusion matrix using the detail values.
            with open(f'paper/autogen/copyleft_summary_{llm_name.replace(":", "-")}_majority_of_{X}.tex', 'w', encoding='utf-8') as f:
                f.write('\\begin{tabular}{l|cc}\\hline\n')
                f.write('\t\\textbf{OSADL \\textbackslash LLM} & Copyleft & Permissive\\\\\\hline\n')
                f.write('\tCopyleft & ' + f'{accuracy_results[llm_name]["detail"]["true_positive"]} & {accuracy_results[llm_name]["detail"]["false_negative"]}\\\\\n')
                f.write('\tPermissive & ' + f'{accuracy_results[llm_name]["detail"]["false_positive"]} & {accuracy_results[llm_name]["detail"]["true_negative"]}\\\\\\hline\n')
                f.write('\\end{tabular}\n')

    # Step 4: Write average accuracy and Majority-of-X accuracy to output for relevant runs for each given model
    VALUES_OF_X_PER_MODEL = {
        'deepseek-r1-8b': 7,
        'gemma3-4b': 3,
        'llama3': 15,
        'qwen3-8b': 3
    }
    for llm_name, X in VALUES_OF_X_PER_MODEL.items():
        files_for_llm = runs_for_majority_of_x_for_llm(X, llm_name)
        # Calculate average accuracy over each individual run
        accuracies = []
        osadl_table = utils.get_osadl_copyleft_table()
        for file in files_for_llm:
            with open(file, 'r') as f:
                data = json.load(f)
                accurate = 0
                inaccurate = 0
                for license_id, result_entry in data['copyleft'].items():
                    llm_result = result_entry['result']
                    osadl_result = osadl_table['copyleft'].get(license_id)[0]
                    match osadl_result:
                        case "Y":
                            if llm_result is True:
                                accurate += 1
                            else:
                                inaccurate += 1
                        case "N":
                            if llm_result is False:
                                accurate += 1
                            else:
                                inaccurate += 1
                        case "Q":
                            # Ignore
                            pass
                total = accurate + inaccurate
                accuracy = (accurate / total) * 100 if total > 0 else 0.0
                accuracies.append(accuracy)
        print(f"Average accuracy for {llm_name} over {X} runs: {sum(accuracies)/len(accuracies):.2f}%")

def calculate_accuracy_by_majority(result_files):
    """
    Helper function to calculate the accuracy of a given set of result files by Majority-of-X voting.

    :param result_files: List of result files to use in calculation.
    """
    majority_votes = dict()  # llm_name -> license_id -> list of votes (True/False)
    for result_file in result_files:
        with open (result_file, 'r') as f:
            data = json.load(f)
            llm_name = data['llm']
            if llm_name not in majority_votes:
                majority_votes[llm_name] = dict()
            for license_id, result_entry in data['copyleft'].items():
                if license_id not in majority_votes[llm_name]:
                    majority_votes[llm_name][license_id] = list()
                majority_votes[llm_name][license_id].append(result_entry['result'])

    # transform the lists into actual results by majority vote
    majority_results = dict()  # llm_name -> license_id -> result (True/False)
    for llm_name, license_votes in majority_votes.items():
        majority_results[llm_name] = dict()
        for license_id, votes in license_votes.items():
            amount_true = votes.count(True)
            amount_false = votes.count(False)
            if amount_true == amount_false:
                print(f"Warning: Votes for {llm_name} on {license_id} with X = {len(votes)} are tied. Defaulting to False.")
            majority_results[llm_name][license_id] = (amount_true > amount_false)

    # Calculate per-LLM accuracy
    osadl_results = utils.get_osadl_copyleft_table()
    llm_accuracy = dict()
    # For each individual license per LLM, compare to OSADL
    for llm_name in majority_results.keys():
        accurate = 0
        inaccurate = 0
        true_positive = 0
        false_positive = 0
        true_negative = 0
        false_negative = 0
        for license_id, llm_result in majority_results[llm_name].items():
            osadl_result = osadl_results['copyleft'].get(license_id)[0]
            match osadl_result:
                case "Y":
                    if llm_result is True:
                        accurate += 1
                        true_positive += 1
                    else:
                        inaccurate += 1
                        false_negative += 1
                case "N":
                    if llm_result is False:
                        accurate += 1
                        true_negative += 1
                    else:
                        inaccurate += 1
                        false_negative += 1
                case "Q":
                    # Ignore
                    pass

        total = accurate + inaccurate
        accuracy = (accurate / total) * 100 if total > 0 else 0.0
        llm_accuracy[llm_name] = {
            "accurate": accurate,
            "inaccurate": inaccurate,
            "accuracy": accuracy,
            "detail": {
                "true_positive": true_positive,
                "false_positive": false_positive,
                "true_negative": true_negative,
                "false_negative": false_negative
            }
        }

    return llm_accuracy, majority_results


if __name__ == "__main__":
    main()