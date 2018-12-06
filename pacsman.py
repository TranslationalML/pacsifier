#Imports.
from execute_commands import *
from numpy import unique
import sys
from tqdm import tqdm, trange
import os 
import warnings
from pandas import read_csv, DataFrame
import json
from sanity_checks import check_ids, check_date, check_date_range, check_ip, check_port, check_AET, check_tuple, check_config_file
from datetime import datetime
from typing import Iterator
from cerberus import Validator
import csv
from typing import Dict, Any,Type
import time
import argparse


warnings.filterwarnings("ignore")

tag_to_attribute = { # type : Dict[str,str]
"(0008,0020)" : "StudyDate",
"(0008,0030)" : "StudyTime",
"(0008,103e)" : "SeriesDescription",
"(0010,0020)" : "PatientID",
"(0018,1030)" : "ProtocolName",
"(0020,000d)" : "StudyInstanceUID",
"(0020,000e)" : "SeriesInstanceUID",
"(0010,0010)" : "PatientName",
"(0010,0030)" : "PatientBirthDate",
"(0018,1000)" : "DeviceSerialNumber", 
"(0008,0022)" : "AcquisitionDate",
"(0008,0060)" : "Modality",
"(0008,0008)" : "ImageType",
"(0020,0011)" : "SeriesNumber",
"(0008,1030)" : "StudyDescription",
"(0008,0050)" : "AccessionNumber",
"(0018,0024)" : "SequenceName"}

ALLOWED_FILTERS = list(tag_to_attribute.values())
ALLOWED_FILTERS.append("new_ids")
########################################################################################################################
########################################################FUNCTIONS#######################################################
########################################################################################################################

def readLineByLine(filename : str) -> Iterator[str]:
	"""
	Returns a list of lines of textfile located at path filename.
	Args : 
		filename (string) : path to textfile to be read.
	Returns : 
		Iterator : list of text lines in file.
	"""
	with open(filename, 'r', encoding = "utf8") as f:
		for line in f:
			yield line.strip('\n')

def parse_findscu_dump_file(filename : str) -> list:
	"""
	Extracts all useful information from the text file generated by dumping the output of the findscu command.
	Args : 
		filename (string) : path to textfile to be read.
	Returns : 
		list : list dictionaries each containing the attributes of a series.
	"""
	start = False
    
	id_table = [] # type : List[str]
	output_dict = {"":""} # type : Dict[str,str]

    #Iterate over text lines
	for line in readLineByLine(filename):

		sample_dict = { # type : Dict[str,str]
		"StudyDate" : "",
		"StudyTime" : "",
		"SeriesDescription" : "",
		"PatientID" : "",
		"ProtocolName": "",
		"StudyInstanceUID" : "",
		"PatientName" : "",
		"PatientBirthDate" : "",
		"SeriesInstanceUID" : "",
		"DeviceSerialNumber" : "",
		"Modality" : "",
		"ImageType" : "",
		"SeriesNumber" : "",
		"StudyDescription" : "",
		"AccessionNumber" : "",
		"SequenceName" : ""}

		if "------------" in line or "Releasing Association" in line : 
			if start : id_table.append(output_dict)
			
			start = True
			output_dict = sample_dict
			continue

		if not start : continue
		for tag in sorted(tag_to_attribute.keys()) : 

			#if current line contains a given tag then extract information from it.
			if tag in line:
				
				item = ""
				try : 
					item = line.split("[")[1].split("]")[0].replace(" ","").replace("'", "_").replace("/","")

				#In case line.split gives a list of length less that 4 pass to next line.
				except IndexError : pass

				if item == "(no" : continue
				output_dict[tag_to_attribute[tag]] = item
		
	return id_table

def check_query_table_allowed_filters(table : DataFrame, allowed_filters : list = ALLOWED_FILTERS) -> None : 
	"""
	Checks if the csv table passed as input has only attributes that are allowed.
	Args : 
		table (DataFrame) : table containing all filters.
		allowed_filters (list) : list of allowed attribute names.
	"""
	cols = table.columns
	for col in cols : 

		if col not in allowed_filters : 
			raise ValueError("Attribute "+ col +" not allowed! Please check the input table's column names.")

	return

def parse_query_table(table : DataFrame , allowed_filters : list = ALLOWED_FILTERS) -> list :
	"""
	Takes the table passed as script input and parse it using its attributes in the query/retrieve command.
	Args : 
		table (DataFrame) : input csv table. 
		allowed_filters (list) : list of allowed attributes to be filtered.
	Returns : 
		list : list of dictionaries each containing the corresponding value of each attribute in allowed_filters. 
			   In case an attribute has no corresponding column in the csv table, an empty string is given. 
	"""
	attributes_list = []
	for idx in table.index :
		
		#Initializing item dictionary.
		filter_dictionary= {filter_ : "" for filter_ in allowed_filters}

		for col in table.columns :
			filter_dictionary[col] = table.loc[idx, col]
			
		attributes_list.append(filter_dictionary)

	return attributes_list

