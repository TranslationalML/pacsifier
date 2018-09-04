#Imports.
from execute_commands import *
from numpy import unique
import sys
from tqdm import tqdm, trange
import os 
import warnings
from pandas import read_csv
import json
from sanity_checks import check_ids, check_dates, check_ip, check_port, check_AET, check_tuple
from datetime import datetime
from typing import Iterator
from cerberus import Validator
import csv
from typing import Dict, Any
import time

warnings.filterwarnings("ignore")

#Default paths to get the patient ids 
dump_path = "../files/query_patient_ids.dcm"
dump_txt_path = "../files/dump.txt"

tag_to_attribute = { # type : Dict[Any,Any] 
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
"(0008,0008)" : "ImageType"}

ALLOWED_FILTERS = list(tag_to_attribute.values())

########################################################################################################################
########################################################FUNCTIONS#######################################################
########################################################################################################################

def modify_query_parameters(
	server_ip : str = "88.202.185.144",
	port : int = 104,
	dump_path_ : str = dump_path,
	dump_txt_path_ : str = dump_txt_path,
	aec : str = "theServerAET") -> tuple:
	"""
	Modifies the command paramaters such as the dicom server ip, port number and the path to dump the results of the find. 
	Args : 
		server_ip (string) : server ip
		port (int) : port 
		dump_path_ (string) : path to where the generated .dcm file will be from dump2dcm command. 
		dump_txt_path_ (string) : path to where the text file from which the .dcm file will be generated.
		aec (string) : server_AET
	Returns : 
		tuple of strings : modified commands using input parameters.
	"""
	dump_query = "dump2dcm "+ dump_txt_path_+ " " + dump_path_
	scrape_patients_query = 'findscu '+ server_ip +' '+ str(port) +' -k 0010,0020={} --key 0008,0020={} --key 0008,0030 -aec '+ aec +' --patient ' + dump_path
	
	dump_query = dump_query.replace(
		dump_txt_path, dump_txt_path_).replace(
		dump_path, dump_path_)

	scrape_patients_query = scrape_patients_query.replace(
		"88.202.185.144", server_ip).replace(
		" 104", " "+str(port)).replace(
		dump_path, dump_path_).replace(
		"theServerAET", aec)

	return dump_query, scrape_patients_query

