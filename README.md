PACSMAN is a batch query/retrieve interface for the CareStream PACS at Lausanne University Hospital.

# Installation

PACSMAN is a Python application running on Ubuntu Linux, relying on the DCMTK suite of tools.

1. Install dcmtk `sudo apt-get install XXX CODE_HERE`
2. Download and install miniconda: `wget ... http://XXX/XXX.sh`, then `chmod u+x XXX.sh; ./XXX.sh`
3. XXX HOW TO OBTAIN THE CODE? GIT CLONE? XXX
3. Create a new python 3.6 environment using the yml file provided `conda create XXX`
4. Setup the configuration file (see below)
5. Verify the installation works by running this test: `XXX_TEST_WITH_EXAMPLE_CSV_HERE`


## Config file : 

The config file is a json file that should include keys
- `server_ip` (the server IP)
- `port` (the port)
- `AET` (The current station's application entity title)
- `server_AET` (The server's application entity title).

The AET and corresponding IP of the workstation should be declared on Carestream, including the storeable attribute.

# Running queries 
## Command line : 

 - Run the command : python pacsman.py --info info --save save --queryfile path_to_queryfile
 - The --info info option allows you to dump the information in the retrieved series into csv files. XXX what does `info` as the argument to `--info` mean? isn't --info just a switch?
 - The --save save option allows you to save the queryed dicom images. XXX same question here
 - The --queryfile path_to_queryfile option is mandatory and specifies which queryfile to use to query/retrieve.

Note : you can download the images without the --info option or only dump the info if --save option is not included.
o
 - Running the command above will download the dicom images by default into data folder of the project folder. 
 - You can specify the output directory by adding the option --out_directory path_to_output_directory.
 - You can also specify a different config file by adding the option --config path_to_config_file.

## Query file: 

The query file is a `.csv` file that should include one or many of these column names : 
- StudyDate : The study dates of this column should be in the format YYYYMMDD (e.g 19900912 which indicates the 12th of September 1990). <br> Note : Querying on a date range is supported. (e.g 20150201-20160201 will query on studies between 01/02/2015 and 01/02/2016 ) 
- StudyTime : The study time should be in the format HHMMSS (e.g 140500 which means 14:05:00)
⁻ SeriesDecription : The series description.
- PatientID :  The patient ID 
- ProtocolName : The protocol names.
- StudyInstanceUID : The Study Instance UID.
- PatientName : The patient name. (It is not recommanded to use this filter since there is no clear norm on how the patient names were stored on the pacs server)
- PatientBirthDate : Similarily to the StudyDate the date should be in format YYYYMMDD. Querying on date range is not supported for patient birth date.
- SeriesInstanceUID : The Series Instance UID
- ImageType : The image type as stored in the pacs server. (Note : using this filter significantly slows down the querying process. Use it only if absolutely necessary.)

Notes : 
- The query file could include one or many of the columns mentioned above. 
- If a line in a csv file contains an empty string on a particular columns, then, the query will not include the attribute corresponding to the column in question.
- The querying does not accept the value `*` alone on any attribute. However it can be used as a wildcard 
if other characters are provided, e.g. `ProtocolName` could be set to `BEAT_SelfNav*`

The query file can be built in Excel and exported to comma-separated values `.csv` format.

### Example : 

#### Example 1 : 

StudyDate,PatientID<br>
20150512,123421<br>
,45322 <br>
20180102,<br>

A csv file like the one written above will retrieve:
- Images correspoding to study done on 12/05/2015 and for patient with patientID 123421.
- Images of patient with patient ID 45322.
- Images of studies done the 02/01/2018.

#### Example 2 : 

StudyDate,patientID<br>
20150512,123421

The query for the csv file described above will fail since the column name patientID does not correspond to any allowed column mentioned above. (patientID should be PatientID)

#### Example 3 : 

StudyDate,PatientID<br>
20150512,*

The query for this csv file will fail because querying with values * is not allowed.

#### Example 4 : 

StudyDate,PatientID<br>
20150512-20150612,124588

Using this csv file, the query will retrieve images of the patient with patient ID 124588 and Study date between 12/05/2015 and 12/06/2015.

#### Example 5

XXX show an example with other fields than StudyDate or PatientID

# Anonymization : 
!! Add description of how to use anonymization here !!

# Converter : 

!! Add description of how to convert dicom images to nifti here !!