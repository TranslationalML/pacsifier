import unittest
import sys
sys.path.insert(0, '../')
from execute_commands import *
from scrape import *
from sanity_checks import *
import pytest
from anonymize import *
from convert import *
import os
import pydicom
import shutil
from hypothesis import given, example
from hypothesis.strategies import text

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! for coverage execute : py.test --cov=../../ testing.py !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ../../ points to the project folder !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def test_find_invalid_inputs(): 
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	
	with pytest.raises(ValueError):
		find("", "19930911")

	with pytest.raises(ValueError):
		find("AET", "19930911", port = 0)

	with pytest.raises(ValueError):
		find("AET", "19930911", port = 65536)

	with pytest.raises(ValueError):
		find("AET", "19930911", port = 0)

	with pytest.raises(ValueError) : 
		find("AET", "19930911", PATIENTID = dummy_long_string )

	with pytest.raises(ValueError) : 
		find("AET", "19930911", STUDYUID = dummy_long_string ,PATIENTID = "PAT004" )

	with pytest.raises(ValueError) : 
		find("AET", "19930911", server_AET = "dummyserverAETdummyserverAETdummyserverAET")

	with pytest.raises(ValueError) : 
		find("AET", "19930911", server_AET = "")

	with pytest.raises(ValueError) : 
		find("dummyAETdummyAETdummyAET", "19930911")

	with pytest.raises(ValueError) : 
		find("AET", STUDYDATE = "19930911", server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError) : 
		find("AET",  STUDYDATE = "19930911", server_ip = "128.s132.185.16")

	with pytest.raises(ValueError) : 
		find("AET",  STUDYDATE = "19930911", server_ip = "128.132..16")

	with pytest.raises(ValueError) : 
		find("AET",  STUDYDATE = "19930911", server_ip = "128.132.1855.16")


def test_get_invalid_inputs():
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

	with pytest.raises(ValueError):
		get("", "19930911")

	with pytest.raises(ValueError): 
		get("AET", "19930911", port = 0)

	with pytest.raises(ValueError):
		get("AET", "19930911", port = 65536)

	with pytest.raises(ValueError):
		get("AET", "19930911", port = 0)

	with pytest.raises(ValueError):
		get("AET", "19930911", PATIENTID = dummy_long_string )
	
	with pytest.raises(ValueError):
		get("AET", "19930911", server_AET = "dummyserverAETdummyserverAETdummyserverAET")

	with pytest.raises(ValueError):
		get("AET", "19930911", server_AET = "")

	with pytest.raises(ValueError):
		get("AET", "19930911", STUDYINSTANCEUID = dummy_long_string)
	
	with pytest.raises(ValueError):
		get("AET", "19930911", SERIESINSTANCEUID = dummy_long_string)
	
	with pytest.raises(ValueError):
		get("dummyAETdummyAETdummyAET", "19930911")

	with pytest.raises(ValueError):
		get("AET", "19930911", server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError):
		get("AET", "19930911", server_ip = "128.s132.185.16")

	with pytest.raises(ValueError):
		get("AET", "19930911", server_ip = "128.132..16")

	with pytest.raises(ValueError):
		get("AET", "19930911", server_ip = "128.132.1855.16")

def test_replace_default_parameters():

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

def test_check_table() : 

	table = read_csv("test.csv").fillna("")
	with pytest.raises(ValueError) :
		check_table(table)
	valid_table = read_csv("valid.csv").fillna("")
	assert check_table(valid_table) == None

def test_parse_table() : 

	table = read_csv("valid.csv")
	parsed_table = parse_table(table)

	expected = [{'DeviceSerialNumber': '',
	'ProtocolName': '', 
	'StudyInstanceUID': '',
	'SeriesInstanceUID': '',
	'PatientBirthDate': '',
	'PatientID': 125,
	'StudyTime': '',
	'AcquisitionDate': '',
	'SeriesDecription': '',
	'PatientName': '',
	'StudyDate': 20170814,
	'ImageType': ''}]

	for i, dict_ in enumerate(parsed_table) :
		shared_items = {k: expected[i][k] for k in expected[i] if k in dict_ and expected[i][k] == dict_[k]}
		assert len(shared_items) == len(expected[i])

def test_fuzz_date():
	
	fuzzed = fuzz_date("20180911", fuzz_parameter = 2)
	assert fuzzed in ["20180910", "20180909", "20180911", "20180912", "20180913"]
	with pytest.raises(ValueError):
		fuzz_date("20180911",fuzz_parameter = random.randint(-10000,0))

