import unittest
import sys
sys.path.insert(0, '../')
from execute_commands import *
from scrape import *
from sanity_checks import *
import pytest


def test_echo_invalid_inputs():
	with pytest.raises(ValueError):
		echo("")
	with pytest.raises(ValueError):
		echo("AET", port = 0)
	with pytest.raises(ValueError):
		echo("AET", port = 65536)
	with pytest.raises(ValueError): 
		echo("AET", port = 0)

	with pytest.raises(ValueError):
		echo("AET",server_AET = "dummyserverAETdummyserverAETdummyserverAET")

	with pytest.raises(ValueError):
		echo("AET",server_AET = "")

	with pytest.raises(ValueError):
		echo("dummyAETdummyAETdummyAET")

	with pytest.raises(ValueError):
		echo("AET", server_AET = "")

	with pytest.raises(ValueError):
		echo("AET", server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError):
		echo("AET", server_ip = "128.s132.185.16")

	with pytest.raises(ValueError):
		echo("AET",server_ip = "128.132..16")

	with pytest.raises(ValueError):
		echo("AET", server_ip = "128.132.1855.16")

	with pytest.raises(ValueError):
		echo("AET", server_ip = "California Dreaming")

def test_find_series_invalid_inputs(): 
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	
	with pytest.raises(ValueError):
		find_series("", "19930911")

	with pytest.raises(ValueError):
		find_series("AET", "19930911", port = 0)

	with pytest.raises(ValueError):
		find_series("AET", "19930911", port = 65536)

	with pytest.raises(ValueError):
		find_series("AET", "19930911", port = 0)

	with pytest.raises(ValueError) : 
		find_series("AET", "19930911", PATIENTID = dummy_long_string )

	with pytest.raises(ValueError) : 
		find_series("AET", "19930911", STUDYUID = dummy_long_string ,PATIENTID = "PAT004" )

	with pytest.raises(ValueError) : 
		find_series("AET", "19930911", server_AET = "dummyserverAETdummyserverAETdummyserverAET")

	with pytest.raises(ValueError) : 
		find_series("AET", "19930911", server_AET = "")

	with pytest.raises(ValueError) : 
		find_series("dummyAETdummyAETdummyAET", "19930911")

	with pytest.raises(ValueError) : 
		find_series("AET", STUDYDATE = "19930911", server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError) : 
		find_series("AET",  STUDYDATE = "19930911", server_ip = "128.s132.185.16")

	with pytest.raises(ValueError) : 
		find_series("AET",  STUDYDATE = "19930911", server_ip = "128.132..16")

	with pytest.raises(ValueError) : 
		find_series("AET",  STUDYDATE = "19930911", server_ip = "128.132.1855.16")
def test_find_study_invalid_inputs(): 
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	
	with pytest.raises(ValueError):
		find_study("", "19930911")

	with pytest.raises(ValueError): 
		find_study("AET", "19930911", port = 0)

	with pytest.raises(ValueError): 
		find_study("AET", "19930911", port = 65536)

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", port = 0)

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", PATIENTID = dummy_long_string )
	
	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", server_AET = "dummyserverAETdummyserverAETdummyserverAET")

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", server_AET = "")

	with pytest.raises(ValueError) : 
		find_study("dummyAETdummyAETdummyAET", "19930911")

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", server_ip = "128.s132.185.16")

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", server_ip = "128.132..16")

	with pytest.raises(ValueError) : 
		find_study("AET", "19930911", server_ip = "128.132.1855.16")

def test_get_invalid_inputs(): 
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	
	with pytest.raises(ValueError):
		get("", "19930911")

	with pytest.raises(ValueError): 
		get("AET", "19930911", port = 0)

	with pytest.raises(ValueError): 
		get("AET", "19930911", port = 65536)

	with pytest.raises(ValueError) : 
		get("AET", "19930911", port = 0)

	with pytest.raises(ValueError) : 
		get("AET", "19930911", PATIENTID = dummy_long_string )
	
	with pytest.raises(ValueError) : 
		get("AET", "19930911", server_AET = "dummyserverAETdummyserverAETdummyserverAET")

	with pytest.raises(ValueError) : 
		get("AET", "19930911", server_AET = "")

	with pytest.raises(ValueError) : 
		get("AET", "19930911", STUDYINSTANCEUID = dummy_long_string)
	
	with pytest.raises(ValueError) : 
		get("AET", "19930911", SERIESINSTANCEUID = dummy_long_string)
	
	with pytest.raises(ValueError) : 
		get("dummyAETdummyAETdummyAET", "19930911")

	with pytest.raises(ValueError) : 
		get("AET", "19930911", server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError) : 
		get("AET", "19930911", server_ip = "128.s132.185.16")

	with pytest.raises(ValueError) : 
		get("AET", "19930911", server_ip = "128.132..16")

	with pytest.raises(ValueError) : 
		get("AET", "19930911", server_ip = "128.132.1855.16")

