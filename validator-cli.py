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
import numpy as np

console = Console()

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

    res = standard[standard['name'] == the_var]["pattern"].item()
    res = None if res == '' else res
    return res


def get_type_of_var(standard, the_var):
    """
    >>> get_type_of_var(standard, "id_site")
    'integer'
    """

    res = standard[standard['name'] == the_var]["type"].item()
    return res


def get_enum_of_var(standard, the_var):
	
	l = standard[standard['name'] == the_var]["enum"].item()
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
            return (False, "Float type found", None)
        elif data_var.dtype == "object":
            v = [bool(re.match("\d", str(elt))) for elt in list(data_var)]
            i_not_valid = [i for i, elt in enumerate(v) if elt is False]
            if len(i_not_valid) > 0:
                elts_not_valid = [list(data_var)[i] for i in i_not_valid]
                return (False, "String characters found", elts_not_valid[1:5])
            else:
                return (True)
        else:
            return (False)

    elif to_type in ("float", "number"):
        if data_var.dtype == "float64":
            return (True)
        elif data_var.dtype == "int64":
            return (True, "Integer type found", None)
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
                    return (False, "No float types found", elts_not_valid[1:5])
                else:
                    return (True, "Integer type found", None)
            else:
                return True
        else:
            return (False)

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
                    "Integer values not equal to 0 or 1",
                    unique_values[1:5],
                )
        elif data_var.dtype == "object":

            data_var = data_var.astype('str')
            
            # Boolean valid values
            ref_bool1 = [["0", "1"], ["O"], ["1"]]
            ref_bool2 = [["FALSE", "TRUE"], ["TRUE"], ["FALSE"]]
            ref_bool3 = [["False", "True"], ["True"], ["False"]]

            # Unique values
            unique_values = sorted(list(set(data_var)))
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
                return (False, "Mix of boolean values, for instance TRUE, True, 0 and FALSE at the same time", None)
            else:
                return (False, "Wrong values", None)
        else:
            return False

    elif to_type == "date":
        if data_var.dtype == "datetime64":
            return(True)
        elif data_var.dtype == "object":

            if all([control_date(elt) is not None for elt in data_var]):
                return True
            elif all([control_date_alt1(elt) is not None for elt in data_var]):
                return (False, "Day, month and year in wrong order. Follow ISO-8601 : apply 2021-04-01", None)
            elif all([control_date_alt2(elt) is not None for elt in data_var]):
                return (False, "Years too short. Follow ISO-8601 : apply 2021-04-01", None)
            elif all(
                [
                    bool(re.match("[0-9]+-[0-9]+-[0-9]+", elt)) is True
                    for elt in data_var
                ]
            ):
                return (False, "Day(s) not in range", None)
            elif all(
                [
                    bool(re.match("[0-9]+/[0-9]+/[0-9]+", elt)) is True
                    for elt in data_var
                ]
            ):
                return (False, "Not well formatted. Follow ISO-8601 : apply 2021-04-01", None)
            else:
                return (False, "Dates not valid. Follow ISO-8601 : apply 2021-04-01", None)

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
                return (False, "Wrong datetime", None)
            else:
                return True
        else:
            return (False)

    elif to_type == "time":
        if data_var.dtype == "datetime64":
            return True
        elif data_var.dtype == "object":
            elts_not_valid = [
                elt for elt in [control_time(elt) for elt in data_var] if elt is None
            ]
            n_not_valid = len(elts_not_valid)
            if n_not_valid > 0:
                return (False, "Wrong time", None)
            else:
                return True
        else:
            return (False)


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
	standard  = pd.read_csv(input_mapping) # ! spécifier le type avec dtype
	
	# Foo Data
	data = pd.DataFrame(data = {
	'id_site':[1,2,3], 
	'foo1':['a', 'b', 'c'],
	'foo2':['a', 'b', 'c'], 
	'pattern':['b1', 'a2', 'a3'],
	'list_values':['a', 'b', 'd'],
	'date1':['2020-03-20', '2020-03-21', '2020-03-19'],
	'date2':['2020-03-33', '2020-03-21', '2020-03-19'],
	'date3':['21-01-2020', '21-01-2020', '21-01-2020'],
	'ok1':[0, 1, 0],
	'ok2':['TRUE', 'FALSE', 'TRUE'],
	'ok3':['FALSE', False, True],
	'ok4':[0, 1, 2],
	'insee1' : ["5001", "75056", "751144"],
	'siret1':["802954785000", "8029547850001899", "80295478500029"]

	})
	
	standard = pd.DataFrame(data = {
	'name':['id_site', 'pattern', 'list_values', 'foo3', 'foo2', 'date1', 'date2', 'date3', 'ok1', 'ok2', 'ok3', 'ok4', 'insee1', 'siret1'], 
	'type':['integer', 'character', 'character', 'character', 'integer', 'date', 'date', 'date', 'boolean','boolean','boolean','boolean', 'character', 'character'], 
	'pattern':['', 'b[0-9]', '', '', '', '', '', '','','','','','^([013-9]\d|2[AB1-9])\d{3}$', '^\d{14}$'],
	'enum':['','','["a", "b", "c"]', '', '', '', '', '','','','','','','']
	})
	
	standard.astype({'name': 'object', 'type':'object', 'pattern':'object', 'enum':'object'}).dtypes
	
	# Columns
	data_columns = list(data.columns)
	schema_columns = list(standard["name"])
	
	# HEADER ###########################
	
	print(now_string)
	print('')
	
	
	# SCHEMA ###########################
	
	MARKDOWN = """
# %s
"""%input_mapping
	md = Markdown(MARKDOWN)
	console.print(md)
	
	# ~ print('[bold blue]%s[/bold blue]'%input_mapping)
	
	for elt in schema_columns:
		if elt not in data_columns:
			print('[red]%s[/red]'%elt)
		else:
			print('[green]%s[/green]'%elt)
	
	print('')
	
	# DATA ###########################
	
	MARKDOWN = """
# %s
"""%input_data
	md = Markdown(MARKDOWN)
	console.print(md)
	
	d = dict()
	# FIELD ANALYSIS
	for elt in data_columns:
		
		d[elt] = dict()
		
		# PRESENCE
		if elt not in schema_columns:
			# ~ print(elt)
			msg = "[red]'%s' absent from schema[/red]"%elt
			# ~ print(msg)
			d[elt]['presence']=(False, msg)
		else:
			d[elt]['presence']=(True, None)
			# TYPES
			to_type = get_type_of_var(standard, elt)
			# ~ print('%s (%s)'%(elt, to_type))
			res = is_ok(data[elt], to_type)
			if res is True:
				msg = '[green]Type %s is ok[/green]'%to_type
				# ~ print(msg)
				d[elt]['type']=(True, msg)
			elif res is False:
				msg = '[red]Type must be %s[/red]'%to_type
				# ~ print(msg)
				d[elt]['type']=(False, msg)
			else:
				msg = res[1]
				if res[0] is True:
					d[elt]['type']=(True, msg)
					# ~ print(msg)
				else:
					msg = '[red]%s[/red]'%msg
					# ~ print(msg)
					d[elt]['type']=(False, msg)
			
			# PATTERNS
			patt = get_pattern_of_var(standard, elt)
			if patt is not None:
				res = matches_regexp(data[elt], get_pattern_of_var(standard, elt))
				if res[0] is False:
					msg = "[red]'%s' do(es) not match pattern %s[/red]"%(', '.join(res[1]), patt)
					# ~ print(msg)
					d[elt]['pattern']=(False, msg)
				else:
					msg = "[green]Pattern %s is respected[/green]"%(patt)
					# ~ print(msg)
					d[elt]['pattern']=(True, msg)
					
			# ENUMS
			enums = get_enum_of_var(standard, elt)
			if enums is not None:
				res = matches_enum(data[elt], enums)
				if res[0] is False:
					msg = "[red]'%s' do(es) not belong to the possible values '%s'[/red]"%(', '.join(res[1]), ','.join(enums))
					# ~ print(msg)
					d[elt]['enums']=(False, msg)
		print('')
	
	print(d)
	
	# SUMMARY ######################
	
	MARKDOWN = """
# %s
"""%input_mapping
	md = Markdown(MARKDOWN)
	console.print(md)	
	
	
	for elt in schema_columns:
		if elt not in d.keys():
			print('[red]%s *ABSENT*[/red]'%elt)
		else:
			d2 = d[elt]
			to_type = get_type_of_var(standard, elt)
			if any([elt[0] is False for elt in d2.values()]):
				print('[red]%s (%s)[/red]'%(elt, to_type))
			else:
				print('[green]%s (%s)[/green]'%(elt, to_type))
	
	# PRINT #######################
	
	MARKDOWN = """
# %s
"""%input_data
	md = Markdown(MARKDOWN)
	console.print(md)
	
	for key, value in d.items():
		if key not in schema_columns:
			print('[red]%s *ABSENT*[/red]'%key)
		else:
			to_type = get_type_of_var(standard, key)
			if(all([elt[0] is True for elt in value.values()])):
				print('%s (%s) [green]OK[/green]'%(key, to_type))
			else:
				for key2, value2 in value.items():
					if value2[0] is False:
						print('%s (%s) %s'%(key, to_type, value2[1]))
		# ~ print('')


def transform(input_data, input_mapping, output_data = None):
	
	
	# READ DATA ###############################################
	
	data = read_data(input_data)
	mapping  = pd.read_csv(input_mapping)
	
	input_name = re.search('(.*)\\.(.*)', input_data).group(1)
	input_extension = re.search('(.*)\\.(.*)', input_data).group(2)
	
		
	# CONTROL ###################################################
	
	strange_cols = list()
	for elt in list(list(mapping['name'])):
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
