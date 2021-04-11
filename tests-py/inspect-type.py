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
		return(None)
	return(res)
	
def control_date_alt1(date_text):
	try:
		res = datetime.strptime(date_text, '%d-%m-%Y')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(None)
	return(res)

def control_date_alt2(date_text):
	try:
		res = datetime.strptime(date_text, '%d-%m-%y')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(None)
	return(res)
	
def control_datetime(datetime_text):
	try:
		res = datetime.strptime(datetime_text, '%Y-%m-%d %H:%M:%S')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(None)
	return(res)
	
def control_time(time_ext):
	try:
		res = datetime.strptime(time_ext, '%Y-%m-%d %H:%M:%S')
	except ValueError:
		# ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
		return(None)
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
	
	if to_type in ("character", "text", "string"):
		if data_var.dtype == "object":
			return(True)
		else:
			return(False)
	
	elif to_type == "integer":
		if data_var.dtype == "int64":
			return((True, None, None))
		elif data_var.dtype == "float64":
			return((False, '[ERROR] Float type found', None))
		elif data_var.dtype == "object":
			v = [bool(re.match('\d', str(elt))) for elt in list(data_var)]
			i_not_valid = [i for i, elt in enumerate(v) if elt is False]
			if(len(i_not_valid) > 0):
				print("toto >", i_not_valid)
				elts_not_valid = [list(data_var)[i] for i in i_not_valid]
				print(elts_not_valid)
				return((False, '[ERROR] String characters found', elts_not_valid[1:5]))
			else:
				return((True, '[WARNING] Object type found', None))
		else:
			return((False, '[ERROR] Wrong type found', None))
				
	elif to_type in ("float", "number"):
		if data_var.dtype == "float64":
			return((True, None, None))
		elif data_var.dtype == "int64":
			return((True, '[WARNING] Integer type found', None))
		elif data_var.dtype == "object":
			v = [bool(re.match("(\d+\.?\d+)|(\d+\,?\d+)", str(elt))) for elt in data_var]
			i_not_valid = [i for i, elt in enumerate(v) if elt is False]
			if len(i_not_valid) > 0:
				v = [bool(re.match("(\d+\.?\d?)|(\d+\,?\d?)", str(elt))) for elt in data_var]
				i_not_valid = [i for i, elt in enumerate(v) if elt is False]
				if len(i_not_valid) > 0:
					print("toto >", i_not_valid)
					elts_not_valid = [list(data_var)[i] for i in i_not_valid]
					return((False, '[ERROR] Not float found', elts_not_valid[1:5]))
				else:
					return((True, '[WARNING] Integer type found', None))
			else:
				return((True, None, None))
		else:
			return((False, '[ERROR] Wrong type found', None))
			
			
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
			elts_not_valid = [elt for elt in list(set(data_var)) if elt not in ref_bool]
			print("v_not_valid > ", elts_not_valid)
			if len(elts_not_valid) > 0:
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
			n_not_valid = len([elt for elt in [control_date(elt) for elt in data_var] if elt is None])
			if n_not_valid > 0:
				return(False)
				elts_not_valid = [elt for elt in [control_date_alt1(elt) for elt in data_var] if elt is None]
				n_not_valid = len(elts_not_valid)
				if n_not_valid > 0:
					return(False)
					n_not_valid = len([elt for elt in [control_date_alt2(elt) for elt in data_var] if elt is None])
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
			elts_not_valid = [elt for elt in [control_datetime(elt) for elt in data_var] if elt is None]
			n_not_valid = len(elts_not_valid)
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
			elts_not_valid = [elt for elt in [control_time(elt) for elt in data_var] if elt is None]
			n_not_valid = len(elts_not_valid)
			if n_not_valid > 0:
				return(False)
			else:
				return(True)
		else:
			return(False)
			

# TESTS ################################################

# ~ # Strings
# ~ data = pd.DataFrame({"str" : ["a","b","c"]})
# ~ print(is_ok(data["str"], "string"))
# ~ print(is_ok(data["str"], "character"))
# ~ data = pd.DataFrame({"str" : [1,2,3]})
# ~ print(is_ok(data["str"], "character"))
# ~ data = pd.DataFrame({"str" : ['a',2,3]})
# ~ print(is_ok(data["str"], "character"))

# ~ # Integers
# ~ data = pd.DataFrame({"id" : [1,2,3]})
# ~ print(is_ok(data["id"], "integer"))
# ~ data = pd.DataFrame({"id" : ["1","2","3"]})
# ~ print(is_ok(data["id"], "integer"))
# ~ data = pd.DataFrame({"id" : ["a","b","c"]})
# ~ print(is_ok(data["id"], "integer"))

# Floats
data = pd.DataFrame({"num" : [1.2,2.2,3.2]})
print(is_ok(data["num"], "float"))
data = pd.DataFrame({"num" : ["1.2","2.2","3.2"]})
print(is_ok(data["num"], "float"))
data = pd.DataFrame({"num" : ["1.2","2.2","3.2"]})
print(is_ok(data["num"], "number"))
data = pd.DataFrame({"num" : ["1","2","3"]})
print(is_ok(data["num"], "number"))
data = pd.DataFrame({"num" : [1,2,3]})
print(is_ok(data["num"], "number"))
data = pd.DataFrame({"num" : ["a", "b", "c", 1, 2, 1.2]})
print(is_ok(data["num"], "number"))

