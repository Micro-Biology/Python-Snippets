
import sys
import os
import glob
import argparse
import pandas as pd
import send2trash
import re
import time


def save_relevant_identifier(df, identifier):
    ids_to_remove = ["StrainID","TaxonID","NBSCode","PrefTaxon"]
    ids_to_remove.remove(identifier)
    headers_all = df.columns.values.tolist()
    for i in ids_to_remove:
        headers_all.remove(i)
    df = df[headers_all]
    df = df.set_index(list(df)[0])
    df = df.loc[(df!=0).any(axis=1)]
    print(df.head(30))
    df.to_csv((identifier + "_OTU_Final.tsv"), sep="\t")

def import_database(xl_file):
    print("Importing database" + xl_file)
    xl = pd.ExcelFile(xl_file)
    sheet_names = xl.sheet_names

    #Import strainid_taxonid_sheet
    strainid_taxonid_sheet = xl.parse(sheet_name=sheet_names[1])
    strainid_taxonid_sheet = strainid_taxonid_sheet[["StrainID", "TaxonID"]]

    #Import taxonid_nbscode_sheet
    taxonid_nbscode_sheet = xl.parse(sheet_name=sheet_names[3])
    taxonid_nbscode_sheet = taxonid_nbscode_sheet[["TaxonId", "NBSCode"]]
    taxonid_nbscode_sheet = taxonid_nbscode_sheet.rename(columns={"TaxonId":"TaxonID"})

    #Import nbscode_preftaxon_sheet
    nbscode_preftaxon_sheet = xl.parse(sheet_name=sheet_names[2])
    nbscode_preftaxon_sheet = nbscode_preftaxon_sheet.rename(columns={"PREFERRED_TAXON_NAME":"PrefTaxon", "BIOSYS_TLIK (corresponds to NBS code)": "NBSCode"})
    nbscode_preftaxon_sheet = nbscode_preftaxon_sheet[["NBSCode", "PrefTaxon"]]

    #Merge
    main_df = pd.merge(strainid_taxonid_sheet, taxonid_nbscode_sheet, on="TaxonID")
    main_df = pd.merge(main_df, nbscode_preftaxon_sheet, on="NBSCode")
    return main_df

def get_args():
    parser = argparse.ArgumentParser(description="Assigns correct taxonomy identifier wanted.")
    parser.add_argument("--database", help="Semi-Optional: input database file in .xlsx format from Tim, if any changes to the format are changed this script will also need to be changed.", default="DarleqTaxonListMaster.xlsx", required=False)
    parser.add_argument("--otu", help="Semi-Optional: input otu table from pipeline", default="StrainID_OTU_Table.tsv", required=False)
    parser.add_argument("--input_dir", help="Semi-Optional: input directory for all input files files.", default="Data", required=False)
    parser.add_argument("--taxon", help="Semi-Optional:Taxonomy identifer to keep, must be StrainID, TaxonID, NBSCode, or PrefTaxon. Must also be spelt correctly", default="PrefTaxon", required=False)
    args = parser.parse_args()
    return args


def main():
    options = get_args()
    database = import_database(options.database)
    otus = pd.read_csv(options.otu, delimiter = "\t", skiprows=1)
    otus = otus.rename(columns={"#OTU ID":"StrainID"})
    main_df = pd.merge(database, otus, on="StrainID")
    save_relevant_identifier(main_df, options.taxon)


main()
