@echo off

:: Single CSV transformation
C:\Python39\python validator-cli.py transform examples\datasets\1-single-file-csv\data.csv examples\datasets\1-single-file-csv\data-mapping.csv

:: Single GPKG transformation
C:\Python39\python validator-cli.py transform examples\datasets\2-single-file-gpkg\data.gpkg examples\datasets\2-single-file-gpkg\data-mapping.csv

:: Folder dir-csv transformation
C:\Python39\python validator-cli.py transform -d examples\datasets\4-directories\dir-csv examples\datasets\4-directories\data-mapping.csv

:: Folder dir-gpkg transformation
C:\Python39\python validator-cli.py transform -d examples\datasets\4-directories\dir-gpkg examples\datasets\4-directories\data-mapping.csv

pause