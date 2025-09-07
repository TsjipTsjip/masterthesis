"""
This script generates a CSV file containing one line for each license combination.
Columns:
- leading_license_id: The ID of the leading license.
- subordinate_license_id: The ID of the subordinate license.
- leading_copyleft_status: The copyleft status of the leading license.
- subordinate_copyleft_status: The copyleft status of the subordinate license.
- osadl_compatibility: The OSADL compatibility status of the combination.
- explanation: The explanation provided by OSADL for the compatibility status.

"""
import utils

if __name__ == '__main__':
    # Get the matrix of licenses
    matrix = utils.get_osadl_matrix()

    if not matrix:
        print("OSADL matrix not found or could not be loaded.")
        exit(1)

    # Parse the OSADL compatibility matrix
    compat_matrix = utils.parse_osadl_compat_matrix(matrix)

    # Get the copyleft table provided by OSADL
    copyleft_table = utils.get_osadl_copyleft_table()

    with open("license_compatibility.csv", "w") as csv_file:
        # Write the header line
        csv_file.write("leading_license_id;subordinate_license_id;leading_copyleft_status;"
                       "subordinate_copyleft_status;osadl_compatibility;explanation\n")

        # Iterate through compat_matrix["licenses"], the "name" field is the leading license ID.
        for leading_license_id, leading_license_entry in compat_matrix.items():

            # Now select each subordinate license from leading_license_entry
            for subordinate_license_id, combination_object in leading_license_entry.items():

                # Skip if same
                if leading_license_id == subordinate_license_id:
                    continue

                # Get copyleft status of leading and subordinate licenses
                leading_copyleft_status = copyleft_table["copyleft"][leading_license_id]
                subordinate_copyleft_status = copyleft_table["copyleft"][subordinate_license_id]

                # Get OSADL evaluation of the combination
                osadl_compatibility = combination_object["compatibility"]
                explanation = combination_object["explanation"]

                # Write the CSV line, quoting the explanation to handle commas
                csv_file.write(f"{leading_license_id};{subordinate_license_id};"
                               f"{leading_copyleft_status};{subordinate_copyleft_status};"
                               f"{osadl_compatibility};\"{explanation}\"\n")