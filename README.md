# validator-cli

`validator-cli` is a command line interface to [validator](https://github.com/datagistips/validator). It enables you to :

- **control** your data (against a data schema)

>

	Usage: validator-cli.py control [OPTIONS] INPUTFILE SCHEMAFILE
	
	  inputfile : input file path or directory (depends if you specified
	  --directory)
	
	  schemafile : data schema file path, with field definitions, types, patterns and enum lists
	
	  --directory : type --directory if you want to control an entire directory
	
	Arguments:
	  INPUTFILE   [required]
	  SCHEMAFILE  [required]
	
	Options:
	  --directory / --no-directory  [default: False]
	  --help                        Show this message and exit.

- **transform** it (against a mapping file)
>

	Usage: validator-cli.py transform [OPTIONS] INPUTFILE MAPPINGFILE

	  inputfile : input file path or directory (depends if you specified
	  --directory)
	
	  mappingfile : data mapping file path. The data mapping file specifies
	  source field and target field names.

  	  --directory : type --directory if you want to control an entire directory
	
	Arguments:
	  INPUTFILE    [required]
	  MAPPINGFILE  [required]
	
	Options:
	  --directory / --no-directory  [default: False]
	  --outputdata TEXT
	  --help                        Show this message and exit.



## Control your data with `control`

### Create your data schema file

The data schema file used in validator is a simplified form of [frictionlessdata table schema](https://specs.frictionlessdata.io/table-schema/)

Create a CSV file (named `schema.csv` for example).

You will find a CSV example file [here](examples/datasets/schema.csv).

Here is an example content :

|name       |type     |pattern                    |enum           |
|-----------|---------|---------------------------|---------------|
|id_site    |integer  |                           |               |
|name       |character|                           |               |
|weight       |number  |                           |               |
|date      |date     |                           |               |
|ok        |boolean  |                           |               |
|values|character|                           |["a", "b", "c"]|
|city_code     |character|^([013-9]\d&#124;2[AB1-9])\d{3}$|               |
|siret     |character|^\d{14}$                   |               |

#### `type` column
Valid types are :

- `string`
- `integer`
- `number`
- `date`
- `datetime`
- `duration`
- `boolean`


#### `pattern` column 
Fill `pattern` column if your values must match a regular expression.

#### `enum` column
Fill `enum` if your values must belong to a list of values.

### Control your data against the data schema
Let's suppose you have a data file named `data.csv` and a data schema named `schema.csv`

Control a single file against your data schema

	python validator-cli.py control data.csv schema.csv

- `NOT FOUND` means that the column is not found either in the data file, either on the data schema file.
- `NOT VALID` means that the pattern or list of values is not respected

Here is an output :

![](images/log-control.png)

### Control all files in a directory
You can also control an entire directory of files

	python validator-cli.py control --directory my_dir schema.csv

## Transform your data with `transform`

You can use `validator` to transform your data to a particular schema. 

> ?????? Note transforming your data will only rename the columns, not modify your data cell contents.

### 1?????? Prepare your mapping file

The mapping file specifies the `source` fields and the `target` fields for the renaming of the data. 

You can create this file with the [validator GUI assistant](https://github.com/datagistips/validator)

![](https://github.com/datagistips/validator/raw/main/images/demo.gif)

The mapping file, in the above animation, is created and named `data-mapping.csv`

> ?????? Note that with the GUI Assistant, the data is also transformed at the same time. 

It has the following 2-column source-to-destination structure :

![](https://github.com/datagistips/validator/raw/main/images/mapping.png)

### :two: Transform your data with `transform`

You can transform your data using the GUI assistant, but you may wish transforming your data programmatically.

For this, `transform` will help you.

Now you have created a data mapping file with the GUI assistant, you can use the data mapping file to transform data in a script with `transform`.

This line will transform `data.csv` into `data-mapped.csv`, using source-target fields specifications contained in `mapping.csv`

	python validator-cli.py transform data.csv mapping.csv

Here is an output :

![](images/log-transform.png)


### Transform all files in a directory
You can also transform files contained in a directory with `--directory`

	python validator-cli.py transform -d my_dir mapping.csv

> ?????? Only data with the right structure will be transformed. Data with wrong structure will be ignored and noticed in the console.
