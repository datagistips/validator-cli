# -*- coding: utf-8 -*-

# - cr�er fonction consid�rant le mapping control_types_mapping(data, mapping, standard)
# - am�liorer la d�tection des dates
# - enlever (True)

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
import ast
from dateutil.parser import parse

# ~ from dateutil.parser import parse
# ~ >>> parse("2003-09-25")
# ~ datetime.datetime(2003, 9, 25, 0, 0)


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
    """


    """

    v = [
        elt
        for elt in list(df_var)
        if elt not in l
    ]
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


def get_type_of_var(standard, the_var):
    """
    >>> get_type_of_var(standard, "id_site")
    'integer'
    """

    res = standard[standard.iloc[:, 0] == the_var]['type']
    return res

    
def get_enum_of_var(standard, the_var):
    """
    """

    l = standard[standard.iloc[:, 0] == the_var]['enum'].item()
    res = ast.literal_eval(l)
    return res


def get_dtype_as_string(dtype):

    if dtype == "object":
        return "object"
    elif dtype == "int64":
        return "int64"
    elif dtype == "float64":
        return "float64"
    elif dtype == "datetime64":
        return "datetime64"
    elif dtype == "bool":
        return "bool"


# R�f�rentiel
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

    print("> type d'origine : ", data_var.dtype)
    print("> type de destination : ", to_type)

    if to_type in ("character", "text", "string"):
        if data_var.dtype == "object":
            return True
        else:
            return False

    elif to_type == "integer":
        if data_var.dtype == "int64":
            return (True)
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
            return (True)
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
                    print("toto >", i_not_valid)
                    elts_not_valid = [list(data_var)[i] for i in i_not_valid]
                    return (False, "[ERROR] No float types found", elts_not_valid[1:5])
                else:
                    return (True, "[WARNING] Integer type found", None)
            else:
                return (True)
        else:
            return (False, "[ERROR] Wrong type found", None)

    elif to_type == "boolean":
        if data_var.dtype == "bool":
            return (True)
        elif data_var.dtype == "int64":
            unique_values = list(set(data_var))
            if unique_values == [0, 1] or unique_values in (0, 1):
                return (True)
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
                return (True)
            elif all([elt in ["0", "1", "TRUE", "FALSE", "True", "False"] for elt in unique_values]):
                return (False, '[ERROR] Mix of values', None)
            else:
                return (False, '[ERROR] Wrong values', None)
        else:
            return False
	
    elif to_type == "date":
	    print('ok')
	    if data_var.dtype == "datetime64":
		    print('ok')
	    elif data_var.dtype == "object":
            
		    if all([control_date(elt) is not None for elt in data_var]):
			    return(True)
		    elif all([control_date_alt1(elt) is not None for elt in data_var]):
			    return((False, '[ERROR] Day, month and year in wrong order', None))
		    elif all([control_date_alt2(elt) is not None for elt in data_var]):
			    return((False, '[ERROR] Years too short', None))
		    elif all([bool(re.match("[0-9]+-[0-9]+-[0-9]+", elt)) is True for elt in data_var]):
			    return((False, '[ERROR] Days not in range', None))
		    elif all([bool(re.match("[0-9]+/[0-9]+/[0-9]+", elt)) is True for elt in data_var]):
			    return((False, '[ERROR] Not well formatted. Folllow ISO8601', None))
		    else:
			    return((False, '[ERROR] Dates not valid', None))
				
    elif to_type == "datetime":
        if data_var.dtype == "datetime64":
            return (True)
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
                return (True)
        else:
            return (False, "[ERROR] Wrong type", None)

    elif to_type == "time":
        if data_var.dtype == "datetime64":
            return (True)
        elif data_var.dtype == "object":
            elts_not_valid = [
                elt for elt in [control_time(elt) for elt in data_var] if elt is None
            ]
            n_not_valid = len(elts_not_valid)
            if n_not_valid > 0:
                return (False, "[ERROR] Wrong time", None)
            else:
                return (True)
        else:
            return (False, "[ERROR] Wrong type", None)


# TESTS ################################################

# ~ # Strings
# ~ data = pd.DataFrame({"str": ["a", "b", "c"]})
# ~ print(is_ok(data["str"], "string"))
# ~ print(is_ok(data["str"], "character"))
# ~ data = pd.DataFrame({"str": [1, 2, 3]})
# ~ print(is_ok(data["str"], "character"))
# ~ data = pd.DataFrame({"str": ["a", 2, 3]})
# ~ print(is_ok(data["str"], "character"))

# ~ # Integers
# ~ data = pd.DataFrame({"id": [1, 2, 3]})
# ~ print(is_ok(data["id"], "integer"))
# ~ data = pd.DataFrame({"id": ["1", "2", "3"]})
# ~ print(is_ok(data["id"], "integer"))
# ~ data = pd.DataFrame({"id": ["a", "b", "c"]})
# ~ print(is_ok(data["id"], "integer"))

