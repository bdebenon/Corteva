import argparse
import logging
import sys
import pandas as pd
from json import dumps

VALID_INPUT_FORMATS = ["csv"]
VALID_OUTPUT_FORMATS = ["json"]


def failure_detected(error):
    logging.error(error)
    exit(-1)


def process_user_data(input_file_paths, output_file_path):
    user_data = set()  # use a set here so we do not create any duplicates

    # Extract data from each input file
    for file_path in input_file_paths:
        logging.debug(f"Reading contents of file: {file_path}")
        try:
            # Handle csv format
            if file_path.lower().endswith("csv"):
                df = pd.read_csv(file_path)
                for index, row in df.iterrows():
                    first_name, last_name = row["full_name"].split(" ")
                    email = row["email"]
                    user_data.add((first_name, last_name, email))
                del df, email, file_path, first_name, index, last_name, row
            else:
                logging.error("File input type not yet supported")
        except KeyError as e:
            failure_detected(f"Error retrieving '{e.args[0]}' in file '{file_path}'")

    # Format data in proper output format
    logging.debug("Converting data to output format")
    user_data = list(user_data)
    output_data = {
        "user_list_size": len(user_data),
        "user_list": []
    }

    # Handle json format
    if output_file_path.lower().endswith('json'):
        for user in user_data:
            first_name, last_name, email = user
            output_data["user_list"].append({
                "first_name": first_name,
                "last_name": last_name,
                "email": email
            })
        with open(output_file_path, "w") as output_file:
            logging.debug(f"Writing data to 'json' formatted output file: {output_file_path}")
            output_file.write(dumps(output_data))
    else:
        failure_detected("File input type not yet supported")

    logging.debug("Data processing completed.")


def main():
    # Setup command line arguments
    arg_parser = argparse.ArgumentParser(description='Determining arguments to call correct function')
    arg_parser.add_argument("-o", "--output_file_path", dest="output_file_path", required=True,
                            help="Specify output file path - Ex. 'results.json'")
    arg_parser.add_argument("-i", "--input_file_path", action='append', dest="input_file_path", required=True,
                            help="Specify an input file path (csv). Multiple --input_file arguments can be specified.")

    # Retrieve command line arguments
    args = arg_parser.parse_args()

    # Setup Logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, filemode='w',
                        format='[%(asctime)s] - %(levelname)s - %(message)s')

    # Validate input file paths
    logging.debug("Validating input file paths.")
    input_file_paths = args.input_file_path
    for path in input_file_paths:
        detected_valid_file_type = list(filter(path.lower().endswith, VALID_INPUT_FORMATS)) != []
        if not detected_valid_file_type:
            failure_detected("Invalid input file type detected. Exiting.")

    # Validate output file path
    logging.debug("Validating output file path.")
    output_file_path = args.output_file_path
    detected_valid_file_type = list(filter(output_file_path.lower().endswith, VALID_OUTPUT_FORMATS)) != []
    if not detected_valid_file_type:
        failure_detected("Invalid output file type detected. Exiting.")

    process_user_data(input_file_paths=input_file_paths, output_file_path=output_file_path)


if __name__ == "__main__":
    main()
