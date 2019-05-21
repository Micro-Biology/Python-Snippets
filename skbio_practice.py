#!/usr/bin/env python3

import os
import argparse
import pandas as pd
from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa
from skbio.stats.distance import anosim
import matplotlib.pyplot as plt
import warnings

#How to use:

#Standalone: 
#       navigate '/media/nls/Storage/HomeBU/Python/skbio' in teminal
#       put transposed otu table in Data folder
#       run 'py37' to activate python environment
#       run 'python ./biodivEA.py --frac <fraction> --input_xl otus_all.xlsx

def make_pcoa(dist_mat, sample_meta, distance):
    fig = pcoa(dist_mat).plot(sample_meta, "type",
        axis_labels=("PC 1", "PC 2", "PC3"),
        title="Samples coloured by type, distance = " + distance, cmap="jet", s=10)
    return fig

def assign_meta(otu_tab):
    samples = list(otu_tab.index)
    sample_metadata = []
    for sample in samples:
        first_char = str(sample)[0].lower()
        if first_char == "b":
            meta = (sample, ["blank", "control"])
        elif first_char == "p":
            meta = (sample, ["positive", "control"])
        elif first_char == "n":
            meta = (sample, ["ntc", "control"])
        elif first_char == "t":
            meta = (sample, ["technical replicate", "control"])
        elif first_char == "g":
            meta = (sample, ["gblock", "control"])
        elif str(sample)[0] == "4":
            meta = (sample, ["sample", "EA"])
        elif str(sample)[0] == "3":
            meta = (sample, ["sample", "SEPA"])
        else:
            meta = (sample, ["unknown", "unknown"])
        try:
            sample_metadata.append(meta)
        except UnboundLocalError:
            print("Meta for " + str(sample) + " was not be added.")
    return pd.DataFrame.from_dict(
        dict(sample_metadata), columns=["type", "area"], orient="index")

def import_otu_table(inputxl, directory, fraction):
    dir_abspath = os.path.abspath(directory)
    xl_abspath = os.path.join(directory, inputxl)
    print("OTU input file: " + xl_abspath)
    print("Fraction of subsample: " + str(fraction))
    xl = pd.ExcelFile(xl_abspath)
    otu_tab = xl.parse(sheet_name=0, index_col=0)
    otu_sub_sample = otu_tab.sample(frac=float(fraction))
    return otu_sub_sample

def get_args():
    parser = argparse.ArgumentParser(description="Processes diatom data into regions.")
    parser.add_argument("--input_xl", help="Semi-Optional: input excel file in .xlsx format.", default="otus_all.xlsx", required=False)
    parser.add_argument("--input_dir", help="Semi-Optional: input directory for all input files files.", default="Data", required=False)
    parser.add_argument("--frac", help="Semi-Optional: Fraction of total samples to use for analysis, must be a float.", default="1.0", required=False)
    args = parser.parse_args()
    return args




def plot_data_from_otu(options):
    distance = "braycurtis"
    otu_tab = import_otu_table(options.input_xl, options.input_dir, options.frac)
    bc_dm = beta_diversity(distance, otu_tab.values, list(otu_tab.index))
    sample_meta = assign_meta(otu_tab)
    results = anosim(bc_dm, sample_meta, column="type", permutations=999)
    print(results)
    bc_pcoa = make_pcoa(bc_dm, sample_meta, distance)
    plt.show()



if __name__ == '__main__':
    options = get_args()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plot_data_from_otu(options)
    
