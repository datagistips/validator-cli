# -*- coding: iso-8859-1 -*-

# - créer fonction is_matched
# - créer fonction considérant le mapping control_types_mapping(data, mapping, standard)

import geopandas as gpd
from dateutil.parser import parse
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
from dateutil.parser import parse

# ~ from dateutil.parser import parse
# ~ >>> parse("2003-09-25")
# ~ datetime.datetime(2003, 9, 25, 0, 0)

def control_date(date_text):
	try:
		res = datetime.strptime(date_text, '%Y-%m-%d') # ISO 8601
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(0)
	return(res)
	
def control_date_alt1(date_text):
	try:
		res = datetime.strptime(date_text, '%d-%m-%Y')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(0)
	return(res)

def control_date_alt2(date_text):
	try:
		res = datetime.strptime(date_text, '%d-%m-%y')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(0)
	return(res)
	
def control_datetime(datetime_text):
	try:
		res = datetime.strptime(datetime_text, '%Y-%m-%d %H:%M:%S')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(0)
	return(res)
	
def control_time(time_ext):
	try:
		res = datetime.strptime(time_ext, '%Y-%m-%d %H:%M:%S')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(0)
	return(res)

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
		

# Référentiel
# ~ from_type = ['integer', 'float', 'character', 'boolean', 'numeric', 'date', 'datetime'] # comprehensive types as mentioned in the standard
# ~ to_type = ['int64', 'float64', 'object', 'bool', ('int64', 'float64'), 'datetime64', 'datetime64'] # pandas dtype as used in python
# ~ d = dict(zip(from_type, to_type))

# Process
# ~ strange_cols = inspect_type(from_types, to_types)
# ~ print(strange_cols)

# Compare
def is_ok(data_var, to_type):
	
	print("----")
	print(data_var)
	
	print("type d'origine : ", data_var.dtype)
	print("type de destination : ", to_type)
	
	if to_type in ("character", "text"):
		if data_var.dtype == "object":
			return(True)
		else:
			return(False)
	
	elif to_type == "integer":
		if data_var.dtype == "int64":
			return(True)
		elif data_var.dtype == "float64":
			return(False)
		elif data_var.dtype == "object":
			v = [bool(re.match('\d', str(elt))) for elt in list(data['id'])]
			v = [elt for elt in v if v is False]
			if(len(v) > 0):
				print("il existe des éléments non entiers")
				return(False)
			else:
				print('ok')
				return(True)
		else:
			return(False)
				
	elif to_type in ("float", "number"):
		if data_var.dtype == "float64":
			return(True)
		elif data_var.dtype == "int64":
			return(False)
		elif data_var.dtype == "object":
			v = [bool(re.match("(\d+\.\d+)|(\d+\,\d+)", elt)) for elt in data_var]
			v = [elt for elt in v if v is False]
			if len(v) > 0:
				return(False)
			else:
				return(True)
		else:
			return(False)
			
			
	elif to_type == "boolean":
		
		if data_var.dtype == "bool":
			return(True)
		elif data_var.dtype == "int64":
			v = list(set(data_var))
			if v == [0,1] or v in (0, 1):
				return(True)
			else:
				return(False)
		elif data_var.dtype == "object":
			print("!! vérifs")
			ref_bool = ["0", "1", "TRUE", "FALSE", "True", "False"]
			v_not_valid = [elt for elt in list(set(data_var)) if elt not in ref_bool]
			print("v_not_valid", v_not_valid)
			if len(v_not_valid) > 0:
				return(False)
			else:
				return(True)
		else:
			return(False)
			
	elif to_type == "date":
		if data_var.dtype == "datetime64":
			return(True)
		elif data_var.dtype == "object":
			print('controle date')
			n_not_valid = len([elt for elt in [control_date(elt) for elt in data_var] if elt == 0])
			if n_not_valid > 0:
				return(False)
				n_not_valid = len([elt for elt in [control_date_alt1(elt) for elt in data_var] if elt == 0])
				if n_not_valid > 0:
					return(False)
					n_not_valid = len([elt for elt in [control_date_alt2(elt) for elt in data_var] if elt == 0])
					if n_not_valid > 0:
						return(False)
					else:
						return(False)
			else:
				return(True)
		else:
			return(False)
			
	elif to_type == "datetime":
		if data_var.dtype == "datetime64":
			print("ok")
		elif data_var.dtype == "object":
			n_not_valid = len([elt for elt in [control_datetime(elt) for elt in data_var] if elt == 0])
			if n_not_valid > 0:
				print(False)
			else:
				return(True)
		else:
			return(False)
				
	elif to_type == "time":
		if data_var.dtype == "datetime64":
			return(True)
		elif data_var.dtype == "object":
			n_not_valid = len([elt for elt in [control_time(elt) for elt in data_var] if elt == 0])
			if n_not_valid > 0:
				return(False)
			else:
				return(True)
		else:
			return(False)
			

