This is a batch query/retrieve interface for the CareStream PACS at Lausanne University Hospital.


# Query/Retrieve : 
## Command line : 

 - Run the command : python pacsman.py --info info --save save --queryfile path_to_queryfile
 - The --info info option allows you to dump the information in the retrieved series into csv files.
 - The --save save option allows you to save the queryed dicom images.
 - The --queryfile path_to_queryfile option is mandatory and specifies which queryfile to use to query/retrieve.

Note : you can download the images without the --info option or only dump the info if --save option is not included.
o
 - Running the command above will download the dicom images by default into data folder of the project folder. 
 - You can specify the output directory by adding the option --out_directory path_to_output_directory.
 - You can also specify a different config file by adding the option --config path_to_config_file.

## Query file: 

The query file is a csv file that should include one or many of these column names : 
- StudyDate : The study dates of this column should be in the format YYYYMMDD (e.g 19900912 which indicates the 12th of September 1990)
- StudyTime : The study time should be in the format HHMMSS (e.g 140500 which means 14:05:00)
⁻ SeriesDecription : The series description.
- PatientID :  The patient ID 
- ProtocolName : The protocol names.
- StudyInstanceUID : The Study Instance UID.
- PatientName : The patient name. (It is not recommanded to use this filter since there is no clear norm on how the patient names were stored on the pacs server)
- PatientBirthDate : Similarily to the Study Date 
- SeriesInstanceUID : The Series Instance UID
- ImageType : The image type as stored in the pacs server. (Note : using this filter significantly slows down the querying process. Use it only if absolutely necessary.)

Notes : 
- The query file could include one or many of the columns mentioned above. 
- If a line in a csv file contains an empty string on a particular columns, then, the query will not include the attribute corresponding to the column in question.
- The querying does not accept * value on any attribute. 

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

## Config file : 

The config file is a json file that should include keys server_ip (the server ip), port (the port), AET (The current station's application entity title), server_AET (The server's application entity title).

# Anonymization : 
!! Add description of how to use anonymization here !!

# Converter : 

!! Add description of how to convert dicom images to nifti here !!