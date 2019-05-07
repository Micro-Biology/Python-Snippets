#Python Snippets

## My common shebang and imports:

    #!/usr/bin/env python3

    import sys
    import os
    import glob
    import argparse
    import pandas as pd
    import send2trash
    import shutil
    import subprocess
    import re
    import time


## Get arguments:

    def get_args():
        parser = argparse.ArgumentParser(description="This describes what your program does.")
        parser.add_argument("--input_xl", help="Semi-Optional: input excel file in .xlsx format containing information about the samples.", default="info.xlsx", required=False)
        parser.add_argument("--input_dir", help="Semi-Optional: input directory for all input files files.", default="Data", required=False)
        args = parser.parse_args()
        return args


## Importing data:

    def import_tsv_as_dataframe(file_name):
        df = pd.read_csv(file_name, delimiter = "\t")
        df = df.rename(index=str)
        return df

    def import_fastq_entries(fastq_file):
        inter = "inter.txt"
        delete_file(inter)
        file_interim = open(inter, "w")
        lines = get_lines(fastq_file)
        for line in lines:
            file_interim.write(line)
        file_interim.close()
        remove_empty_lines(inter)
        lines_all = get_lines(inter)
        os.remove(inter)
        fastq_entries = []
        for i in range(0, len(lines_all), 4):
            header = lines_all[i]
            seq = lines_all[i+1]
            qual = lines_all[i+3]
            read = Single_Fastq_Entry(header,seq,qual,fastq_file)
            fastq_entries.append(read)
        return fastq_entries

## How to init a class:

    class Sample_Metadata: #Listed from biosys.py
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

## Copy paste classes:
    
    class FormatError(Exception):
        '''Formating of an input file is incompatible with this program.'''
        pass

    class Single_Fastq_Entry:
        '''A class used to store information about paired end fastq data.'''
        def __init__(self,header,seq,qual,filename):
            self.tag = filename[18:26] #This will need changing depending on the format of the filename
            if header.lstrip()[0] == "@":
                self.header = header.lstrip()[0:45]
                self.header_full = header.lstrip()
            self.seq = seq.lstrip()
            self.qual = qual.lstrip()

    class Paired_Fastq_Entry:
        '''A class holding infor about a sample.'''
        def __init__(self,f_fastq,r_fastq):
            self.f = f_fastq
            self.r = r_fastq

    class Sample_Meta():
        '''A class used to store data about the QC process of the pipeline.'''
        def __init__(self, sample_id, file_path_f, file_path_r, file_format):
            self.sample_id = sample_id
            self.path_f = file_path_f
            self.path_r = file_path_r
            self.format = file_format
            path,file_name = os.path.split(self.path_f)
            self.directory = path
            self.stage = "start"

        def assign_progress(self, stage_passed, file_path_f, file_path_r):
            self.path_f = file_path_f
            self.path_r = file_path_r
            self.stage = stage_passed

## Subprocess examples:

    def run_cutadapt(sample_list, fprimer, rprimer, directory): 
        error_rate = get_highest_error_rate(fprimer, rprimer)
        print(fprimer, rprimer)
        print("Error rate = " + str(error_rate))
        for sample in sample_list:
            sampleid = str(sample.sample_id)
            cutadapt_command = ("cutadapt -j 0 --discard-untrimmed -e " + str(error_rate)
                                " -g fprimer=" + str(fprimer) + " -G rprimer=" + str(rprimer) 
                                " -o " + directory + "/" + sampleid + ".R1.trimmed.fastq.gz -p "
                                directory + "/" + sampleid + ".R2.trimmed.fastq.gz "
                                sample.path_f + " " + sample.path_r )
            cutadapt_child = subprocess.Popen(str(cutadapt_command), stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell=True)
            cutadapt_output,cutadapt_error = cutadapt_child.communicate()
            print(cutadapt_output,cutadapt_error)
            cutadapt_child.wait(timeout=None)
            if os.path.isfile(directory + "/" + sampleid + ".R1.trimmed.fastq.gz") == True:
                delete_file(sample.path_f)
                delete_file(sample.path_r)
                sample.assign_progress("cutadapt", (directory + "/" + sampleid + ".R1.trimmed.fastq.gz"), (directory + "/" + sampleid + ".R2.trimmed.fastq.gz"))
            else:
                print(sample.sample_id + " has failed cutadapt stage.")

## Others, will probably be needed:

    def get_lines(file_in):
        file_open = open(file_in)
        lines = file_open.readlines()
        file_open.close()
        return lines

    def delete_file(file_in):
        file_exists = os.path.isfile(file_in)
        if file_exists == True:
            send2trash.send2trash(file_in)

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
