@echo off

echo What is your input directory ?
set /p input_dir=

echo What is your mapping file ?
set /p mapping_file=

C:\Python27\python validator-cli.py -d %input_dir% -m %mapping_file%

pause