# TESTS ################################################

# Strings
data = pd.DataFrame({"str" : ["a","b","c"]})
is_ok(data["str"], "string")
is_ok(data["str"], "character")
data = pd.DataFrame({"str" : [1,2,3]})
is_ok(data["str"], "character")
data = pd.DataFrame({"str" : ['a',2,3]})
is_ok(data["str"], "character")

# Integers
data = pd.DataFrame({"id" : [1,2,3]})
is_ok(data["id"], "integer")
data = pd.DataFrame({"id" : ["1","2","3"]})
is_ok(data["id"], "integer")

# Floats
data = pd.DataFrame({"num" : [1.2,2.2,3.2]})
is_ok(data["num"], "float")
data = pd.DataFrame({"num" : ["1.2","2.2","3.2"]})
is_ok(data["num"], "foat")
data = pd.DataFrame({"num" : ["1.2","2.2","3.2"]})
is_ok(data["num"], "number")


# Booleans
data = pd.DataFrame({"ok" : [True, False, True]})
is_ok(data["ok"], "boolean")
data = pd.DataFrame({"ok" : [0, 1, 1]})
is_ok(data["ok"], "boolean")
data = pd.DataFrame({"ok" : ["TRUE", "FALSE", "TRUE"]})
is_ok(data["ok"], "boolean")
data = pd.DataFrame({"ok" : ["True", "False", "True"]})
is_ok(data["ok"], "boolean")
data = pd.DataFrame({"ok" : ["TRUE", "False", "True"]})
is_ok(data["ok"], "boolean")
data = pd.DataFrame({"ok" : ["0", "1", "1"]})
is_ok(data["ok"], "boolean")

# Dates
data = pd.DataFrame({"date" : ["2021-04-03", "2021-04-02", "2021-04-01"]})
is_ok(data["date"], "date")
data = pd.DataFrame({"date" : ["2021/04/03", "2021/04/02", "2021/04/01"]})
is_ok(data["date"], "date")
data = pd.DataFrame({"date" : ["2021-04-03", "2021-04-33", "2021-04-01"]}) # avec une erreur
is_ok(data["date"], "date")
data = pd.DataFrame({"date" : ["01-04-2021", "02-04-2021", "03-04-2021"]}) # avec un autre formatage
is_ok(data["date"], "date")
data = pd.DataFrame({"date" : ["01-04-21", "02-04-21", "03-04-21"]}) # avec les années courtes
is_ok(data["date"], "date")

# Datetimes
data = pd.DataFrame({"datetime" : ["2021-04-03 08:12:00", "2021-04-02 08:12:00", "2021-04-01 10:12:00"]})
is_ok(data["datetime"], "datetime")
data = pd.DataFrame({"datetime" : ["2021-04-03  08:12:00", "2021-04-02 30:12:00", "2021-04-01 25:12:00"]})
is_ok(data["datetime"], "datetime")

# Times
data = pd.DataFrame({"time" : ["08:12:00", "08:12:00", "10:12:00"]})
is_ok(data["time"], "time")
data = pd.DataFrame({"time" : ["08:12:00", "30:12:00", "25:12:00"]})
is_ok(data["time"], "time")

# CONFRONTATION AU FICHIER DE STANDARD #########################

# Read data
data = gpd.read_file("../examples/data.gpkg", encoding = "utf-8")
standard = pd.read_csv("standard.csv", encoding = "iso-8859-1")
# ~ mapping = pd.read_csv("../examples/data-mapping.csv", encoding = "utf-8")

def control_types(data, standard):
	
	print("## CONTROLE")
	to_cols = [elt for elt in data.columns if elt in list(standard.iloc[:,0]) and elt != 'geometry']
	# ~ to_cols = [mapping.iloc[i, 1] for i in range(data.shape[1]) if mapping.iloc[i, 1]!="_%s"%mapping.iloc[i, 0]] # on ne retient pas les colonnes avec préfixe _
	print('>> to_cols : ', to_cols)
	
	d = dict()
	res = list()
	for i, elt in enumerate(to_cols):
		to_type = get_type_of_var(standard, elt)
		if elt != "geometry":
			print("colonne d'entrée :", elt)
			if to_type is not None:
				data_var = data[elt]
				data_var = data_var.dropna()
				res.append(is_ok(data_var, to_type))
				d[elt] = is_ok(data_var, to_type)
			else:
				res.append(True)
				d[elt] = is_ok(data_var, to_type)
	return(d)

d = control_types(data, standard)

print(d)

def control_mapping_standard(data, mapping, standard):
	[elt for elt in data.columns if elt not in mapping.iloc[:,0]]
