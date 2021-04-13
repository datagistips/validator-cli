# validator-cli

`validator-cli` is a command line interface to [validator](https://github.com/datagistips/validator). It enables you to :

- **control** your data (against a data schema)
- **transform** it (against a mapping file)

>

	usage: validator-cli.py [-h] [-d] {control,transform} input schema
	
	positional arguments:
	  {control,transform}  'control' data against a data schema or 'transform' data thanks to a mapping file
	  input                input file or directory (depends if you specified -d or not)
	  schema               data schema file path (if 'control' mode) or mapping file (if 'transform' mode)
	
	optional arguments:
	  -h, --help           show this help message and exit
	  -d, --directory      process entire directory

## Create your data schema file

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

### `type`
Valid types are :

- `string`
- `date`
- `datetime`
- `duration`
- `boolean`
- `number`
- `integer`

### `pattern`
Fill `pattern` column if your values must match a regular expression.

### `enum`
Fill `enum` if your values must belong to a list of values.

## Control your data with `control`

Let's suppose you have a data file named `data.csv` and a data schema named `schema.csv`

Control a single file against your data schema

	python validator-cli.py control data.csv schema.csv

You can also control an entire directory of files

	python validator-cli.py control -d my_dir schema.csv

See below to see the log output.

## Transform your data in :two: steps

You can use `validator` to transform your data to a particular schema. 

> ℹ️ Note transforming your data will only rename the columns, not modify your data cell contents.

### 1️⃣ Prepare your mapping file

The mapping file specifies the `source` fields and the `target` fields for the renaming of the data. 

You can create this file with the [validator GUI assistant](https://github.com/datagistips/validator)

![](https://github.com/datagistips/validator/raw/main/images/demo.gif)

The mapping file, in the above animation, is created and named `data-mapping.csv`

> ℹ️ Note that with the GUI Assistant, the data is also transformed at the same time. 

It has the following 2-column source-to-destination structure :

![](https://github.com/datagistips/validator/raw/main/images/mapping.png)

### :two: Transform your data with `transform`

You can transform your data using the GUI assistant, but you may wish transforming your data programmatically.

For this, `transform` will help you.

Now you have created a data mapping file with the GUI assistant, you can use the data mapping file to transform data in a script with `transform`.

### One file
This line will transform `data.csv` into `data-mapped.csv`, using source-target fields specifications contained in `mapping.csv`

	python validator-cli.py transform data.csv mapping.csv

### One directory
You can also transform files contained in a directory with `-d`

	python validator-cli.py transform -d my_dir mapping.csv

> ⚠️ Only data with the right structure will be transformed. Data with wrong structure will be ignored and noticed in the console.

## Log outputs

### `control` outputs
	python validator-cli.py control data3.csv schema3.csv

will output :

![](images/log-control.png)

### `transform` outputs
	python validator-cli.py transform data.csv mapping.csv

will output :

![](images/log-transform.png)

### Logs
You can redirect print messages to a log file like this :

	python validator-cli.py control data.csv schema.csv > log.txt
