@echo off

set pythonpath=C:\Python27

echo Transform a file
:: will output a file automatically named data-mapped.gpkg
%pythonpath%\python validator-cli.py -i data.gpkg -m data-mapping.csv

echo Transform a file
:: will generate a warning because of a wrong structure, so, no mapping done.
%pythonpath%\python validator-cli.py -i data.gpkg -m data-mapping2.csv

echo Transform a file and specify output name
%pythonpath%\python validator-cli.py -i data.gpkg -m data-mapping.csv -o my_output.gpkg

echo Transform a folder of CSVs
:: only the files with structure matching mapping file will be transformed
%pythonpath%\python validator-cli.py -d dir-csv -m data-mapping.csv

echo Transform a folder of GeoPackages
%pythonpath%\python validator-cli.py -d dir-gpkg -m data-mapping.csv

pause