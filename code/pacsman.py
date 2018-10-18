#Imports.
from execute_commands import *
from numpy import unique
import sys
from tqdm import tqdm, trange
import os 
import warnings
from pandas import read_csv
import json
from sanity_checks import check_ids, check_date, check_date_range, check_ip, check_port, check_AET, check_tuple
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
"(0008,103e)" : "SeriesDecription",
"(0010,0020)" : "PatientID",
"(0018,1030)" : "ProtocolName",
"(0020,000d)" : "StudyInstanceUID",
"(0020,000e)" : "SeriesInstanceUID",
"(0010,0010)" : "PatientName",
"(0010,0030)" : "PatientBirthDate",
"(0018,1000)" : "DeviceSerialNumber", 
"(0008,0022)" : "AcquisitionDate",
"(0008,0060)" : "Modality",
"(0008,0008)" : "ImageType"}

ALLOWED_FILTERS = list(tag_to_attribute.values())

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

def process_text_files(filename : str) -> list:
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
		"SeriesDecription" : "",
		"PatientID" : "",
		"ProtocolName": "",
		"StudyInstanceUID" : "",
		"PatientName" : "",
		"PatientBirthDate" : "",
		"SeriesInstanceUID" : "",
		"DeviceSerialNumber" : "",
		"Modality" : "",
		"ImageType" : ""} 

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

def check_table(table, allowed_filters : list = ALLOWED_FILTERS) : 
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


def parse_table(table , allowed_filters : list = ALLOWED_FILTERS) -> list :
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

def process_names(name : str) -> str : 
	"""
	Processing name to be the input of the query. 
	Args : 
		name (string) : patient name. 
	Returns : 
		string : patient name in the format it will be used in the query.
	"""
	splitted_name = name.upper().split(" ")
	new_name = "*"+ "^" +"*"+ splitted_name[-1]
	return new_name

########################################################################################################################
##########################################################MAIN##########################################################
########################################################################################################################

