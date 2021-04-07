# validator-cli

`validator-cli` is a command line interface to [validator](https://github.com/datagistips/validator) to either control, either transform your data

	usage: validator-cli.py [-h] [-d] {control,transform} input schema
	
	positional arguments:
	  {control,transform}  'control' data against a data schema or 'transform' data thanks to a mapping file
	  input                input file or directory (depends if you specified -d or not)
	  schema               data schema file path (if 'control' mode) or mapping file (if 'transform' mode)
	
	optional arguments:
	  -h, --help           show this help message and exit
	  -d, --directory      process entire directory

## Control your data in :one: step

Control a single file against a data standard

	python validator-cli.py control data.csv standard.csv

Control a directory of files against a data standard

	python validator-cli.py control -d my_dir standard.csv

## Transform your data in :two: steps

1️⃣ Prepare your mapping file. For this, you can use the output of `control` to create it manually.

Or you can use the [validator GUI assistant](https://github.com/datagistips/validator).

![](https://github.com/datagistips/validator/raw/main/images/demo.gif)

The mapping file, named in the above animation `data-mapping.csv` specifies the source fields and the target fields for the renaming of the data. It has the following structure :

![](https://github.com/datagistips/validator/raw/main/images/mapping.png)

:two: Transform your data with `transform`

### One file
For instance, this line will transform `my_data.csv` into `my_data-mapped.csv`, using source-target fields specifications contained in `mapping.csv` file :

	python validator-cli.py transform data.csv -m mapping.csv

### One directory
You can also transform a directory of data with `-d`. All the data files inside the directory, which respect the structure, will be transformed : 

	python validator-cli.py transform -d my_dir -m mapping.csv

> Notice only data with the right structure will be transformed

## Example outputs
You can redirect print messages to a log file like this :

	python validator-cli.py control data.csv standard.csv > log.txt

### Control outputs
	python validator-cli.py control data.csv standard.csv

will produce :

	07/04/2021 19:05:23
	[KO] Data non valid
	
	Input data : data.csv
	Data schema : standard.csv
	
	Data columns : fid, id, lib, date, heure, ok, id_site
	Schema columns : id_site, date_maj, nb_sites, is_ok, libelle
	
	Data columns present in schema : id_site
	Data columns absent from schema : fid, id, lib, date, heure, ok
	
	Schema columns present in data : id_site
	Schema columns absent from data : date_maj, nb_sites, is_ok, libelle

### Transform outputs
	python validator-cli.py transform data.csv mapping.csv

will produce :

	07/04/2021 19:05:23
	Input data : data.csv
	   fid  id        lib        date                heure     ok  id_site
	0    1  11   à la mer  2021/03/02                  NaN   vrai      100
	1    2  10  printemps  2021/03/09  2021/03/09 00:00:00  false      100
	2    3  20        été         NaN                  NaN  false      100
	3    4  20        été         NaN                  NaN  false      100
	4    5  10         BD  2021/03/09  2021/03/09 00:00:00  false      100
	
	
	Mapping file : mapping.csv
	      from        to
	0  id_site   id_site
	1       ok       _ok
	2      lib      _lib
	3      fid      _fid
	4     date  date_maj
	5    heure    _heure
	6       id       _id
	
	
	Mapped data : examples\data-mapped.csv
	   _fid  _id       _lib    date_maj               _heure    _ok  id_site
	0     1   11   à la mer  2021/03/02                  NaN   vrai      100
	1     2   10  printemps  2021/03/09  2021/03/09 00:00:00  false      100
	2     3   20        été         NaN                  NaN  false      100
	3     4   20        été         NaN                  NaN  false      100
	4     5   10         BD  2021/03/09  2021/03/09 00:00:00  false      100
