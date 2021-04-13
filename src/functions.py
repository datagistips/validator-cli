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
import pathlib

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
        for i, elt in enumerate([bool(match(regexp, str(elt))) for elt in list(df_var)])
        if elt is False
    ]
    

    not_valid = [list(df_var)[i] for i in i_not_valid]
    if len(not_valid) > 0:
        return (False, not_valid)
    else:
        return True


def matches_enum(df_var, l):
    """"""

    not_valid = [elt for elt in list(df_var) if elt not in l]
    if len(not_valid) > 0:
        return (False, not_valid)
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
    Retrieves pattern for a variable in the data standard
    """

    res = standard[standard['name'] == the_var]["pattern"].item()
    res = None if res == '' or res is np.nan else res
    return res


def get_type_of_var(standard, the_var):
    """
    >>> get_type_of_var(standard, "id_site")
    'integer'
    """

    res = standard[standard['name'] == the_var]["type"].item()
    return res


def get_enum_of_var(standard, the_var):
	"""
	Retrieves enum list in data schema for a variable
	"""
	
	l = standard[standard['name'] == the_var]["enum"].item()
	l = None if l == '' or l is np.nan else l
	if l is not None:
		res = literal_eval(l)
	else:
		res = None
	return res


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
            v = [bool(match("\d", str(elt))) for elt in list(data_var)]
            i_not_valid = [i for i, elt in enumerate(v) if elt is False]
            if len(i_not_valid) > 0:
                elts_not_valid = [list(data_var)[i] for i in i_not_valid]
                return (False, "String character(s) found", elts_not_valid[1:5])
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
                bool(match("(\d+\.?\d+)|(\d+\,?\d+)", str(elt))) for elt in data_var
            ]
            i_not_valid = [i for i, elt in enumerate(v) if elt is False]
            if len(i_not_valid) > 0:
                v = [
                    bool(match("(\d+\.?\d?)|(\d+\,?\d?)", str(elt)))
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
                    "One or more integer values not equal to 0 or 1",
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
                    bool(match("[0-9]+-[0-9]+-[0-9]+", elt)) is True
                    for elt in data_var
                ]
            ):
                return (False, "Day(s) not in range", None)
            elif all(
                [
                    bool(match("[0-9]+/[0-9]+/[0-9]+", elt)) is True
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

    elif to_type == "duration":
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
	input_extension = pathlib.Path(input_data).suffix
	
	if input_extension == '.csv':
		file_class = "df"
		data = pd.read_csv(input_data, encoding = 'utf-8')
	else:
		file_class = "geo"
		data = gpd.read_file(input_data, encoding = 'utf-8')
			
	return(data)


def get_fields_report(data, standard):
	
	data_columns = [elt for elt in list(data.columns) if elt != 'geometry']
	schema_columns = list(standard["name"])
	
	d = dict()
	
	# FIELD ANALYSIS
	for elt in data_columns:
		
		d[elt] = dict()
		
		# PRESENCE ----
		if elt not in schema_columns:
			msg = "[red]'%s' absent from schema[/red]"%elt
			d[elt]['presence']=(False, msg)
		else:
			d[elt]['presence']=(True, None)
			
			# TYPES ----
			to_type = get_type_of_var(standard, elt)
			res = is_ok(data[elt], to_type)
			if res is True:
				msg = '[green]Type %s is ok[/green]'%to_type
				d[elt]['type']=(True, msg)
			elif res is False:
				msg = '[red]Type must be %s[/red]'%to_type
				d[elt]['type']=(False, msg)
			else:
				msg = res[1]
				if res[0] is True:
					d[elt]['type']=(True, msg)
				else:
					msg = '[red]%s[/red]'%msg
					d[elt]['type']=(False, msg)
			
			# PATTERNS ----
			patt = get_pattern_of_var(standard, elt)
			if patt is not None:
				res = matches_regexp(data[elt].astype(str), get_pattern_of_var(standard, elt))
				if res[0] is False:
					msg = "[red]'%s' do(es) not match pattern %s[/red]"%(', '.join(res[1]), patt)
					d[elt]['pattern']=(False, msg)
				else:
					msg = "[green]Pattern %s is respected[/green]"%(patt)
					d[elt]['pattern']=(True, msg)
					
			# ENUMS ----
			enums = get_enum_of_var(standard, elt)
			if enums is not None:
				res = matches_enum(data[elt], enums)
				if res[0] is False:
					msg = "[red]'%s' do(es) not belong to the possible values '%s'[/red]"%(', '.join(res[1]), ','.join(enums))
					d[elt]['enums']=(False, msg)
	
	return(d)
