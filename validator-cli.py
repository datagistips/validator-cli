# -*- coding: utf-8 -*-

import geopandas as gpd
import pandas as pd
from re import match, search
import os
import sys
import argparse
from datetime import datetime
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from ast import literal_eval
import numpy as np

from src.functions import *

console = Console()

global mapping


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
	
	# HEADER ###########################
	
	print('Time : %s'%now_string)
	
	data_columns = list(data.columns)
	schema_columns = list(standard["name"])
	
	
	# GET FIELDS REPORT ####################
	
	d = get_fields_report(data, standard)
	
	
	# PRINT SUMMARY ######################
	
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
	
	
	# PRINT DETAILS ON DATA #######################
	
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
				print('[green]%s (%s)[/green]'%(key, to_type))
			else:
				for key2, value2 in value.items():
					if value2[0] is False:
						print('[red]%s (%s) : %s[/red]'%(key, to_type, value2[1]))
		# ~ print('')


def transform(input_data, input_mapping, output_data = None):
	
	
	# READ DATA ###############################################
	
	data = read_data(input_data)
	mapping  = pd.read_csv(input_mapping)
	
	input_name = search('(.*)\\.(.*)', input_data).group(1)
	input_extension = search('(.*)\\.(.*)', input_data).group(2)
	
		
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
