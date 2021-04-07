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


def process(input_data, input_mapping, output_data = None):
	
	
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
				print(elt)
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
	
	parser.add_argument("-i", "--input", help="input file")
	parser.add_argument("-d", "--inputdir", help="input directory")
	parser.add_argument("-m", "--mapping", help="input mapping file path", required = True)
	parser.add_argument("-o", "--output", help="Output file (Optional and active if in single file mode, not directory mode)")


	args = parser.parse_args()

	input_data = args.input
	input_dir = args.inputdir
	input_mapping = args.mapping
	output_data = args.output
	
	
	# READ ####################################################
	
	# Read mapping
	if not os.path.exists(input_mapping):
		print(("ERROR : mapping file '%s' doesn't exist")%input_mapping)
		quit()
	else:
		mapping  = pd.read_csv(input_mapping)

	
	# PROCESS ####################################################
	
	# Process
	if input_data is not None and input_dir is None:
		
		# READ FILE ----
		
		if not os.path.exists(input_data):
			print(("ERROR : file '%s' doesn't exist")%input_data)
			quit()
		
		if output_data is not None:
			process(input_data, input_mapping, output_data)
		else:
			process(input_data, input_mapping)
		
	elif input_data is None and input_dir is not None:
		
		if not os.path.exists(input_dir):
			print(("ERROR : directory '%s' doesn't exist")%input_dir)
			quit()
		
		if output_data is not None:
			print("Output file will not be taken into account when renaming batches of data")
			
		l = os.listdir(input_dir)
		for input_data in l:
			input_data = os.path.join(input_dir, input_data)
			process(input_data, input_mapping)
			print('-----------------------------------------------------------------------------------')
			
	elif input_data is not None and input_dir is not None:
		
		print("ERROR : Choose either a file or folder with data")
		quit()
		
	elif input_data is None and input_dir is None:
		
		print("ERROR : Choose either a file or folder with data")
		quit()