def test_replace_default_parameters() :

	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	PARAMETERS = "88.202.185.144 104 -aec theServerAET -aet MY_AET"
	modified = "127.0.0.1 80 -aec Hello -aet Hello_Back"
	
	assert replace_default_params(PARAMETERS, "Hello_Back","127.0.0.1","Hello",80) == modified

	with pytest.raises(ValueError) : 
		
		replace_default_params(PARAMETERS, dummy_long_string, "127.0.0.1","Hello",80)

	with pytest.raises(ValueError) : 
		
		replace_default_params(PARAMETERS, dummy_long_string, "127.0.0.1","Hello",-1)
	with pytest.raises(ValueError) : 
		
		replace_default_params(PARAMETERS, "AET", "127.0.0.1",dummy_long_string,80)

	with pytest.raises(ValueError) : 
		
		replace_default_params(PARAMETERS, "AET", "127.0.0554.1","Hello",80)

	with pytest.raises(ValueError) : 
		replace_default_params(PARAMETERS, "AET", "California Dreaming","Hello",80)

	with pytest.raises(ValueError) : 
		replace_default_params(PARAMETERS, "AET", "124.20.564.45.45","Hello",80)

	with pytest.raises(ValueError) : 
		replace_default_params(PARAMETERS, "AET", "214..54.454","Hello",80)

	with pytest.raises(ValueError) : 
		replace_default_params(PARAMETERS, "", "214.1.54.454","Hello",80)

	with pytest.raises(ValueError) : 
		replace_default_params(PARAMETERS, "AET", "214.54.1.1","",80)

def test_modify_query_params() :
	scrape_command = "findscu 127.0.0.1 80 -k 0010,0020={} --key 0008,0020={} --key 0008,0030 -aec hello --patient path_to_dump.dcm"
	dump_query = "dump2dcm path_to_dump_txt.txt path_to_dump.dcm"

	queries = modify_query_parameters(
		server_ip = "127.0.0.1", 
		port = 80,
		dump_path_ = "path_to_dump.dcm",
		dump_txt_path_ = "path_to_dump_txt.txt", 
		aec = "hello" )
	
	assert queries[0] == dump_query
	assert queries[1] == scrape_command

def test_get_and_store_patients(): 
	
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	
	with pytest.raises(ValueError) :
		get_and_store_patients([dummy_long_string], dates = ["20150625"])

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "127.0.0.1", port = -1)

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "127.0.0.1", port = 65536)

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "127.0.0554.1")

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "California Dreaming")

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "124.20.564.45.45")

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "214..54.454")

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "214.54.1")

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], server_ip = "214.54.a.1")

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], aec = dummy_long_string)

	with pytest.raises(ValueError) : 
		get_and_store_patients(["NormalID"], dates = ["20150625"], aec = "")

def test_parse_date() : 
	with pytest.raises(ValueError) : 
		parse_date("12/08/171")

	with pytest.raises(ValueError) : 
		parse_date("12/08/")

	with pytest.raises(ValueError) : 
		parse_date("12/13/17")

	with pytest.raises(ValueError) : 
		parse_date("40/11/17")

	with pytest.raises(ValueError) : 
		parse_date("12//17")

	with pytest.raises(ValueError) : 
		parse_date("hihi/1/17")

	with pytest.raises(ValueError) : 
		parse_date("12/1/-2")

	with pytest.raises(ValueError) : 
		parse_date("Hello")

	with pytest.raises(ValueError) : 
		parse_date("1/2")

	assert parse_date("12/2/99") == "19990212"
	assert parse_date("12/2/12") == "20120212"

def test_process_date() : 
	with pytest.raises(ValueError) : 
		process_date("Not a date")

	with pytest.raises(ValueError) : 
		process_date("Not-date")

	with pytest.raises(ValueError) : 
		process_date("2/5/15-2/6/16-2/6/17")

	
	assert process_date("") == ""

	assert process_date("15/2/17-15/2/18") == "20170215-20180215"
	assert process_date("15/2/17") == "20170215"
	assert process_date("15/2/99-15/2/18") == "19990215-20180215"
def test_parse_birth_date() : 
	###!!!!!!!!!!!!!!!!!! TODO : add imput validation for birth date!!!!!!!!!!!!!!!!!!!!!
	assert parse_birth_date("15.02.2017") == "20170215"
	assert parse_birth_date("") == ""
def test_process_text_file() : 
	
	res = [{ 
	"StudyDate" : "20171020",
	"StudyTime" : "104457",
	"SeriesDecription" : "4metas24Gy_PTV18Gy_68min-RTDOSE",
	"PatientID" : "dummyid",
	"ProtocolName": "",
	"StudyInstanceUID" : "1.2.826.0.1.3680043.2.146.2.20.3171184.1700225197.0",
	"PatientName" : "dummyname",
	"PatientBirthDate" : "19640417",
	"SeriesInstanceUID" : "1.2.840.114358.359.1.20171101170336.1838414727465",
	"ImageType" : ""}, 
	{"StudyDate" : "20171020",
	"StudyTime" : "104457",
	"SeriesDecription" : "4metas24Gy_PTV18Gy_68min",
	"PatientID" : "dummyid",
	"ProtocolName": "",
	"StudyInstanceUID" : "1.2.826.0.1.3680043.2.146.2.20.3171184.170022.173107110677054118",
	"PatientName" : "dummyname",
	"PatientBirthDate" : "19640417",
	"SeriesInstanceUID" : "1.2.840.114358.1230.20171101171003.1",
	"ImageType" : ""}
	]

	#Testing all the dictionaries in the list are identical.
	dict_list =  process_text_files(filename = "test.txt")

	for i, dict_ in enumerate(dict_list) :
		shared_items = {k: res[i][k] for k in res[i] if k in dict_ and res[i][k] == dict_[k]}
		assert len(shared_items) == len(res[i])
		