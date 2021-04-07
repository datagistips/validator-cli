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

The mapping file, named above `data-mapping.csv` specifies the source fields and the target fields for the renaming of the data. It has the following structure :

![](https://github.com/datagistips/validator/raw/main/images/mapping.png)

:two: Transform other data or pools of data programmatically using the mapping file with `validator-cli`

For instance, this line will transform `my_data.csv` into `my_data-mapped.csv`, using source-target fields specifications contained in `my_mapping_file.csv` file :

	python validator-cli.py -i my_data.csv -m my_mapping_file.csv

You can also transform a directory of data with `-d`. All the data files inside the directory, which respect the structure, will be transformed : 

	python validator-cli.py -d my_dir -m my_mapping_file.csv

> Notice only data with the right structure will be transformed

## Example scripts
- If you want to see example command lines, see [RUN-examples.bat](https://github.com/datagistips/validator-cli/blob/master/example-scripts/RUN-examples.bat) for data transformation examples
- You can run `validator-cli` manually, with prompts :
	- on a file with this [RUN-on-file batch](https://github.com/datagistips/validator-cli/blob/master/example-scripts/RUN-on-file.bat)
	- or on a directory with this [RUN-on-dir batch](https://github.com/datagistips/validator-cli/blob/master/example-scripts/RUN-on-dir.bat)
