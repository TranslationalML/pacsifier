#Imports .
from datetime import date
import os
import warnings
from sanity_checks import check_parameters_inputs, check_ids, check_dates, check_port
import shlex
import subprocess
from typing import List, Dict, Tuple
from sanity_checks import check_filter

warnings.filterwarnings("ignore")

#Query default parameters
PATIENTID = '"PAT004"'
PATIENTID_2, STUDYDESC = '"PAT004"',""
PATIENTID_3, STUDYINSTANCEUID, SERIESINSTANCEUID, OUTDIR = '"PAT004"', '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.461"', '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.462"', "../data" 

PARAMETERS = "88.202.185.144 104 -aec theServerAET -aet MY_AET"

#Query squeletons.
echo_command = 'echoscu -ll trace {}'
find_series_command= 'findscu -v {} --study -k QueryRetrieveLevel=SERIES -k 0010,0020={} -k 10,10 -k 0020,000d={} --key 0020,000e={} --key 0008,103E={} --key 18,1030={} --key 8,22={} --key 0008,0020={} --key 0010,0010={} --key 10,30={} --key 8,30'
find_studies_command = 'findscu -v {} --study -k QueryRetrieveLevel=STUDY --key 0010,0020={} --key 10,10 --key 0020,000d --key 0008,0061 --key 0008,0030 --key 0008,0020={} --key 0020,1206'
move_command = 'movescu -ll trace {} -aem {} -k 0008,0052="PATIENT" --patient --key 0010,0020={} --key 0020,000d={} --key 0020,000e={} --key 0008,0020={} --port {} -od {}'

######################################################################################################################## 
########################################################FUNCTIONS#######################################################
########################################################################################################################

def echo(
	AET : str,
	server_ip : str = "88.202.185.144",
	server_AET : str = "theServerAET",
	port : int = 104) -> str: 
	"""
	Builds a command line string for echoscu using the parameters passed as arguments.
	Args : 
		AET (string) : Called AET
		server_ip (string) : server ip
		server_AET (string) : server_AET
		port (int) : port 
	Returns : 
		string : The log lines.
	"""

	modified_params = replace_default_params(PARAMETERS, AET, server_ip , server_AET , port)
	command = echo_command.format(modified_params)

	return run(command)

def find_series(
	AET : str,
	server_ip : str = "88.202.185.144",
	server_AET : str = "theServerAET",
	port : int = 104, 
	PATIENTID : str = "",
	STUDYUID : str = "",
	SERIESINSTANCEUID : str ="",
	SERIESDESCRIPTION : str ="", 
	PROTOCOLNAME : str = "", 
	ACQUISITIONDATE : str = "", 
	PATIENTNAME : str = "",
	PATIENTBIRTHDATE : str = "",
	STUDYDATE : str = "") -> str : 
	"""
  	builds a query for findscu of QueryRetrieveLevel of series using the parameters passed as arguments.
  	Args : 
		AET (string) : Called AET
		server_ip (string) : server ip
		server_AET (string) : server_AET
		port (int) : port 
		PATIENTID (string) : patient id 
		STUDYUID (string) : Study unique idetifier.
		SERIESINSTANCEUID (string) : Series Instance UID.
		SERIESDESCRIPTION (string) : Series Description.
		PROTOCOLNAME (string) : protocol name.
		ACQUISITIONDATE (string) : Acquisition Date.
		STUDYDATE (string) : Study Date.
	Returns : 
		string : The log lines.
	"""

	#check_ids(PATIENTID)
	#check_ids(STUDYUID , attribute = "Study instance UID")

	modified_params = replace_default_params(PARAMETERS, AET, server_ip , server_AET , port)
	command = find_series_command.format(
		modified_params,
		PATIENTID,
		STUDYUID,
		SERIESINSTANCEUID,
		SERIESDESCRIPTION,
		PROTOCOLNAME,
		ACQUISITIONDATE,
		STUDYDATE, 
		PATIENTNAME,PATIENTBIRTHDATE)
	
	
	return run(command)

