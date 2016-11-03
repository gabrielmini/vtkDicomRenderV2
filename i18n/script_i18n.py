import json
import re
import os

# Perform a scan
BASE_DIR = os.path.dirname(os.getcwd())
word_dict = dict()
FILE_NAME = "words.json"
print "\n\tPerforming a scan. Base Directory:", BASE_DIR

# Walk in all files on root directory
print "\tWalking on base directory"
for root, dirs, files in os.walk(BASE_DIR):

    if root == os.getcwd():  # To avoid i18n directory
        continue

    for file_name in files:
        if file_name.split(".")[-1] == "py":  # Verifies if is a python file
            python_file = os.path.join(root, file_name)

            with open(python_file) as pf:
                # Find all items with a i18n string format _("... ...")
                terms_list = re.findall('_\("(.*?)"\)', pf.read())
                for item in terms_list:
                    # Save into a dictionary with a null value
                    word_dict[item] = None

print "\tSaving all terms in file: " + FILE_NAME
with open(FILE_NAME, "w") as jf:
    json.dump(word_dict, jf, indent=4)

print "\tFile saved successfully!"




