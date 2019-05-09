#!/usr/bin/env python3

import os
import re
import sys
import send2trash
import time

#To do: implement this into the docker pipeline as an option

#inputs:
fasta_file = "repset.fasta"
taxonomy_file = "repset.taxonomy.txt"
mapping_file = "readyForQiime.allsamples_otus.txt"

#warning:
warning_message = "This program requires several files from the diatom qiime1 pipeline, as follows: \n* " + fasta_file + "\n* " + taxonomy_file + "\n* " + mapping_file + "\n \n Are these files in the current directory? (y/n)"

#Output:
out_file = "no_blast_hits_counts.csv"

class Fasta:
    """A basic method of storing sequences, 
       usually DNA across 2 lines. Each fasta 
       entry has an identifier (header), 
       stored on the first line and a sequence
       stored on the second line."""

    def __init__(self, header, dna):
        """Gives each fasta entry a header and dna 
           value, ensuring that they are formatted
           correctly."""
        try:
            if header[0] != ">":
                raise ValueError("Fasta header does not begin with a '>' character")
        except (ValueError):
            exit('''\nERROR: \n      Fasta header does not begin with a '>' character, are you sure this is a fasta file?\n''')
        self.header = header
        dna = dna.upper()
        try:
            dna_chars = r'[^ACGTRYSWKMBDHVN]'
            if re.search(dna_chars, dna):
                raise ValueError("Contains non-dna characters")
        except (ValueError):
            exit('''\nERROR: \n      DNA sequence conatins non-DNA characters, DNA can only contain 'ACGTRYSWKMBDHVN' characters. \n      (Lowercase characters are accepted but will be converted to uppercase.)\n''')
        self.dna = dna

    def len(self):
        """Returns the length of the DNA sequence."""
        length = len(self.dna)
        return length

    def perc_degen(self):
        bases = 0
        bases_degen = 0
        for base in self.dna:
            if base in "ACGT":
                bases = bases + 1
            else:
                bases_degen = bases_degen + 1
        perc_degen = (bases_degen / ( bases + bases_degen )) * 100
        return format(perc_degen, ".5f")

    def assign_abundance(self, num):
        if type(num) is int:
            self.abundance = num
        else:
            print("Abundance of sequence must be an interger")

def import_fasta_entries(file_name):
    inter = "inter.txt"
    delete_file(inter)
    file_interim = open(inter, "w")
    lines = get_lines(file_name)
    for line in lines:
        file_interim.write(line)
    file_interim.close()
    remove_empty_lines(inter)
    lines_all = get_lines(inter)
    os.remove(inter)
    fasta_entries = {}
    entry_num = 1
    for line_num in range(0, len(lines_all), 2):
        fasta_header_num = line_num
        fasta_header = lines_all[fasta_header_num]
        fasta_seq_num = line_num + 1
        fasta_seq = lines_all[fasta_seq_num]
        fasta_entry = Fasta(fasta_header.rstrip(), fasta_seq.rstrip())
        fasta_key = fasta_header.split()[0]
        fasta_entries[fasta_key[1:]] = fasta_entry
    return fasta_entries

#Generic

def remove_empty_lines(filename):
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()
    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)

def delete_file(file_in):
    file_exists = os.path.isfile(file_in)
    if file_exists == True:
        send2trash.send2trash(file_in)

def get_lines(file_in):
    file_open = open(file_in)
    lines = file_open.readlines()
    file_open.close()
    return lines

#Program specific

def get_id_counts(no_hit_ids, mapping_file):
    count_dict = {}
    with open(mapping_file, "r") as map_file:
        for line in map_file:
            line_list = line.split()
            repseq_id = line_list[0]
            num_seqs = len(line_list)
            if repseq_id in no_hit_ids:
                count_dict[repseq_id] = num_seqs
    return count_dict

def get_no_hit_ids(taxonomy_file):
    no_hit_ids = []
    with open(taxonomy_file, "r") as tax_file:
        for line in tax_file:
            line_list = line.split()
            id_denovo = line_list[0]
            taxonomy_1 = line_list[1]
            if taxonomy_1 == "No_blast_hit;":
                no_hit_ids.append(id_denovo)
    return no_hit_ids

def main():
    answer = input(warning_message)
    if answer[0] == "y":
        pass
    else:
        print("Add the required files to the current directory.")
        time.sleep(30)
        exit
    print("Identifying all otus with no blast hits...")
    no_hit_ids = get_no_hit_ids(taxonomy_file)
    print("\tNumber of otus with no blast hit: " + str(len(no_hit_ids)))
    print("Calculating number of sequences seach no blast hit otu has...")
    count_dict = get_id_counts(no_hit_ids, mapping_file)
    print("Getting a repseqs...")
    fasta_all = import_fasta_entries(fasta_file)
    output = open(out_file, "w")
    for key in count_dict.keys():
        fasta_obj = fasta_all[key]
        fasta_obj.assign_abundance(count_dict[key])
        output.write(fasta_obj.header + "," + fasta_obj.dna + "," + str(fasta_obj.abundance) + "\n")
    output.close()
    

main()


