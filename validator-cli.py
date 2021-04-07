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

global mapping


def read_data(input_data):
	
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
	
	data = read_data(input_data)
	mapping  = pd.read_csv(input_mapping)
	
	# Columns
	data_columns = list(data.columns)
	schema_columns = list(mapping.iloc[:,0])

	# Data columns absent from schema
	strange_cols1 = list()
	matching_cols1 = list()
	for elt in data_columns:
		if elt not in schema_columns:
			strange_cols1.append(elt)
		else:
			matching_cols1.append(elt)
	
	# Schema columns absent from data
	strange_cols2 = list()
	matching_cols2 = list()
	for elt in schema_columns:
		if elt not in data_columns:
			strange_cols2.append(elt)
		else:
			matching_cols2.append(elt)
	
	# Conform or not ?
	if len(matching_cols1) > 0:
		conform = False
		pc = len(matching_cols1) / data.shape[0]
	else:
		conform = True
	
	# Messages
	print('[KO] Data non valid' if conform is False else '[OK] Data valid')
	print('')
	print('Input data : %s'%input_data)
	print('Data schema : %s'%input_mapping)
	print('')
	print(('Data columns : %s')%(', '.join(data_columns)))
	print(('Schema columns : %s')%(', '.join(schema_columns)))
	print('')
	print(('Data columns present in schema : %s')%(', '.join(matching_cols1)))
	print(('Data columns absent from schema : %s')%(', '.join(strange_cols1)))
	print('')
	print(('Schema columns present in data : %s')%(', '.join(matching_cols2)))
	print(('Schema columns absent from data : %s')%(', '.join(strange_cols2)))
	


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
	
	print(('Input data : %s')%(input_data))
	print(data.iloc[range(5),])
	print('\n')
	print(('Mapping file : %s')%(input_mapping))
	print(mapping)
	print('\n')
	print(('Mapped data : %s')%(output_data))
	print(data2.iloc[range(5), ])


if __name__ == "__main__":
	
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
