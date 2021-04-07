@echo off

echo What is your input data ?
set /p input_data=

echo What is your mapping file ?
set /p mapping_file=

echo Type the name of your output data
set /p output_data=

if [%output_data%] == [] goto no_output_name
::C:\Python27\python validator-cli.py -i %input_data% -m %mapping_file% -o %output_data%

:no_output_name
C:\Python27\python validator-cli.py -i %input_data% -m %mapping_file%

:end

pause