def get_and_store_patients(
	patient_ids : list,
	dates : list,
	text_file : str = "../files/patients.txt",
	server_ip : str = "88.202.185.144",
	port : int = 104,
	dump_path_ : str = dump_path,
	dump_txt_path_ : str = dump_txt_path,
	aec : str = "theServerAET"):
	"""
	Queries for patient ids passed as an argument and saves the resulting logs in a text file.
	Args : 
		patient_ids (list) : list of patient ids to be queried.
		dates (list) : list of study dates.
		text_file (string) : path to text file containing the logs generated by modify_query_parameters function.
		server_ip (string) : server ip.
		port (int) : port.
		dump_path_ (string) : path to where the generated .dcm file will be from dump2dcm command. 
		dump_txt_path_ (string) : path to where the text file from which the .dcm file will be generated.
		aec (string) : server_AET
	"""

	check_ip(server_ip)
	check_port(port)
	check_AET(aec , server = True)

	#delete patients text file if already exists.
	if os.path.isfile(text_file) : 
		os.remove(text_file)

	dump_query , scrape_patients_query = modify_query_parameters(server_ip, port, dump_path_, dump_txt_path_, aec)
	
	res = run(dump_query)

	for i, id_ in enumerate(patient_ids) : 
		
		check_ids(str(id_))
		res = run(scrape_patients_query.format(str(id_), dates[i]))
		write_file(res, file = text_file)

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
    
	id_table = []
	output_dict = Dict[Any,Any]

    #Iterate over text lines
	for line in readLineByLine(filename):

		sample_dict = { # type : Dict[Any,Any]
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


def parse_date(date : str) -> str : 
	"""
	Transforms a date passed as an argument to a date in format YYYYMMDD exaacly like the VR DA.
	Args : 
		date (string) : date in format dd/mm/yy (yy : two last digits of year)
	Returns : 
		list : parsed dates.
	"""

	check_dates(date)
	addition = "20"
	splitted = date.split("/")
	if int(splitted[2]) > datetime.now().year % 100 : 
		addition = "19"

	if len(splitted[0]) == 1 : splitted[0] = "0" + splitted[0]
	if len(splitted[1]) == 1 : splitted[1] = "0" + splitted[1]
	
	return addition + splitted[2] + splitted[1] + splitted[0]


def process_date(date : str) -> str : 
	"""
	Process a date according to its format (a simple date or a date range)
	Args : 
		date (string) : date or date range in format dd/mm/yy or dd/mm/yy-dd/mm/yy
	Returns : 
		string : processed date/date range.
	"""
	if date == "" : return ""
	#Case a date range was passed
	if len(str(date).split("-")) == 2 :
		dates = date.split("-")
		dates = [parse_date(dat) for dat in dates]
		return dates[0]+"-"+dates[1]
	
	#Case of a single date (not a date range)
	elif len(str(date).split("-")) == 1 :
		return parse_date(date) 
	
	#Otherwise raise an error.
	else : 
		raise ValueError("Invalid date input!")

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
def parse_birth_date(date : str) -> str :
	"""
	Parses the patients birth date into format YYYYMMDD.
	Args : 
		date (string) : date in format DD.MM.YYYY .
	Returns : 
		string : String in YYYYMMMDD format.
	"""
	if date == "" : return ""
	splitted_date = date.split(".")
	date_ret = splitted_date[2]+splitted_date[1]+splitted_date[0]
	return date_ret

def parse_table(table, allowed_filters) :
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

def process_names(name) : 
	"""
	Processing name to be the input of the query. 
	Args : 
		name (string) : patient name. 
	Returns : 
		string : patient name in the format it will be used in the query.
	"""
	splitted_name = name.upper().split(" ")
	new_name = "*"+ "^" +"*"+ splitted_name[-1]+"*"
	return new_name
########################################################################################################################
##########################################################MAIN##########################################################
########################################################################################################################


def main(argv) : 
	
	#Reading config file.
	with open('../files/config.json') as f:
		parameters = json.load(f)


	pacs_server = parameters["server_ip"] 
	port = int(parameters["port"])
	called_aet = parameters["AET"] 
	calling_aet = parameters["server_AET"]
	output_dir = parameters["directory"]

	#Reading table.
	table = read_csv("../files/"+argv[0]).fillna("")

	#processing command line inputs
	additional = argv[1:]
	additional = [add for add in additional if add[0] != '-']
	options = [opt for opt in argv[1:] if opt[0] == '-']

	info = False
	save = False

	if '-info' in options : 
		info = True

	if '-save' in options : 
		save = True

	check_table(table)

	#Flexible parsing.
	attributes_list = parse_table(table , ALLOWED_FILTERS)
	
	schema = {
	'PatientID' : {'type' : 'string', 'maxlength' : 64}, #Add more checking to the inputs.
	'StudyDate' : {'type' : 'string', 'maxlength' : 17},
	'StudyInstanceUID' : {'type' : 'string', 'maxlength' : 64},
	'SeriesInstanceUID' : {'type' : 'string', 'maxlength' : 64},
	'ProtocolName' : {'type' : 'string', 'maxlength' : 64},
	'PatientName': {'type' : 'string', 'maxlength' : 64},
	'SeriesDecription' : {'type' : 'string', 'maxlength' : 64},
	'AcquisitionDate' : {'type' : 'string', 'maxlength' : 8},
	'PatientBirthDate' : {'type' : 'string', 'maxlength' : 8}, 
	"DeviceSerialNumber" : {'type' : 'string', 'maxlength' : 64},
	"ImageType" : {'type' : 'string', 'maxlength' : 16}
	}

	validator = Validator(schema)

	for i, tuple_ in enumerate(attributes_list) : 
		
		print("Retrieving images for subject number ", i)
		
		check_tuple(tuple_)
		PATIENTID = str(tuple_["PatientID"])
		STUDYINSTANCEUID = tuple_["StudyInstanceUID"]
		SERIESINSTANCEUID  = tuple_["SeriesInstanceUID"]
		SERIESDESCRIPTION = tuple_["SeriesDecription"] 
		PROTOCOLNAME = tuple_["ProtocolName"]
		ACQUISITIONDATE = tuple_["AcquisitionDate"]
		STUDYDATE = process_date(tuple_["StudyDate"])
		PATIENTNAME = process_names(tuple_["PatientName"])
		PATIENTBIRTHDATE = parse_birth_date(tuple_ ["PatientBirthDate"])
		DEVICESERIALNUMBER = str(tuple_["DeviceSerialNumber"])
		IMAGETYPE = tuple_["ImageType"]
		
		

		inputs = {
		'PatientID' : PATIENTID, 
		'StudyDate' : STUDYDATE,
		'StudyInstanceUID' : STUDYINSTANCEUID,
		'SeriesInstanceUID' : SERIESINSTANCEUID,
		'ProtocolName' : PROTOCOLNAME,
		'PatientName': PATIENTNAME,
		'SeriesDecription' : SERIESDESCRIPTION,
		'AcquisitionDate' : ACQUISITIONDATE,
		'PatientBirthDate' : PATIENTBIRTHDATE,
		'DeviceSerialNumber' : DEVICESERIALNUMBER,
		'ImageType' : IMAGETYPE
		}


		if not validator.validate(inputs) : 
			raise ValueError("Invalid input file element at position "+ str(i) + " " + str(validator.errors))

		#Look for series of current patient and current study.
		find_series_res = find_series(
			called_aet,
			server_ip = pacs_server,
			server_AET = calling_aet,
			port = port,
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
			IMAGETYPE = IMAGETYPE)


		if os.path.isfile("current.txt") : 
			os.remove("current.txt")

		write_file(find_series_res, file = "current.txt")

		#Extract all series ids.
		series = process_text_files("current.txt")
		k = 0 
		#loop over series
		for serie in tqdm(series) :
			k+=1
			if k % 50 == 0 : 
				time.sleep(60)
			patient_dir = os.path.join(output_dir, "sub-"+ serie["PatientID"])

			if not os.path.isdir(patient_dir):
				os.mkdir(patient_dir)

			patient_study_output_dir = os.path.join(patient_dir, "ses-" + serie["StudyDate"] + serie["StudyTime"])

			if not os.path.isdir(patient_study_output_dir):
				os.mkdir(patient_study_output_dir)

			
			patient_serie_output_dir = os.path.join(patient_study_output_dir ,serie["SeriesDecription"])

			#Store all later retrieved files of current patient within the serie_id directory.
			if not os.path.isdir(patient_serie_output_dir):
				os.mkdir(patient_serie_output_dir)

		 
			#Retrieving files of current patient, study and serie.
			if save :
				get_res = get(
					called_aet,
					serie["StudyDate"],
					additional,
					server_ip = pacs_server,
					server_AET = calling_aet,
					port = port,
					PATIENTID = serie["PatientID"],
					STUDYINSTANCEUID = serie["StudyInstanceUID"],
					SERIESINSTANCEUID = serie["SeriesInstanceUID"],
					OUTDIR  = patient_serie_output_dir)
			if info : 
				
				#Writing series info to csv file.
				with open(patient_serie_output_dir+'.csv', 'w') as f: 
				    w = csv.DictWriter(f, serie.keys())
				    w.writeheader()
				    w.writerow(serie)

	if os.path.isfile("current.txt") : 
		os.remove("current.txt")

if __name__ == "__main__" :
	main(sys.argv[1:])