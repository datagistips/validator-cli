# -*- coding: iso-8859-1 -*-

import geopandas as gpd
import pandas as pd
import math
import re
import os
import sys
import json
import argparse
import csv
from datetime import datetime
from rich import print
from rich.console import Console
from rich.markdown import Markdown
import ast

MARKDOWN = """
# This is an h1

Rich can do a pretty *decent* job of rendering markdown.

1. This is a list item
2. This is another list item
"""

console = Console()
md = Markdown(MARKDOWN)

global mapping

def matches_regexp(df_var, regexp):
    """
            matches_regexp a column against a regexp

            >>> df_var
    0    a1
    1    a2
    2    a3

    >>> regexp
    'a[0-9]'

    > True

    """

    i_not_valid = [
        i
        for i, elt in enumerate([bool(re.match(regexp, elt)) for elt in list(df_var)])
        if elt is False
    ]

    v = [list(df_var)[i] for i in i_not_valid]
    # ~ print(v)
    if len(v) > 0:
        return (False, v)
    else:
        return True


def matches_enum(df_var, l):
    """"""

    v = [elt for elt in list(df_var) if elt not in l]
    # ~ print(v)
    if len(v) > 0:
        return (False, v)
    else:
        return True


def control_date(date_text):
    try:
        res = datetime.strptime(date_text, "%Y-%m-%d")  # ISO 8601
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_date_alt1(date_text):
    try:
        res = datetime.strptime(date_text, "%d-%m-%Y")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_date_alt2(date_text):
    try:
        res = datetime.strptime(date_text, "%y-%m-%d")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_datetime(datetime_text):
    try:
        res = datetime.strptime(datetime_text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_time(time_ext):
    try:
        res = datetime.strptime(time_ext, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res

def get_pattern_of_var(standard, the_var):
    """
    """

    res = standard[standard.iloc[:, 0] == the_var]["pattern"].item()
    res = None if res == '' else res
    return res


def get_type_of_var(standard, the_var):
    """
    >>> get_type_of_var(standard, "id_site")
    'integer'
    """

    res = standard[standard.iloc[:, 0] == the_var]["type"].item()
    return res


def get_enum_of_var(standard, the_var):
	
	l = standard[standard.iloc[:, 0] == the_var]["enum"].item()
	l = None if l == '' else l
	if l is not None:
		res = ast.literal_eval(l)
	else:
		res = None
	return res

# Compare
def is_ok(data_var, to_type):
    """
	> data_var
	0    a
	1    b
	2    c
	Name: str, dtype: object

	> to_type
	character

	>> True
    """

    # ~ print("----")
    # ~ print(data_var)
    # ~ print(to_type)

    # ~ print("> type d'origine : ", data_var.dtype)
    # ~ print("> type de destination : ", to_type)

    if to_type in ("character", "text", "string"):
        if data_var.dtype == "object":
            return True
        else:
            return False

    elif to_type == "integer":
        if data_var.dtype == "int64":
            return True
        elif data_var.dtype == "float64":
            return (False, "[ERROR] Float type found", None)
        elif data_var.dtype == "object":
            v = [bool(re.match("\d", str(elt))) for elt in list(data_var)]
            i_not_valid = [i for i, elt in enumerate(v) if elt is False]
            if len(i_not_valid) > 0:
                print("toto >", i_not_valid)
                elts_not_valid = [list(data_var)[i] for i in i_not_valid]
                print(elts_not_valid)
                return (False, "[ERROR] String characters found", elts_not_valid[1:5])
            else:
                return (True, "[WARNING] Object type found", None)
        else:
            return (False, "[ERROR] Wrong type found", None)

    elif to_type in ("float", "number"):
        if data_var.dtype == "float64":
            return True
        elif data_var.dtype == "int64":
            return (True, "[WARNING] Integer type found", None)
        elif data_var.dtype == "object":
            v = [
                bool(re.match("(\d+\.?\d+)|(\d+\,?\d+)", str(elt))) for elt in data_var
            ]
            i_not_valid = [i for i, elt in enumerate(v) if elt is False]
            if len(i_not_valid) > 0:
                v = [
                    bool(re.match("(\d+\.?\d?)|(\d+\,?\d?)", str(elt)))
                    for elt in data_var
                ]
                i_not_valid = [i for i, elt in enumerate(v) if elt is False]
                if len(i_not_valid) > 0:
                    elts_not_valid = [list(data_var)[i] for i in i_not_valid]
                    return (False, "[ERROR] No float types found", elts_not_valid[1:5])
                else:
                    return (True, "[WARNING] Integer type found", None)
            else:
                return True
        else:
            return (False, "[ERROR] Wrong type found", None)

    elif to_type == "boolean":
        if data_var.dtype == "bool":
            return True
        elif data_var.dtype == "int64":
            unique_values = list(set(data_var))
            if unique_values == [0, 1] or unique_values in (0, 1):
                return True
            else:
                return (
                    False,
                    "[ERROR] Integer values not in range",
                    unique_values[1:5],
                )
        elif data_var.dtype == "object":

            # Boolean valid values
            ref_bool1 = [["0", "1"], ["O"], ["1"]]
            ref_bool2 = [["FALSE", "TRUE"], ["TRUE"], ["FALSE"]]
            ref_bool3 = [["False", "True"], ["True"], ["False"]]

            # Unique values
            unique_values = sorted(list(set(data_var)))
            print(unique_values)
            if (
                unique_values in ref_bool1
                or unique_values in ref_bool2
                or unique_values in ref_bool3
            ):
                return True
            elif all(
                [
                    elt in ["0", "1", "TRUE", "FALSE", "True", "False"]
                    for elt in unique_values
                ]
            ):
                return (False, "[ERROR] Mix of values", None)
            else:
                return (False, "[ERROR] Wrong values", None)
        else:
            return False

    elif to_type == "date":
        print("ok")
        if data_var.dtype == "datetime64":
            print("ok")
        elif data_var.dtype == "object":

            if all([control_date(elt) is not None for elt in data_var]):
                return True
            elif all([control_date_alt1(elt) is not None for elt in data_var]):
                return (False, "[ERROR] Day, month and year in wrong order", None)
            elif all([control_date_alt2(elt) is not None for elt in data_var]):
                return (False, "[ERROR] Years too short", None)
            elif all(
                [
                    bool(re.match("[0-9]+-[0-9]+-[0-9]+", elt)) is True
                    for elt in data_var
                ]
            ):
                return (False, "[ERROR] Days not in range", None)
            elif all(
                [
                    bool(re.match("[0-9]+/[0-9]+/[0-9]+", elt)) is True
                    for elt in data_var
                ]
            ):
                return (False, "[ERROR] Not well formatted. Folllow ISO8601", None)
            else:
                return (False, "[ERROR] Dates not valid", None)

    elif to_type == "datetime":
        if data_var.dtype == "datetime64":
            return True
        elif data_var.dtype == "object":
            elts_not_valid = [
                elt
                for elt in [control_datetime(elt) for elt in data_var]
                if elt is None
            ]
            n_not_valid = len(elts_not_valid)
            if n_not_valid > 0:
                print((False, "[ERROR] Wrong datetime", None))
            else:
                return True
        else:
            return (False, "[ERROR] Wrong type", None)

    elif to_type == "time":
        if data_var.dtype == "datetime64":
            return True
        elif data_var.dtype == "object":
            elts_not_valid = [
                elt for elt in [control_time(elt) for elt in data_var] if elt is None
            ]
            n_not_valid = len(elts_not_valid)
            if n_not_valid > 0:
                return (False, "[ERROR] Wrong time", None)
            else:
                return True
        else:
            return (False, "[ERROR] Wrong type", None)


def read_data(input_data):
	
	# !! https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups
	input_name = re.search('(.*)\\.(.*)', input_data).group(1)
	input_extension = re.search('(.*)\\.(.*)', input_data).group(2)
	
	if input_extension == 'csv':
		file_class = "df"
		data = pd.read_csv(input_data, encoding = 'utf-8')
	else:
		file_class = "geo"
		data = gpd.read_file(input_data, encoding = 'utf-8')
			
	return(data)


def control(input_data, input_mapping):
	
	# Read Data
	data = read_data(input_data)
	mapping  = pd.read_csv(input_mapping) # ! spécifier le type avec dtype
	
	# Foo Data
	data = pd.DataFrame(data = {
	'id_site':[1,2,3], 
	'foo1':['a', 'b', 'c'], 
	'pattern':['a1', 'a2', 'a3'],
	'list_values':['a', 'b', 'd']
	})
	mapping = pd.DataFrame(data = {
	'fields':['id_site', 'pattern', 'list_values'], 
	'type':['integer', 'character', 'character'], 
	'pattern':['', 'b[0-9]', ''],
	'enum':['','','["a", "b", "c"]']
	})
	
	# Columns
	data_columns = list(data.columns)
	schema_columns = list(mapping.iloc[:,0])
	
	
	# PRESENCE OF FIELDS ###########################
	
	MARKDOWN = """
	PRESENCE OF FIELDS
	"""
	
	md = Markdown(MARKDOWN)
	console.print(md)
	
	print("[bold blue]PRESENCE[/bold blue]")
	
	print(now_string)
	
	# Data columns absent from schema
	strange_cols1 = list()
	matching_cols1 = list()
	# !! utiliser set plutôt et diff
	for elt in data_columns:
		if elt not in schema_columns:
			strange_cols1.append(elt)
			print('[red]%s absent from schema[/red]'%elt)
		else:
			matching_cols1.append(elt)
	
	# Schema columns absent from data
	strange_cols2 = list()
	matching_cols2 = list()
	for elt in schema_columns:
		if elt not in data_columns:
			strange_cols2.append(elt)
			print('[red]%s absent from data[/red]'%elt)
		else:
			matching_cols2.append(elt)
	
	# valid or not ?
	# ~ if len(matching_cols1) > 0:
		# ~ conform = False
		# ~ pc = len(matching_cols1) / data.shape[0]
	# ~ else:
		# ~ conform = True
	
	# Messages
	# ! format, fstring, reach
	# ~ print(now_string)
	# ~ print('[KO] Data non valid' if conform is False else '[OK] Data valid')
	# ~ print('')
	# ~ print('Input data : %s'%input_data)
	# ~ print('Data schema : %s'%input_mapping)
	# ~ print('')
	# ~ print(('Data columns : %s')%(', '.join(data_columns)))
	# ~ print(('Schema columns : %s')%(', '.join(schema_columns)))
	# ~ print('')
	# ~ print(('Data columns present in schema : %s')%(', '.join(matching_cols1)))
	# ~ print(('Data columns absent from schema : %s')%(', '.join(strange_cols1)))
	# ~ print('')
	# ~ print(('Schema columns present in data : %s')%(', '.join(matching_cols2)))
	# ~ print(('Schema columns absent from data : %s')%(', '.join(strange_cols2)))
	
	
	# TYPE OF FIELDS ###########################
	
	print("")
	print("[bold blue]TYPES[/bold blue]")
	
	for elt in data_columns:
		if elt in schema_columns:
			print(elt, is_ok(data[elt], get_type_of_var(mapping, elt)))
			
	# PATTERNS ###########################
	
	print("")
	print("[bold blue]PATTERNS[/bold blue]")
	
	for elt in data_columns:
		if elt in schema_columns:
			patt = get_pattern_of_var(mapping, elt)
			if patt is not None:
				res = matches_regexp(data[elt], get_pattern_of_var(mapping, elt))
				if res[0] is False:
					print('[red]%s : %s do not match pattern %s[/red]'%(elt, ','.join(res[1]), patt))
			
	# ENUMS ###########################
	
	print("")
	print("[bold blue]ENUMS[/bold blue]")
	
	for elt in data_columns:
		if elt in schema_columns:
			print(elt)
			enums = get_enum_of_var(mapping, elt)
			if enums is not None:
				print(enums)
				res = matches_enum(data[elt], enums)
				if res[0] is False:
					print("[red]%s : '%s' do not match list of possible values %s[/red]"%(elt, ','.join(res[1]), ','.join(enums)))


def transform(input_data, input_mapping, output_data = None):
	
	
	# READ DATA ###############################################
	
	data = read_data(input_data)
	mapping  = pd.read_csv(input_mapping)
	
	input_name = re.search('(.*)\\.(.*)', input_data).group(1)
	input_extension = re.search('(.*)\\.(.*)', input_data).group(2)
	
		
	# CONTROL ###################################################
	
	strange_cols = list()
	for elt in list(list(mapping.iloc[:,0])):
		if elt not in list(data.columns):
			if (elt != 'fid' and file_class == "geo") or (file_class == "df") :
				strange_cols.append(elt)
				
	if len(strange_cols) > 0:
		print(('> Input data : %s')%(input_data))
		print('WARNING : Wrong structure. No mapping done. Odd columns : %s'%(', '.join(strange_cols)))
		return()
	
	
	# PARAMETERS ################################################
	
	if output_data is None:
		output_data = input_name + '-mapped.' + input_extension
	else:
		output_data_path = output_data
	
	
	# RENAME ################################
	
	d = dict(zip(mapping['from'], mapping['to']))
	data2 = data.rename(index=str, columns=d)
	
	
	# EXPORT #################################
	
	if input_extension == "csv":
		data2.to_csv(output_data, encoding = "utf-8", index = False, quoting=csv.QUOTE_ALL)
	elif input_extension == 'gpkg':
		data2.to_file(output_data, driver="GPKG", encoding = "utf-8", index = False)
	elif input_extension == 'shp':
		data2.to_file(output_data, driver="ESRI Shapefile", encoding = "utf-8", index = False)
	
	
	# MESSAGES ################################################
	
	print(now_string)
	print(('Input data : %s')%(input_data))
	print(data.iloc[range(5),])
	print('\n')
	print(('Mapping file : %s')%(input_mapping))
	print(mapping)
	print('\n')
	print(('Mapped data : %s')%(output_data))
	print(data2.iloc[range(5), ])


if __name__ == "__main__":
	
	now = datetime.now()
	now_string = now.strftime("%d/%m/%Y %H:%M:%S")
	
	# ARGUMENTS ##############################################
	
	parser = argparse.ArgumentParser()
	
	parser.add_argument("mode", choices=['control', 'transform'], help="'control' data against a data schema or 'transform' data thanks to a mapping file")
	parser.add_argument("-d", "--directory", help="process entire directory", action="store_true")
	parser.add_argument("input", help="input file or directory (depends if you specified -d or not)")
	parser.add_argument("schema", help="data schema file path (if 'control' mode) or mapping file (if 'transform' mode)")
	# ~ parser.add_argument("-o", "--output", help="Output file (Optional and active if in single file mode, not directory mode)")


	args = parser.parse_args()
	
	mode = args.mode
	directory = args.directory
	input_data = args.input
	input_mapping = args.schema
	# ~ output_data = args.output
	output_data = None
	
	# READ ####################################################
	
	# Read mapping
	if not os.path.exists(input_mapping):
		print(("ERROR : mapping file '%s' doesn't exist")%input_mapping)
		quit()
		
	# CONTROL ########################################################"
	if not os.path.exists(input_data):
		print(("ERROR : file '%s' doesn't exist")%input_data)
		quit()

	
	# PROCESS ####################################################
	
	# Transform
	
	if mode == "control":
		
		# Single file treatment -----
		if directory is False :
			control(input_data, input_mapping) # we'll create and output data name based on input data file name
		
		# Directory treatment -----
		elif directory is True:			
				
			l = os.listdir(input_data)
			for elt in l:
				control(os.path.join(input_data, elt), input_mapping)
				print('-----------------------------------------------------------------------------------')
				
	elif mode == "transform":
		
		# Single file treatment -----
		if directory is False :
			
			if output_data is not None:
				transform(input_data, input_mapping, output_data) # we use the output data file name
			else:
				transform(input_data, input_mapping) # we'll create and output data name based on input data file name
		
		# Directory treatment -----
		elif directory is True:
			
			if output_data is not None:
				print("Output file will not be taken into account when renaming batches of data")
				
			l = os.listdir(input_data)
			for elt in l:
				transform(os.path.join(input_data, elt), input_mapping)
				print('-----------------------------------------------------------------------------------')
