#Python Snippets

## My common shebang and imports:

    #!/usr/bin/env python3

    import sys
    import os
    import glob
    import argparse
    import pandas as pd
    import send2trash
    import re
    import time


## Get arguements:

    def get_args():
        parser = argparse.ArgumentParser(description="This describes what your program does.")
        parser.add_argument("--input_xl", help="Semi-Optional: input excel file in .xlsx format containing information about the samples.", default="info.xlsx", required=False)
        parser.add_argument("--input_dir", help="Semi-Optional: input directory for all input files files.", default="Data", required=False)
        args = parser.parse_args()
        return args


## String formatting:

    def get_initials(string):
        xs = (string)
        words_list = xs.split()
        initials = ""
        for word in words_list:
            initials = initials + word[0].upper()
        return initials

    def get_capital(string):
        xs = (string)
        word_list = xs.split()
        words_num = len(word_list)
        words_return = ""
        for word in word_list:
            word_return = word[0].upper() + word[1:].lower()
            words_return = words_return + word_return + " "
        return words_return.strip() 


## text delimited formats:

    def import_tsv_as_dataframe(file_name):
        df = pd.read_csv(file_name, delimiter = "\t")
        df = df.rename(index=str)
        return df

## How to init a class:

    class Sample_Metadata:
        """A slice of an OTU table, and associated metadata for a diatom sample."""
        def __init__(self, sample_name, sample_id):
            self.name = sample_name
            self.id = sample_id

        def assign_results(self, otus, batch_num):
                self.otu_tab = otus
                try:
                    count = self.otu_tab[str(self.folder)].sum()
                    self.count = count
                except KeyError:
                    self.count = 0
                    print("Seq count for " + str(self.folder) + " has been set to 0.")
                if self.count >= 3000:
                    self.pass_fail = "Successful"
                if batch_num:
                    self.batch_num = str(batch_num).split(".")[0]
                    try:
                        date = batch_num_dict[self.batch_num]
                    except KeyError:
                        date = "Run metadata has not been set"
                        print(date + " for sample: " + str(self.folder) + " " + str(self.batch_num))
                    self.analysis_date = date
                else:
                    self.batch_num = no_value
                    self.analysis_date = no_value

## Other

    def delete_file(file_in):
        file_exists = os.path.isfile(file_in)
        if file_exists == True:
            send2trash.send2trash(file_in)
