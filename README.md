This is a batch query/retrieve interface for the CareStream PACS at Lausanne University Hospital.

How to use : 

# Query/Retrieve : 
## Command line : 

 - Run the command : python pacsman.py --info info --save save --queryfile path_to_queryfile
 - The --info info option allows you to dump the information in the retrieved series into csv files.
 - The --save save option allows you to save the queryed dicom images.
 - The --queryfile path_to_queryfile option is mandatory and specifies which queryfile to use to query/retrieve.

Note : you can download the images without the --info option or only dump the info if --save option is not included.

 - Running the command above will download the dicom images by default into data folder of the project folder. 
 - You can specify the output directory by adding the option --out_directory path_to_output_directory.
 - You can also specify a different config file by adding the option --config path_to_config_file.

## Query file: 

