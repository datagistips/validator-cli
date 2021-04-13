# -*- coding: utf-8 -*-

import geopandas as gpd
import pandas as pd
from re import match, search
import os
import sys
import csv
import argparse
from datetime import datetime
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from ast import literal_eval
import numpy as np
import typer
from typing import Optional
from src.functions import *

app = typer.Typer()
console = Console()

global mapping


def process_control(input_data, input_mapping):

    # Read Data
    data = read_data(input_data)
    standard = pd.read_csv(input_mapping)

    # HEADER ###########################

    print("Time : %s" % now_string)

    data_columns = [elt for elt in list(data.columns) if elt != "geometry"]
    schema_columns = list(standard["name"])

    # GET FIELDS REPORT ####################

    d = get_fields_report(data, standard)

    # PRINT SUMMARY ######################

    MARKDOWN = (
        """
# %s
"""
        % input_mapping
    )
    md = Markdown(MARKDOWN)
    console.print(md)

    for elt in schema_columns:
        to_type = get_type_of_var(standard, elt)
        if elt not in d.keys():
            print("[yellow]%s (%s) *NOT FOUND IN DATA*[/yellow]" % (elt, to_type))
        else:
            d2 = d[elt]
            if any([elt[0] is False for elt in d2.values()]):
                print("[red]%s (%s) *NOT VALID*[/red]" % (elt, to_type))
            else:
                print("[green]%s (%s) *OK*[/green]" % (elt, to_type))

    print("")

    # PRINT DETAILS ON DATA #######################

    MARKDOWN = (
        """
# %s
"""
        % input_data
    )
    md = Markdown(MARKDOWN)
    console.print(md)

    for key, value in d.items():
        if key not in schema_columns:
            print("[yellow]%s *NOT FOUND IN SCHEMA*[/yellow]" % key)
        else:
            from_type = data[key].dtype
            if all([elt[0] is True for elt in value.values()]):
                print("[green]%s (%s) *OK*[/green]" % (key, from_type))
            else:
                for key2, value2 in value.items():
                    if value2[0] is False:
                        print(
                            "[red]%s (%s) *NOT VALID*: %s[/red]"
                            % (key, from_type, value2[1])
                        )
        # ~ print('')


def process_transform(input_data, input_mapping, output_data=None):

    # READ DATA ###############################################

    data = read_data(input_data)
    mapping = pd.read_csv(input_mapping)

    p = pathlib.Path(input_data)
    input_name = p.parents[0].joinpath(p.stem)
    input_extension = p.suffix

    if input_extension in ("shp", "gpkg"):
        file_class = "df"
    else:
        file_class = "geo"

    # CONTROL ###################################################

    strange_cols = list()
    for elt in list(list(mapping["from"])):
        if elt not in list(data.columns):
            if (elt != "fid" and file_class == "geo") or (file_class == "df"):
                strange_cols.append(elt)

    if len(strange_cols) > 0:
        MARKDOWN = (
            """
# Input data : %s
"""
            % input_data
        )
        md = Markdown(MARKDOWN)
        console.print(md)
        # ~ print(('> Input data : %s')%(input_data))
        print(
            "[red]Wrong structure. No mapping done. Source mapping columns %s not found in data[/red]"
            % (", ".join(strange_cols))
        )
        print("")
        return ()

    # PARAMETERS ################################################

    if output_data is None:
        output_data = str(input_name) + "-mapped" + str(input_extension)
    else:
        output_data_path = output_data

    # RENAME ################################

    d = dict(zip(mapping["from"], mapping["to"]))
    data2 = data.rename(index=str, columns=d)

    # EXPORT #################################

    if input_extension == ".csv":
        data2.to_csv(output_data, encoding="utf-8", index=False, quoting=csv.QUOTE_ALL)
    elif input_extension == ".gpkg":
        data2.to_file(output_data, driver="GPKG", encoding="utf-8", index=False)
    elif input_extension == ".shp":
        data2.to_file(
            output_data, driver="ESRI Shapefile", encoding="utf-8", index=False
        )

    # MESSAGES ################################################

    MARKDOWN = (
        """
# Input data : %s
"""
        % input_data
    )
    md = Markdown(MARKDOWN)
    console.print(md)
    print(
        data.iloc[
            range(5),
        ]
    )
    print("")

    MARKDOWN = (
        """
# Mapping file : %s
"""
        % input_mapping
    )
    md = Markdown(MARKDOWN)
    console.print(md)
    print(mapping)
    print("")

    MARKDOWN = (
        """
# Output data : %s
"""
        % output_data
    )
    md = Markdown(MARKDOWN)
    console.print(md)
    print(
        data2.iloc[
            range(5),
        ]
    )
    print("")
    

@app.command()
def control(inputfile: str, schemafile:str, directory: bool = False):
    """
inputfile : input file path or directory (depends if you specified --directory)

schemafile : data schema file path

--directory : type --directory if you want to control an entire directory	
    """
    
	# Check existence
    if not os.path.exists(schemafile):
        print(("ERROR : mapping file '%s' doesn't exist") % schemafile)
        quit()

    if not os.path.exists(inputfile):
        print(("ERROR : file '%s' doesn't exist") % inputfile)
        quit()

	# Single file treatment -----
    if directory is False:
	    process_control(
		    inputfile, schemafile
	    )  # we'll create and output data name based on input data file name

	# Directory treatment -----
    else :
	    inputdir = inputfile
	    l = os.listdir(inputdir)
	    for elt in l:
		    process_control(os.path.join(inputdir, elt), schemafile)


@app.command()
def transform(inputfile: str, mappingfile:str, directory: bool = False, outputdata: Optional[str] = None):
	"""
inputfile : input file path or directory (depends if you specified --directory)

mappingfile : data mapping file path. The data mapping file specifies source field and target field names.

--directory : type --directory if you want to control an entire directory	
    """
	
	# Single file treatment -----
	if directory is False:

		if outputdata is not None:
			print(now_string)
			process_transform(
				inputfile, mappingfile, outputdata
			)  # we use the output data file name
		else:
			print(now_string)
			process_transform(
				inputfile, mappingfile
			)  # we'll create and output data name based on input data file name

	# Directory treatment -----
	else :
		inputdir = inputfile

		if outputdata is not None:
			print(
				"Output file will not be taken into account when renaming batches of data"
			)

		print(now_string)
		l = os.listdir(inputfile)
		for elt in l:
			process_transform(os.path.join(inputfile, elt), mappingfile)


if __name__ == "__main__":

    now = datetime.now()
    now_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    app()

    # ARGUMENTS ##############################################

    # ~ parser = argparse.ArgumentParser()

    # ~ parser.add_argument(
        # ~ "mode",
        # ~ choices=["control", "transform"],
        # ~ help="'control' data against a data schema or 'transform' data thanks to a mapping file",
    # ~ )
    # ~ parser.add_argument(
        # ~ "-d", "--directory", help="process entire directory", action="store_true"
    # ~ )
    # ~ parser.add_argument(
        # ~ "input", help="input file or directory (depends if you specified -d or not)"
    # ~ )
    # ~ parser.add_argument(
        # ~ "schema",
        # ~ help="data schema file path (if 'control' mode) or mapping file (if 'transform' mode)",
    # ~ )
    # ~ parser.add_argument("-o", "--output", help="Output file (Optional and active if in single file mode, not directory mode)")

    # ~ args = parser.parse_args()

    # ~ mode = args.mode
    # ~ directory = args.directory
    # ~ input_data = inputfile
    # ~ input_mapping = schemafile
    # ~ output_data = args.output
    # ~ output_data = None

    # READ ####################################################

    
    