def process_person_names(name : str) -> str : 
	"""
	Processing name to be the input of the query. 
	Args : 
		name (string) : patient's name. 
	Returns : 
		string : patient name in the format it will be used in the query.
	"""
	if name == "" : return ""
	splitted_name = name.upper().split(" ")
	new_name = "*"+ splitted_name[-1]
	return new_name

########################################################################################################################
##########################################################MAIN##########################################################
########################################################################################################################

def main(argv):
	
	parser = argparse.ArgumentParser()
	
	parser.add_argument('--config',"-c", help='Configuration file path', default=os.path.join("..","files","config.json"))
	parser.add_argument('--save', "-s", action='store_true', help = "The images will be stored")
	parser.add_argument('--info', "-i", action ='store_true', help = "The info csv files will be stored")
	parser.add_argument("--queryfile", "-q", help = 'Path to query file')
	parser.add_argument("--out_directory", "-d" , help = 'Output directory where images will be saved', default = os.path.join("..","data"))
	
	args = parser.parse_args()
	
	config_path = args.config
	
	#Reading config file.
	try:
		with open(config_path) as f:
			parameters = json.load(f)
		check_config_file(parameters)

		pacs_server = parameters["server_ip"] 
		port = int(parameters["port"])
		move_port = int(parameters["move_port"])
		client_AET = parameters["AET"]		
		server_AET = parameters["server_AET"]	
		batch_wait_time = int(parameters["batch_wait_time"])
		batch_size = int(parameters["batch_size"])
	except FileNotFoundError: 		
		args.config = None
		pass
		
	output_dir = args.out_directory
	
	#Check the case where the queryfile option is missing. If it is the case print help.
	if args.queryfile == None or args.config == None: 
		print("Missing mandatory parameter --queryfile or --config!")
		parser.print_help()
		sys.exit()

	#Reading table.
	table = read_csv(args.queryfile, dtype=str).fillna("")
	
	check_query_table_allowed_filters(table)

	#Flexible parsing.
	attributes_list = parse_query_table(table , ALLOWED_FILTERS)
	
	schema = {
	'PatientID' 		: {'type' : 'string', 'maxlength' : 64},
	'StudyDate' 		: {'type' : 'string', 'maxlength' : 17},
	'StudyInstanceUID' 	: {'type' : 'string', 'maxlength' : 64},
	'SeriesInstanceUID' : {'type' : 'string', 'maxlength' : 64},
	'ProtocolName' 		: {'type' : 'string', 'maxlength' : 64},
	'PatientName'		: {'type' : 'string', 'maxlength' : 64},
	'SeriesDescription' : {'type' : 'string', 'maxlength' : 64},
	'AcquisitionDate' 	: {'type' : 'string', 'maxlength' : 8 },
	'PatientBirthDate' 	: {'type' : 'string', 'maxlength' : 8 },
	"DeviceSerialNumber": {'type' : 'string', 'maxlength' : 64},
	"Modality"			: {'type' : 'string', 'maxlength' : 16},
	"SeriesNumber"		: {'type' : 'string', 'maxlength' : 12},
	"StudyDescription" 	: {'type' : 'string', 'maxlength' : 64},
	"AccessionNumber"	: {'type' : 'string', 'maxlength' : 16}, 
	"SequenceName"		: {'type' : 'string', 'maxlength' : 64}	
	#"ImageType" 		: {'type' : 'string', 'maxlength' : 16} The norm says it is a CS but apparently it is something else on Chuv PACS server.
	}

	validator = Validator(schema)
	counter = 0 
	for i, tuple_ in enumerate(attributes_list):
		
		print("Retrieving images for element number ", i+1)
		
		check_tuple(tuple_)

		PATIENTID = tuple_["PatientID"]
		STUDYINSTANCEUID = tuple_["StudyInstanceUID"]
		SERIESINSTANCEUID  = tuple_["SeriesInstanceUID"]
		SERIESDESCRIPTION = tuple_["SeriesDescription"] 
		PROTOCOLNAME = tuple_["ProtocolName"]
		ACQUISITIONDATE = tuple_["AcquisitionDate"]
		STUDYDATE = tuple_["StudyDate"]
		PATIENTNAME = process_person_names(tuple_["PatientName"])
		PATIENTBIRTHDATE = tuple_ ["PatientBirthDate"]
		DEVICESERIALNUMBER = tuple_["DeviceSerialNumber"]
		IMAGETYPE = tuple_["ImageType"]
		MODALITY = tuple_["Modality"]
		SERIESNUMBER = tuple_["SeriesNumber"]
		STUDYDESCRIPTION = tuple_["StudyDescription"]
		ACCESSIONNUMBER = tuple_["AccessionNumber"]
		NEW_ID = tuple_["new_ids"]
		SEQUENCENAME = tuple_["SequenceName"]

		inputs = {
		'PatientID' 		: PATIENTID, 
		'StudyDate' 		: STUDYDATE,
		'StudyInstanceUID' 	: STUDYINSTANCEUID,
		'SeriesInstanceUID' : SERIESINSTANCEUID,
		'ProtocolName' 		: PROTOCOLNAME,
		'PatientName'		: PATIENTNAME,
		'SeriesDescription' : SERIESDESCRIPTION,
		'AcquisitionDate' 	: ACQUISITIONDATE,
		'PatientBirthDate' 	: PATIENTBIRTHDATE,
		'DeviceSerialNumber': DEVICESERIALNUMBER,
		'Modality' 			: MODALITY,
		'SeriesNumber'		: SERIESNUMBER,
		'StudyDescription'	: STUDYDESCRIPTION,
		'AccessionNumber'	: ACCESSIONNUMBER,
		'SequenceName'		: SEQUENCENAME
		#'ImageType' 		: IMAGETYPE
		}
		
		if not validator.validate(inputs) : 
			raise ValueError("Invalid input file element at position "+ str(i) + " " + str(validator.errors))

		check_date_range(STUDYDATE)
		check_date_range(ACQUISITIONDATE)
		check_date(PATIENTBIRTHDATE)

		QUERYRETRIVELEVEL = "SERIES"
		if IMAGETYPE != "" or SEQUENCENAME == "":
			QUERYRETRIVELEVEL = "IMAGE"

		# check if we can ping the PACS
		echo_res =  echo(
		server_ip = pacs_server,
		port = port,
		server_AET = server_AET)
		if not echo_res :
			raise RuntimeError("Cannot associate with PACS server")
		
		#Look for series of current patient and current study.
		find_series_res = find(
			client_AET,
			server_ip = pacs_server,
			server_AET = server_AET,
			port = port,
			QUERYRETRIVELEVEL = QUERYRETRIVELEVEL,
			PATIENTID = PATIENTID,
			STUDYUID = STUDYINSTANCEUID,
			SERIESINSTANCEUID = SERIESINSTANCEUID,
			SERIESDESCRIPTION = SERIESDESCRIPTION,
			PROTOCOLNAME = PROTOCOLNAME, 
			ACQUISITIONDATE = ACQUISITIONDATE, 
			STUDYDATE = STUDYDATE,
			PATIENTNAME = PATIENTNAME,
			PATIENTBIRTHDATE = PATIENTBIRTHDATE,
			DEVICESERIALNUMBER = DEVICESERIALNUMBER,
			MODALITY = MODALITY,
			IMAGETYPE = IMAGETYPE,
			STUDYDESCRIPTION = STUDYDESCRIPTION,
			ACCESSIONNUMBER = ACCESSIONNUMBER,
			SEQUENCENAME = SEQUENCENAME) 

		if os.path.isfile("current.txt") : 
			os.remove("current.txt")

		write_file(find_series_res, file = "current.txt")

		#Extract all series ids.
		series = parse_findscu_dump_file("current.txt")

		
		#loop over series
		for serie in tqdm(series) :
			
			counter+=1
			if counter % batch_size == 0: 
				time.sleep(batch_wait_time)

			patient_dir = os.path.join(output_dir, "sub-"+ serie["PatientID"])
			
			#Make the patient folder.
			if not os.path.isdir(patient_dir) and (args.save or args.info):
				os.mkdir(patient_dir)

			if NEW_ID != "" : 
				file = open(os.path.join(patient_dir,"new_id.txt"), "w") 
				file.write(str(NEW_ID)) 
				file.close() 

			patient_study_output_dir = os.path.join(patient_dir, "ses-" + serie["StudyDate"] + serie["StudyTime"])

			#Make the Study folder.
			if not os.path.isdir(patient_study_output_dir) and (args.save or args.info):
				os.mkdir(patient_study_output_dir)

			#Name the series folder after the SeriesDescription.
			folder_name = serie["SeriesDescription"]

			#If the StudyDescription is an empty string name the folder No_series_description.
			if folder_name == "" : folder_name = "No_series_description"
			patient_serie_output_dir = os.path.join(patient_study_output_dir ,serie["SeriesNumber"].zfill(4)+"-"+folder_name.replace("<","").replace(">","").replace(":","").replace("/",""))

			#Store all later retrieved files of current patient within the serie_id directory.
			if not os.path.isdir(patient_serie_output_dir) and (args.save or args.info):
				os.mkdir(patient_serie_output_dir)

			#Retrieving files of current patient, study and serie.
			if args.save :
				get_res = get(
					client_AET,
					serie["StudyDate"],
					server_ip = pacs_server,
					server_AET = server_AET,
					port = port,
					PATIENTID = serie["PatientID"],
					STUDYINSTANCEUID = serie["StudyInstanceUID"],
					SERIESINSTANCEUID = serie["SeriesInstanceUID"],
					move_port = move_port,
					OUTDIR  = patient_serie_output_dir)

			if args.info : 

				#Writing series info to csv file.
				with open(patient_serie_output_dir+'.csv', 'w') as f: 
					w = csv.DictWriter(f, serie.keys())
					w.writeheader()
					w.writerow(serie)
			
			if os.path.isfile("current.txt"): 
				os.remove("current.txt")
				
if __name__ == "__main__" :
	main(sys.argv[1:])