def main(argv):
	additional = []
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', help='configuration file path')
	parser.add_argument('--save', help='save images')
	parser.add_argument('--info', help ='save images info')
	parser.add_argument("--queryfile", help = 'database')
	parser.add_argument("--out_directory", help = 'Output directory where images will be saved')
	args = parser.parse_args()




	config_path = args.config
	if config_path == None : config_path = "../files/config.json"
	#Reading config file.
	with open(config_path) as f:
		parameters = json.load(f)

	"""with open("../files/new_ids.csv") as f: 
					reader = csv.reader(f)
					new_ids = list(reader)"""
	
	#new_ids = [id_[0].replace(" ","") for id_ in new_ids]

	id_tuples = {}

	# XXX VALIDATE INPUT PARAMETERS

	pacs_server = parameters["server_ip"] 
	port = int(parameters["port"])
	move_port = int(parameters["move_port"])
	client_AET = parameters["AET"]		
	server_AET = parameters["server_AET"]
	output_dir = os.path.join("..","data")	

	#processing command line inputs
	
	"""	additional = argv[1:]
	additional = [add for add in additional if add[0] != '-']
	options = [opt for opt in argv[1:] if opt[0] == '-']
	"""

	info = False
	save = False

	if args.info == "info" : info = True
	if args.save == "save" : save = True
	if args.out_directory != None : output_dir = args.out_directory

	#Reading table.
	table = read_csv(args.queryfile, dtype=str).fillna("")
	
	check_table(table)

	#Flexible parsing.
	attributes_list = parse_table(table , ALLOWED_FILTERS)
	
	schema = {
	'PatientID' 		: {'type' : 'string', 'maxlength' : 64},
	'StudyDate' 		: {'type' : 'string', 'maxlength' : 17},
	'StudyInstanceUID' 	: {'type' : 'string', 'maxlength' : 64},
	'SeriesInstanceUID' : {'type' : 'string', 'maxlength' : 64},
	'ProtocolName' 		: {'type' : 'string', 'maxlength' : 64},
	'PatientName'		: {'type' : 'string', 'maxlength' : 64},
	'SeriesDecription' 	: {'type' : 'string', 'maxlength' : 64},
	'AcquisitionDate' 	: {'type' : 'string', 'maxlength' : 8 },
	'PatientBirthDate' 	: {'type' : 'string', 'maxlength' : 8 },
	"DeviceSerialNumber": {'type' : 'string', 'maxlength' : 64},
	"Modality"			: {'type' : 'string', 'maxlength' : 16}
	#"ImageType" 		: {'type' : 'string', 'maxlength' : 16} The norm says it is a CS but apparently it is something else on Chuv PACS server.
	}

	validator = Validator(schema)

	for i, tuple_ in enumerate(attributes_list):
		
		print("Retrieving images for study number ", i)
		
		check_tuple(tuple_)
		PATIENTID = tuple_["PatientID"]
		STUDYINSTANCEUID = tuple_["StudyInstanceUID"]
		SERIESINSTANCEUID  = tuple_["SeriesInstanceUID"]
		SERIESDESCRIPTION = tuple_["SeriesDecription"] 
		PROTOCOLNAME = tuple_["ProtocolName"]
		ACQUISITIONDATE = tuple_["AcquisitionDate"]
		STUDYDATE = tuple_["StudyDate"]
		PATIENTNAME = process_names(tuple_["PatientName"])
		PATIENTBIRTHDATE = tuple_ ["PatientBirthDate"]
		DEVICESERIALNUMBER = tuple_["DeviceSerialNumber"]
		IMAGETYPE = tuple_["ImageType"]
		MODALITY = tuple_["Modality"]

		inputs = {
		'PatientID' 		: PATIENTID, 
		'StudyDate' 		: STUDYDATE,
		'StudyInstanceUID' 	: STUDYINSTANCEUID,
		'SeriesInstanceUID' : SERIESINSTANCEUID,
		'ProtocolName' 		: PROTOCOLNAME,
		'PatientName'		: PATIENTNAME,
		'SeriesDecription'  : SERIESDESCRIPTION,
		'AcquisitionDate' 	: ACQUISITIONDATE,
		'PatientBirthDate' 	: PATIENTBIRTHDATE,
		'DeviceSerialNumber': DEVICESERIALNUMBER,
		'Modality' 			: MODALITY
		#'ImageType' 		: IMAGETYPE
		}
		
		if not validator.validate(inputs) : 
			raise ValueError("Invalid input file element at position "+ str(i) + " " + str(validator.errors))

		check_date_range(STUDYDATE)
		check_date_range(ACQUISITIONDATE)
		check_date(PATIENTBIRTHDATE)

		QUERYRETRIVELEVEL = "SERIES"
		if IMAGETYPE != "":
			QUERYRETRIVELEVEL = "IMAGE"

		# check if we can ping the PACS
		echo_res =  echo(
			server_ip = pacs_server,
			port = port,
			client_AET = client_AET)
		if not echo_res:
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
			IMAGETYPE = IMAGETYPE)

		if os.path.isfile("current.txt") : 
			os.remove("current.txt")

		write_file(find_series_res, file = "current.txt")

		#Extract all series ids.
		series = process_text_files("current.txt")
		counter = 0 
		
		#loop over series
		for serie in tqdm(series) :
			#study_counter = 0 
			counter+=1
			if counter % 50 == 0 : 
				time.sleep(60)

			patient_dir = os.path.join(output_dir, "sub-"+ serie["PatientID"])
			
			"""if study_counter == 0 : 
													id_tuples[serie["PatientID"]] = new_ids[i]
													study_counter += 1
									"""
			if not os.path.isdir(patient_dir):
				os.mkdir(patient_dir)

			patient_study_output_dir = os.path.join(patient_dir, "ses-" + serie["StudyDate"] + serie["StudyTime"])

			if not os.path.isdir(patient_study_output_dir):
				os.mkdir(patient_study_output_dir)
			
			folder_name = serie["SeriesDecription"]

			if folder_name == "" : folder_name = "No_series_description"
			patient_serie_output_dir = os.path.join(patient_study_output_dir ,folder_name.replace("<","").replace(">","").replace(":","").replace("/",""))

			#Store all later retrieved files of current patient within the serie_id directory.
			if not os.path.isdir(patient_serie_output_dir):
				os.mkdir(patient_serie_output_dir)
		 
			#Retrieving files of current patient, study and serie.
			if save :
				get_res = get(
					client_AET,
					serie["StudyDate"],
					additional,
					server_ip = pacs_server,
					server_AET = server_AET,
					port = port,
					PATIENTID = serie["PatientID"],
					STUDYINSTANCEUID = serie["StudyInstanceUID"],
					SERIESINSTANCEUID = serie["SeriesInstanceUID"],
					move_port = move_port,
					OUTDIR  = patient_serie_output_dir)
			if info : 
			
				#Writing series info to csv file.
				with open(patient_serie_output_dir+'.csv', 'w') as f: 
				    w = csv.DictWriter(f, serie.keys())
				    w.writeheader()
				    w.writerow(serie)

	"""if os.path.isfile("current.txt") : 
					os.remove("current.txt")"""

	
	"""with open("../files/id_mapper.json","w") as fp: 
					json.dump(id_tuples,fp)"""

if __name__ == "__main__" :
	main(sys.argv[1:])