def test_sanity_checks(): 
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	with pytest.raises(ValueError):
		check_ip("California Dreaming")

	with pytest.raises(ValueError): 
		check_ip("128.132.185.16.1")

	with pytest.raises(ValueError): 
		check_ip("128.s132.185.16")

	with pytest.raises(ValueError): 
		check_ip("128.132..16")

	with pytest.raises(ValueError): 
		check_ip("128.132.1855.16")

	with pytest.raises(ValueError): 
		check_ip("124.20.564.45.45")

	with pytest.raises(ValueError):
		check_port(14785425)
	
	with pytest.raises(ValueError):
		check_port(-2)

	with pytest.raises(ValueError):
		check_AET(dummy_long_string)

	with pytest.raises(ValueError):
		check_parameters_inputs(dummy_long_string, "1.1.1.1","Hello", 80)

	with pytest.raises(ValueError):
		check_parameters_inputs("hello", "1.1.1.1",dummy_long_string, 80)

	with pytest.raises(ValueError):
		check_parameters_inputs("AET", "1.1.1.1","Hello", -80)

	with pytest.raises(ValueError):
		check_parameters_inputs("AET", "1.1.1.1","Hello", 100000000)

	with pytest.raises(ValueError):
		check_parameters_inputs("hello", "1.1.1.1.","teff", 80)

	with pytest.raises(ValueError):
		check_parameters_inputs("hello", "1.1s.1.1","teff", 80)

	with pytest.raises(ValueError):
		check_parameters_inputs("hello", "1..1.1","teff", 80)

	with pytest.raises(ValueError):
		check_parameters_inputs("hello", "California Dreaming","teff", 80)

	with pytest.raises(ValueError):
		check_ids(dummy_long_string)

	with pytest.raises(ValueError):
		check_filter("hello")

	with pytest.raises(ValueError):
		check_tuple({"shrek" : "*" , "is" : 1, "love" : 2, "shrek is" : 3 , "life" : 4})

	with pytest.raises(ValueError):
		check_tuple({"shrek" : "" , "is" : "", "love" : "", "shrek is" : "" , "life" : ""})


	with pytest.raises(ValueError):
		check_date("18930402")

	with pytest.raises(ValueError):
		check_date("19934402")
	
	with pytest.raises(ValueError):
		check_date("19930472")

	with pytest.raises(ValueError):
		check_date("189304029")

	with pytest.raises(ValueError):
		check_date("1804029")

	with pytest.raises(ValueError):
		check_date("dakdjak")

	assert check_date("") == None
	assert check_date("20180825") == None
	assert check_date_range("") == None
	assert check_date_range("20180825") == None

	with pytest.raises(ValueError):
		check_date_range("18930402-20180722")

	with pytest.raises(ValueError):
		check_date_range("19930825-19934402")
	
	with pytest.raises(ValueError):
		check_date_range("19930825-19930472")

	with pytest.raises(ValueError):
		check_date_range("19930825-189304029")

	with pytest.raises(ValueError):
		check_date_range("19930825-1804029")

	with pytest.raises(ValueError):
		check_date_range("19930825-dakdjak")

def test_process_list():
	
	paths = ["sub-25647/ses-20170425114530","sub-14569/ses-20170525114530","sub-5879/ses-20170625114530","sub-69875/ses-20170725114530"]
	assert process_list(paths) == [("25647","20170425114530"),("14569","20170525114530"),("5879","20170625114530"),("69875","20170725114530")]

def test_list_files():
	path = os.path.join("..","..","code","*.py")
	expected_result = {'../../code/sanity_checks.py', '../../code/scrape.py', '../../code/sghipt.py', '../../code/execute_commands.py', '../../code/heuristic.py', '../../code/depannage.py', '../../code/anonymize.py', '../../code/convertall.py', '../../code/convert.py'}
	assert set(list_files(path)) == expected_result

def test_anonymize():
	anonymize("sample_image","output_sample_image",PatientID = "000420", PatientName = "Hello")
	dataset = pydicom.read_file("output_sample_image")

	assert dataset.PatientID == "000420"
	assert dataset.PatientName == "Hello"
	assert dataset.InstitutionAddress == "Address"
	assert dataset.ReferringPhysicianTelephoneNumbers == ""
	assert dataset.PatientTelephoneNumbers == ""
	assert dataset.PersonTelephoneNumbers == ""
	assert dataset.OrderCallbackPhoneNumber == ""

	dataset.PatientAge = "091"
	dataset.save_as("output_sample_image")


	anonymize("output_sample_image","output_sample_image",PatientID = "000420", PatientName = "Hello")
	dataset = pydicom.read_file("output_sample_image")
	assert dataset.PatientAge == "90+Y"

def test_anonymize_all(): 
	dict_ = anonymize_all(output_folder = ".", datapath=".", subject_dicom_path = "output_sample_image", rename = False)
	#assert dict_ == {'000000': '.pytest_cache', '000001': '__pycache__'}

def test_read_line_by_line():
	lines = list(readLineByLine("test.txt"))[:4]
	assert lines == [
	'I: Requesting Association',
	'I: Association Accepted (Max Send PDV: 32756)',
	'I: Sending Find Request (MsgID 1)',
	'I: Request Identifiers:']

def test_process_name():
	assert process_names("Obi-Wan Kenobi") == "*^*KENOBI*"

def test_run():
	assert [] == run("echo Shrek is love, shrek is life.")

@given(s = text())
@example(s='Obi-Wan Kenobi')
def test_check_date_input(s):
	assert process_names(s) == "*^*"+s.split(" ")[-1].upper()+"*"

"""
TODO :
- Hypothesis testing.
- Heuristic mapping.
- Mypy.
- Docker version.

""" 

if __name__ == '__main__':
    test_check_date_input()

