# validator-cli

`Validator-cli` is a command line interface to [validator](https://github.com/datagistips/validator)

	C:\Python27\python.exe validator-cli.py --help
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

## Transform your data in 3 steps

Prepare your mapping file with validator GUI.

![](https://github.com/datagistips/validator/raw/main/images/demo.gif)

> The mapping file specifies the source field names and the target field names for the renaming of the data.

![](https://github.com/datagistips/validator/raw/main/images/mapping.png)

Then, transform other data or pools of data programmatically using the mapping file with `validator-cli`

	C:\Python27\python.exe validator-cli.py --help
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

	python validator-cli.py -i my_dir.csv -m my_mapping_file.csv

> Notice only data with the right structure will be transformed

## Example scripts
