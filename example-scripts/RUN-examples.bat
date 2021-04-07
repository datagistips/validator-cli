@echo off

set mapping_file=example-datasets/data-mapping.csv

echo Transform a file
:: will output a file automatically named data-mapped.gpkg
C:\Python27\python validator-cli.py -i example-datasets/data.gpkg -m %mapping_file%

echo Transform a file
:: will generate a warning because of a wrong structure, so, no mapping done.
C:\Python27\python validator-cli.py -i example-datasets/data.gpkg -m example-datasets/data-mapping2.csv

echo Transform a file and specify output name
C:\Python27\python validator-cli.py -i example-datasets/data.gpkg -m %mapping_file% -o example-datasets/my_output.gpkg

echo Transform a folder of CSVs
:: only the files with structure matching mapping file will be transformed
C:\Python27\python validator-cli.py -d example-datasets/dir-csv -m %mapping_file%

echo Transform a folder of GeoPackages
C:\Python27\python validator-cli.py -d example-datasets/dir-gpkg -m %mapping_file%

pause