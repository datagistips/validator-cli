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


def transform(input_data, input_mapping, output_data = None):
	
	
	# READ DATA ###############################################
	
	input_name = re.search('(.*)\\.(.*)', input_data).group(1)
	input_extension = re.search('(.*)\\.(.*)', input_data).group(2)
	
	if input_extension == 'csv':
		file_class = "df"
		data = pd.read_csv(input_data, encoding = 'utf-8')
	else:
		file_class = "geo"
		data = gpd.read_file(input_data, encoding = 'utf-8')
		
		
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
	
	print(('> Input data : %s')%(input_data))
	print(data.iloc[range(5),])
	print('\n')
	print(('> Mapping file : %s')%(input_mapping))
	print(mapping)
	print('\n')
	print(('> Mapped data : %s')%(output_data))
	print('> Here is its content (first 10 rows) :')
	print(data2.iloc[range(5), ])


if __name__ == "__main__":
	
	# ARGUMENTS ##############################################
	
	parser = argparse.ArgumentParser()
	
	parser.add_argument("mode", choices=['control', 'transform'], help='Control data against a data schema or transform data thanks to a mapping file')
	parser.add_argument("-d", "--directory", help="process entire directory", action="store_true")
	parser.add_argument("input", help="input file or directory (depends if you specified -d or not)")
	parser.add_argument("schema", help="input mapping file or data schema file path")
	parser.add_argument("-o", "--output", help="Output file (Optional and active if in single file mode, not directory mode)")


	args = parser.parse_args()
	
	mode = args.mode
	directory = args.directory
	input_data = args.input
	input_mapping = args.schema
	output_data = args.output
	
	print(mode)
	print(args)
	
	
	# READ ####################################################
	
	# Read mapping
	if not os.path.exists(input_mapping):
		print(("ERROR : mapping file '%s' doesn't exist")%input_mapping)
		quit()
	else:
		mapping  = pd.read_csv(input_mapping)

	
	# PROCESS ####################################################
	
	# Transform
	
	if mode == "transform":
		if directory is False :
			
			# READ FILE ----
			
			if not os.path.exists(input_data):
				print(("ERROR : file '%s' doesn't exist")%input_data)
				quit()
			
			if output_data is not None:
				transform(input_data, input_mapping, output_data) # we use the output data file name
			else:
				transform(input_data, input_mapping) # we'll create and output data name based on input data file name
			
		elif directory is True:
			
			if not os.path.exists(input_data):
				print(("ERROR : directory '%s' doesn't exist")%input_dir)
				quit()
			
			if output_data is not None:
				print("Output file will not be taken into account when renaming batches of data")
				
			l = os.listdir(input_data)
			for elt in l:
				transform(os.path.join(input_data, elt), input_mapping)
				print('-----------------------------------------------------------------------------------')
