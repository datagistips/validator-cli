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
import numpy as np


def get_type_of_var(standard, the_var):
	'''
	>>> get_type_of_var(standard, "id_site")
	'integer'
	'''
	
	res = standard[standard.iloc[:,0]==the_var].iloc[0,2]
	return(res)
	
	
def get_dtype_as_string(dtype):
	
	if dtype == "object":
		return("object")
	elif dtype == "int64":
		return("int64")
	elif dtype == "float64":
		return("float64")
	elif dtype == "datetime64":
		return("datetime64")
	elif dtype == "bool":
		return("bool")
		

def inspect_type(from_types, to_types):
	'''
	>>> from_types
id          int64
lib        object
date       object
heure      object
ok           bool
id_site     int64
dtype: object

>>> to_types
['integer', 'character', 'date', None, 'boolean', None, None]
	'''
	
	strange_cols = list()
	for i, elt in enumerate(from_types):
		print(i)
		print(data.columns[i])
		from_type_dtype = get_dtype_as_string(elt)
		to_type_standard = to_types[i]
		if to_type_standard is not None:
			to_type_dtype = d[to_types[i]]
			print(from_type_dtype, '->', to_type_dtype)
			if from_type_dtype not in to_type_dtype:
				print("!! KO")
				strange_cols.append([i, from_type_dtype, to_type_dtype])
			
	return(strange_cols)


# Read data
data = gpd.read_file("../examples/data.gpkg", encoding = "utf-8")
standard = pd.read_csv("../examples/standard.csv", encoding = "iso-8859-1")
mapping = pd.read_csv("../examples/data-mapping.csv", encoding = "utf-8")

# Data and standard types
from_types = data.dtypes
from_types = from_types[:-1] # if geometry

to_types = list(standard.iloc[:,2])
to_cols = ['id_site', 'libelle', 'date_maj', None, 'is_ok', None, None]
to_types = [get_type_of_var(standard, elt) if elt is not None else None for elt in to_cols]
# ~ to_types = ['numeric', 'character', 'character', 'numeric', 'character', 'integer']

# Référentiel
from_type = ['integer', 'float', 'character', 'boolean', 'numeric', 'date', 'datetime'] # comprehensive types as mentioned in the standard
to_type = ['int64', 'float64', 'object', 'bool', ('int64', 'float64'), 'datetime64', 'datetime64'] # pandas dtype as used in python
d = dict(zip(from_type, to_type))

# Process
strange_cols = inspect_type(from_types, to_types)
print(strange_cols)
