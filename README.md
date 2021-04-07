# validator-cli

`validator-cli` is a command line interface to [validator](https://github.com/datagistips/validator)

	python validator-cli.py --help
	usage: validator-cli.py [-h] [-i INPUT] [-d INPUTDIR] -m MAPPING [-o OUTPUT]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -i INPUT, --input INPUT
	                        input file
	  -d INPUTDIR, --inputdir INPUTDIR
	                        input directory
	  -m MAPPING, --mapping MAPPING
	                        input mapping file path
	  -o OUTPUT, --output OUTPUT
	                        output file (if in single file mode, not directory
	                        mode)

## Transform your data in :two: steps

1️⃣ Prepare your mapping file with [validator GUI](https://github.com/datagistips/validator).

![](https://github.com/datagistips/validator/raw/main/images/demo.gif)

> The mapping file specifies the source field names and the target field names for the renaming of the data.

![](https://github.com/datagistips/validator/raw/main/images/mapping.png)

:two: Transform other data or pools of data programmatically using the mapping file with `validator-cli`

	python validator-cli.py --help
	usage: validator-cli.py [-h] [-i INPUT] [-d INPUTDIR] -m MAPPING [-o OUTPUT]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -i INPUT, --input INPUT
	                        input file
	  -d INPUTDIR, --inputdir INPUTDIR
	                        input directory
	  -m MAPPING, --mapping MAPPING
	                        input mapping file path
	  -o OUTPUT, --output OUTPUT
	                        output file (if in single file mode, not directory
	                        mode)

For instance :

	python validator-cli.py -i my_data.csv -m my_mapping_file.csv

You can also transform a folder of data.

	python validator-cli.py -d my_dir.csv -m my_mapping_file.csv

> Notice only data with the right structure will be transformed

## Example scripts
- If you want to see example scripts, to run validator programmatically, see [RUN-examples.bat](https://github.com/datagistips/validator-cli/blob/master/example-scripts/RUN-examples.bat) for data transformation examples
- You can run validator-cli manually validator-cli :
	- on a file with this [RUN-on-file batch](https://github.com/datagistips/validator-cli/blob/master/example-scripts/RUN-on-file.bat)
	- or on a directory with this [RUN-on-dir batch](https://github.com/datagistips/validator-cli/blob/master/example-scripts/RUN-on-dir.bat)