# ~ # Booleans
# ~ data = pd.DataFrame({"ok" : [True, False, True]})
# ~ is_ok(data["ok"], "boolean")
# ~ data = pd.DataFrame({"ok" : [0, 1, 1]})
# ~ is_ok(data["ok"], "boolean")
# ~ data = pd.DataFrame({"ok" : ["TRUE", "FALSE", "TRUE"]})
# ~ is_ok(data["ok"], "boolean")
# ~ data = pd.DataFrame({"ok" : ["True", "False", "True"]})
# ~ is_ok(data["ok"], "boolean")
# ~ data = pd.DataFrame({"ok" : ["TRUE", "False", "True"]})
# ~ is_ok(data["ok"], "boolean")
# ~ data = pd.DataFrame({"ok" : ["0", "1", "1"]})
# ~ is_ok(data["ok"], "boolean")

# ~ # Dates
# ~ data = pd.DataFrame({"date" : ["2021-04-03", "2021-04-02", "2021-04-01"]})
# ~ is_ok(data["date"], "date")
# ~ data = pd.DataFrame({"date" : ["2021/04/03", "2021/04/02", "2021/04/01"]})
# ~ is_ok(data["date"], "date")
# ~ data = pd.DataFrame({"date" : ["2021-04-03", "2021-04-33", "2021-04-01"]}) # avec une erreur
# ~ is_ok(data["date"], "date")
# ~ data = pd.DataFrame({"date" : ["01-04-2021", "02-04-2021", "03-04-2021"]}) # avec un autre formatage
# ~ is_ok(data["date"], "date")
# ~ data = pd.DataFrame({"date" : ["01-04-21", "02-04-21", "03-04-21"]}) # avec les années courtes
# ~ is_ok(data["date"], "date")

# ~ # Datetimes
# ~ data = pd.DataFrame({"datetime" : ["2021-04-03 08:12:00", "2021-04-02 08:12:00", "2021-04-01 10:12:00"]})
# ~ is_ok(data["datetime"], "datetime")
# ~ data = pd.DataFrame({"datetime" : ["2021-04-03  08:12:00", "2021-04-02 30:12:00", "2021-04-01 25:12:00"]})
# ~ is_ok(data["datetime"], "datetime")

# ~ # Times
# ~ data = pd.DataFrame({"time" : ["08:12:00", "08:12:00", "10:12:00"]})
# ~ is_ok(data["time"], "time")
# ~ data = pd.DataFrame({"time" : ["08:12:00", "30:12:00", "25:12:00"]})
# ~ is_ok(data["time"], "time")


# CONFRONTATION AU FICHIER DE STANDARD #########################

# Read data
data = gpd.read_file("../examples/data.gpkg", encoding = "utf-8")
standard = pd.read_csv("standard.csv", encoding = "iso-8859-1")
# ~ mapping = pd.read_csv("../examples/data-mapping.csv", encoding = "utf-8")

def control_standard(data, standard):
	'''
	>>> @data     
	id         lib        date                heure     ok  id_site                   geometry
0   11    à la mer  2021-03-02                 None   True      100   POINT (-0.39889 0.22078)
1   10   printemps  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
2   20         été        None                 None  False      100    POINT (0.44341 0.46568)
3   20         été        None                 None  False      100    POINT (0.44341 0.46568)
4   10          BD  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
5   20         été        None                 None  False      100    POINT (0.44341 0.46568)
6   10         DVD  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
7   20       livre        None                 None  False      100    POINT (0.44341 0.46568)
8   10    oreiller  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
9   20     coussin        None                 None  False      100    POINT (0.44341 0.46568)
10  10        jean  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
11  20  chaussette        None                 None  False      100    POINT (0.44341 0.46568)
12  10       hiver  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)

>>> @standard     
	colonne          description       type
0        id  identifiant du site    boolean
1      date  date de mise à jour       date
2  nb_sites      nombre de sites    integer
3        ok                 ok ?    boolean
4       lib      libellé du site  character

> @d 
{'id': False, 'lib': True, 'date': True, 'ok': True}
	
	'''
	print("@data", data)
	print("@standard", standard)
	
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
				
	print("@d", d)			
	return(d)

# ~ d = control_standard(data, standard)
# ~ print(d)


# CASE WITH MAPPING FILE #########################################"

# Read data
data = gpd.read_file("../examples/data.gpkg", encoding = "utf-8")
standard = pd.read_csv("standard2.csv", encoding = "iso-8859-1")
mapping = pd.read_csv("data-mapping.csv", encoding = "utf-8")

def find_to_col(mapping, elt):
	to_col = mapping[mapping["from"] == elt]["to"].item()
	
	if to_col == ('_%s')%elt:
		return(None)
	else:
		return(to_col)
		
def is_matched(df_var, regexp):
	'''
	>>> df_var
0    a1
1    a2
2    a3

>>> regexp
'a[0-9]'

> True
	
	'''
	
	v = [elt for elt in [bool(re.match(regexp, elt)) for elt in list(df_var)] if elt is False]
	print(v)
	if len(v) > 0:
		return(False)
	else:
		return(True)
	
def control_mapping_standard(data, mapping, standard):
	
	print("-----")
	print("CONTROL 2")
	
	from_cols = [elt for elt in list(data.columns) if elt != 'geometry']
	to_cols = [find_to_col(mapping, elt) for elt in from_cols]
	
	
	print("from : ", from_cols)
	print("to : ", to_cols)
	
	d = dict()
	for i, from_col in enumerate(from_cols):
		to_col = to_cols[i]
		if to_col is not None:
			to_type = get_type_of_var(standard, to_col)
			print("colonne d'entrée :", from_col)
			if to_type is not None:
				data_var = data[from_col]
				data_var = data_var.dropna()
				d[from_col] = is_ok(data_var, to_type)
			else:
				d[from_col] = is_ok(data_var, to_type)
	
	return(d)
					
# ~ d = control_mapping_standard(data, mapping, standard)


# TESTS REGEXP #########################################

df = pd.DataFrame({'v':['a1', 'a2', 'a3']})
# ~ print(is_matched(df['v'], 'a[0-9]'))

