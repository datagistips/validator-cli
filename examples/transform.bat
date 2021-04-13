@echo off

:: Single file transformation
C:\Python39\python validator-cli.py transform examples\datasets\data.csv examples\datasets\data-mapping.csv

:: Folder dir-csv transformation
C:\Python39\python validator-cli.py transform -d examples\datasets\dir-csv examples\datasets\data-mapping.csv

:: Folder dir-gpkg transformation
C:\Python39\python validator-cli.py transform -d examples\datasets\dir-gpkg examples\datasets\data-mapping.csv

pause