def find_study(
	AET : str,
	date : str,
	server_ip : str = "88.202.185.144",
	server_AET : str = "theServerAET",
	port : int = 104, 
	PATIENTID : str = PATIENTID) -> str:
	"""
	builds a query for findscu of QueryRetrieveLevel of study using the parameters passed as arguments.
	Args : 
		AET (string) : Called AET
		server_ip (string) : server ip
		server_AET (string) : server_AET
		port (int) : port 
		PATIENTID (string) : patient id 
		STUDYDESC (string) : Study description.
	Returns : 
		string : The log lines.
	"""
	
	check_ids(PATIENTID)
	modified_params = replace_default_params(PARAMETERS, AET, server_ip , server_AET , port)
	command = find_studies_command.format(modified_params, PATIENTID, date)
	
	return run(command)

def get(
	AET : str,
	date : str,
	additional_filters : list = [],
	server_ip : str = "88.202.185.144",
	server_AET : str = "theServerAET",
	port : int = 104, 
	PATIENTID : str = PATIENTID,
	STUDYINSTANCEUID : str = STUDYINSTANCEUID,
	SERIESINSTANCEUID : str = SERIESINSTANCEUID,
	move_port : int = 4006,
	OUTDIR : str  = OUTDIR) -> str:
	"""
	builds a query for movescu.
	Args : 
		AET (string) : Called AET
		server_ip (string) : server ip
		server_AET (string) : server_AET
		port (int) : port 
		PATIENTID (string) : patient id 
		STUDYINSTANCEUID (string) : Study instance unique idetifier.
		SERIESINSTANCEUID (string) : Series instance unique identifier
		OUTDIR (string) : directory of output files
	Returns : 
		string : The log lines.
	"""

	check_ids(PATIENTID)
	check_ids(SERIESINSTANCEUID, attribute = "Series instance UID")
	check_ids(STUDYINSTANCEUID, attribute = "Study instance UID")
	check_port(move_port)
	check_port(port)

	modified_params = replace_default_params(PARAMETERS, AET, server_ip , server_AET , port)
	command = move_command.format(
		modified_params,
		AET,
		PATIENTID,
		STUDYINSTANCEUID,
		SERIESINSTANCEUID,
		date,
		move_port,
		OUTDIR)
	
	for filter_ in additional_filters : 
		check_filter(filter_)
		command += " --key "+ filter_ + " "

	return run(command)
	
def write_file(results : str, file : str = "output.txt"): 
	"""
	Writes results in file passed in parameters using the parameters passed as arguments.
	Args : 
		results (str) : a str of lines of logs
		file (string) : path to text file where the log lines in results will be written.
	"""

	if not os.path.exists(file):
	    os.mknod(file)

	f = open(file, "a")
	for line in results:
		f.write(str(line) + "\n")
	f.close()

def replace_default_params(
	PARAMETERS : str,
	AET : str,
	server_ip : str,
	server_AET : str ,
	port : int) -> str: 
	"""
	Helper function to replace default parameters in queries by new parameters.

	Args : 
		AET (string) : Called AET
		server_ip (string) : server ip
		server_AET (string) : server_AET
		port (int) : port 

	Returns : 
		string : modified parameters with input values.
	"""
	check_parameters_inputs(AET, server_ip, server_AET, port)

	return PARAMETERS.replace(
		"theServerAET", server_AET).replace(
		" 104", " "+str(port)).replace(
		"88.202.185.144", server_ip).replace(
		"MY_AET",AET)

def run(query: str) -> str:
    """
    Runs a the command passed as parameter. 
    Args:
    	query (string) : query command line to be executed.
    Returns : 
    	string : The log lines.
    """

    try : 
    	cmd = shlex.split(query)
    except ValueError : 
    	
    	exit()
    completed = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    lines = completed.stderr.decode('latin1').splitlines()
    lines = [line.replace('\x00', '') for line in lines]
    
    return lines
