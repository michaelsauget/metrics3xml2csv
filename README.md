## The metrics3xml2csv tool 

It's a simple python code to transform the Eclipse Metrics 3 XML extractions into a well formatted CSV file. This allows
the analysis of multiple packages into a single Excel document.

### Dependencies
Only Python3.6 or later for the command line version, or Docker for the second option

### Command-line
#### Options
- -o to specify the output CSV file path
- -f to specify the XML file paths you want to merge into a CSV

A working example would be:
```shell script
$ python metrics2csv.py -o ./output.csv -f xml/xml1.xml xml/xml2.xml xml/xml3.xml 
```


### Using Docker
You only have to specify the XML files you want to merge into your CSV. You can put 1 or as many as you wish.
```shell script
$ docker build .
$ docker run -v ${PWD}/output:/usr/workspace/output metrics2csv -f <PATH_TO_FILE_1> <PATH_TO_FILE_2> <PATH_TO_FILE_3> 
```

A working example would be:
```shell script
$ docker build .
$ docker run -v ${PWD}/output:/usr/workspace/output metrics2csv -f path/to/file_1.xml pathto/file_2.xml path/to/file_n.xml 
```

The Docker version will put your output CSV file in the output folder