# ~ # Floats
# ~ data = pd.DataFrame({"num": [1.2, 2.2, 3.2]})
# ~ print(is_ok(data["num"], "float"))
# ~ data = pd.DataFrame({"num": ["1.2", "2.2", "3.2"]})
# ~ print(is_ok(data["num"], "float"))
# ~ data = pd.DataFrame({"num": ["1.2", "2.2", "3.2"]})
# ~ print(is_ok(data["num"], "number"))
# ~ data = pd.DataFrame({"num": ["1", "2", "3"]})
# ~ print(is_ok(data["num"], "number"))
# ~ data = pd.DataFrame({"num": [1, 2, 3]})
# ~ print(is_ok(data["num"], "number"))
# ~ data = pd.DataFrame({"num": ["a", "b", "c", 1, 2, 1.2]})
# ~ print(is_ok(data["num"], "number"))

# Booleans
data = pd.DataFrame({"ok": [True, False, True]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": [0, 1, 1]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": [0, 1, 1, 2, 3]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": ["TRUE", "FALSE", "TRUE"]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": ["True", "False", "True"]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": ["TRUE", "False", "True"]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": ["0", "1", "1"]})
print(is_ok(data["ok"], "boolean"))
data = pd.DataFrame({"ok": ["0", "1", "2"]})
print(is_ok(data["ok"], "boolean"))

# ~ # Dates
# ~ data = pd.DataFrame({"date": ["2021-04-03", "2021-04-02", "2021-04-01"]})
# ~ print(is_ok(data["date"], "date"))
# ~ data = pd.DataFrame({"date": ["2021/04/03", "2021/04/02", "2021/04/01"]})
# ~ print(is_ok(data["date"], "date"))
# ~ data = pd.DataFrame(
    # ~ {"date": ["2021-04-03", "2021-04-33", "2021-04-01"]}
# ~ )  # avec une erreur
# ~ print(is_ok(data["date"], "date"))
# ~ data = pd.DataFrame(
    # ~ {"date": ["01-04-2021", "02-04-2021", "03-04-2021"]}
# ~ )  # avec un autre formatage
# ~ print(is_ok(data["date"], "date"))
# ~ data = pd.DataFrame(
    # ~ {"date": ["01-04-21", "02-04-21", "03-04-21"]}
# ~ )  # avec les ann�es courtes
# ~ print(is_ok(data["date"], "date"))
# ~ data = pd.DataFrame({"date": [1, 2, 3]})
# ~ print(is_ok(data["date"], "date"))
# ~ data = pd.DataFrame({"date": ["a", "b", "c"]})
# ~ print(is_ok(data["date"], "date"))


# ~ # Datetimes
# ~ data = pd.DataFrame(
    # ~ {"datetime": ["2021-04-03 08:12:00", "2021-04-02 08:12:00", "2021-04-01 10:12:00"]}
# ~ )
# ~ print(is_ok(data["datetime"], "datetime"))
# ~ data = pd.DataFrame(
    # ~ {"datetime": ["2021-04-03  08:12:00", "2021-04-02 30:12:00", "2021-04-01 25:12:00"]}
# ~ )
# ~ print(is_ok(data["datetime"], "datetime"))

# ~ # Times
# ~ data = pd.DataFrame({"time": ["08:12:00", "08:12:00", "10:12:00"]})
# ~ print(is_ok(data["time"], "time"))
# ~ data = pd.DataFrame({"time": ["08:12:00", "30:12:00", "25:12:00"]})
# ~ print(is_ok(data["time"], "time"))

# ~ # Regexps
# ~ data = pd.DataFrame({"values": ["75114-P-001", "75114-P-002", "75056-P-001"]}) 
# ~ print(matches_regexp(data["values"], "^([013-9]\d|2[AB1-9])\d{3}-P-\d{3}$"))# parkings
# ~ data = pd.DataFrame({"values": ["75114-P-001", "751-P-001", "75114-P-00"]})
# ~ print(matches_regexp(data["values"], "^([013-9]\d|2[AB1-9])\d{3}-P-\d{3}$")) 
# ~ data = pd.DataFrame({"values": ["75114", "75100", "13090"]})
# ~ print(matches_regexp(data["values"], "^([013-9]\d|2[AB1-9])\d{3}$")) # codes insee
# ~ data = pd.DataFrame({"values": ["75114", "751", "751144"]})
# ~ print(matches_regexp(data["values"], "^([013-9]\d|2[AB1-9])\d{3}$"))
# ~ data = pd.DataFrame({"values": ["80295478500028", "80295478500018", "80295478500029"]}) 
# ~ print(matches_regexp(data["values"], "^\d{14}$")) # siret
# ~ data = pd.DataFrame({"values": ["802954785000", "8029547850001899", "80295478500029"]})
# ~ print(matches_regexp(data["values"], "^\d{14}$"))

