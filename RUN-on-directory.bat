@echo off

set pythonpath=C:\Python27

echo What is your input directory ?
set /p input_dir=

echo What is your mapping file ?
set /p mapping_file=

%pythonpath%\python validator-cli.py -d %input_dir% -m %mapping_file%

pause