# ~ # List of values
# ~ print(">> Control of values list")
# ~ standard = pd.read_csv("standard2.csv", encoding = "iso-8859-1")
# ~ l = get_enum_of_var(standard, 'liste_valeurs1')
# ~ data = pd.DataFrame({"values": ["a", "b", "c"]})
# ~ print(matches_enum(data["values"], l))
# ~ data = pd.DataFrame({"values": ["a", "b", "d"]})
# ~ print(matches_enum(data["values"], l))

# ~ l = get_enum_of_var(standard, 'liste_valeurs2')
# ~ data = pd.DataFrame({"values": [1, 2, 3]})
# ~ print(matches_enum(data["values"], l))
# ~ data = pd.DataFrame({"values": [1, 2, 4]})
# ~ print(matches_enum(data["values"], l))

################################################################
# CONFRONTATION AU FICHIER DE STANDARD #########################
################################################################

# Read data
# ~ data = gpd.read_file("../examples/data.gpkg", encoding = "utf-8")
# ~ standard = pd.read_csv("standard.csv", encoding = "iso-8859-1")
# ~ mapping = pd.read_csv("../examples/data-mapping.csv", encoding = "utf-8")


def control_data_to_standard(data, standard):
    """
            >>> @data
            id         lib        date                heure     ok  id_site                   geometry
    0   11    � la mer  2021-03-02                 None   True      100   POINT (-0.39889 0.22078)
    1   10   printemps  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
    2   20         �t�        None                 None  False      100    POINT (0.44341 0.46568)
    3   20         �t�        None                 None  False      100    POINT (0.44341 0.46568)
    4   10          BD  2021-03-09  2021-03-09T00:00:00  False      100  POINT (-0.01670 -0.18367)
    5   20         �t�        None                 None  False      100    POINT (0.44341 0.46568)
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
    1      date  date de mise � jour       date
    2  nb_sites      nombre de sites    integer
    3        ok                 ok ?    boolean
    4       lib      libell� du site  character

    > @d
    {'id': False, 'lib': True, 'date': True, 'ok': True}

    """
    print("@data", data)
    print("@standard", standard)

    print("## CONTROLE")
    to_cols = [
        elt
        for elt in data.columns
        if elt in list(standard.iloc[:, 0]) and elt != "geometry"
    ]
    # ~ to_cols = [mapping.iloc[i, 1] for i in range(data.shape[1]) if mapping.iloc[i, 1]!="_%s"%mapping.iloc[i, 0]] # on ne retient pas les colonnes avec pr�fixe _
    print(">> to_cols : ", to_cols)

    d = dict()
    res = list()
    for i, elt in enumerate(to_cols):
        to_type = get_type_of_var(standard, elt)
        if elt != "geometry":
            print("colonne d'entr�e :", elt)
            if to_type is not None:
                data_var = data[elt]
                data_var = data_var.dropna()
                res.append(is_ok(data_var, to_type))
                d[elt] = is_ok(data_var, to_type)
            else:
                res.append(True)
                d[elt] = is_ok(data_var, to_type)

    print("@d", d)
    return d


# ~ d = control_data_to_standard(data, standard)
# ~ print(d)


# CASE WITH MAPPING FILE #########################################"

# Read data
# ~ data = gpd.read_file("../examples/data.gpkg", encoding = "utf-8")
# ~ standard = pd.read_csv("standard2.csv", encoding = "iso-8859-1")
# ~ mapping = pd.read_csv("data-mapping.csv", encoding = "utf-8")


def find_destination_column_for_source_column(mapping, elt):
    to_col = mapping[mapping["from"] == elt]["to"].item()

    if to_col == ("_%s") % elt:
        return None
    else:
        return to_col


def control_data_to_mapping(data, mapping, standard):

    print("-----")
    print("CONTROL 2")

    from_cols = [elt for elt in list(data.columns) if elt != "geometry"]
    to_cols = [
        find_destination_column_for_source_column(mapping, elt) for elt in from_cols
    ]

    print("from : ", from_cols)
    print("to : ", to_cols)

    d = dict()
    for i, from_col in enumerate(from_cols):
        to_col = to_cols[i]
        if to_col is not None:
            to_type = get_type_of_var(standard, to_col)
            print("colonne d'entr�e :", from_col)
            if to_type is not None:
                data_var = data[from_col]
                data_var = data_var.dropna()
                d[from_col] = is_ok(data_var, to_type)
            else:
                d[from_col] = is_ok(data_var, to_type)

    return d


# ~ d = control_data_to_mapping(data, mapping, standard)


# TESTS REGEXP #########################################

# ~ df = pd.DataFrame({'v':['a1', 'a2', 'a3']})
# ~ print(matches_regexp(df['v'], 'a[0-9]'))
