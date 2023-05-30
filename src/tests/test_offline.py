import sys
sys.path.insert(0, '../../')
sys.path.insert(0, '../')

from execute_commands import *
import pacsman
from pacsman import *
from sanity_checks import *
import pytest
from anonymize_Dicoms import *
#from convert import *
import os
import pydicom
import shutil
from functools import reduce
from hypothesis import given, example
from create_DICOMDIR import *
import move_dumps
from hypothesis.strategies import text, integers

#TODO: after anonymisation run dicom3tools' dcentvfy on whole series to check consistency

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! for coverage execute : py.test --cov=../../ testing.py !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ../../ points to the project folder !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def test_echo_invalid_inputs() : 

	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

	with pytest.raises(ValueError): 
		echo(port = 0)

	with pytest.raises(ValueError):
		echo(port = 65536)

	with pytest.raises(ValueError):
		echo(port = 0)

	
	with pytest.raises(ValueError):
		echo(server_AET = dummy_long_string)

	with pytest.raises(ValueError):
		echo(server_AET = "")

	with pytest.raises(ValueError):
		echo( server_ip = "128.132.185.16.1")

	with pytest.raises(ValueError):
		echo( server_ip = "128.s132.185.16")

	with pytest.raises(ValueError):
		echo(server_ip = "128.132..16")

	with pytest.raises(ValueError):
		echo(server_ip = "128.132.1855.16")


def test_find_invalid_inputs(): 
	dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	
	with pytest.raises(ValueError) :
		find("", "19930911")

	with pytest.raises(ValueError) :
		find("AET", "19930911", port = 0)

	with pytest.raises(ValueError) :
		find("AET", "19930911", port = 65536)

	with pytest.raises(ValueError) :
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


def test_process_findscu_dump_file() :

	res = [{
	'SeriesInstanceUID': '1.2.840.114358.359.1.20171101170336.3712639202739',
	'StudyDate': '20171001',
	'SeriesDescription': '4metas24Gy_PTV18Gy_68min-RTDOSE',
	'PatientBirthDate': '19640101',
	'ProtocolName': '',
	'SeriesNumber': '',
	'ImageType': '',
	'StudyTime': '114557',
	'PatientID': 'dummyid',
	'DeviceSerialNumber': '',
	'StudyDescription': '',
	'StudyInstanceUID': '1.2.826.0.1.3680043.2.146.2.20.3171184.1700225197.0',
	'PatientName': 'dummyname',
	'AccessionNumber': '',
	'Modality': ''},
	{'SeriesInstanceUID': '1.2.840.231122.1230.23181726456172.1',
	'StudyDate': '20171001',
	'SeriesDescription': '4metas24Gy_PTV18Gy_68min',
	'PatientBirthDate': '19640101',
	'ProtocolName': '', 
	'SeriesNumber': '', 
	'ImageType': '',
	'StudyTime': '114557',
	'PatientID': 'dummyid',
	'DeviceSerialNumber': '',
	'StudyDescription': '',
	'StudyInstanceUID': '1.2.826.0.1.3680043.2.146.2.20.3171184.170022.232193921818771717',
	'PatientName': 'dummyname',
	'AccessionNumber': '',
	'Modality': ''}]

	#Testing all the dictionaries in the list are identical.
	dict_list =  parse_findscu_dump_file(filename = "test_data/findscu_dump_file_example.txt")
	for i, dict_ in enumerate(dict_list):
		shared_items = {k: res[i][k] for k in res[i] if k in dict_ and res[i][k] == dict_[k]}
		assert len(shared_items) == len(res[i])


def test_check_table() : 

	table = read_csv("test_data/query_file_invalid.csv").fillna("")
	with pytest.raises(ValueError) :
		check_query_table_allowed_filters(table)

	valid_table = read_csv("test_data/query_file_valid.csv").fillna("")
	assert check_query_table_allowed_filters(valid_table) == None


def test_parse_table() : 

	table = read_csv("test_data/query_file_valid.csv")
	parsed_table = parse_query_table(table)

	expected = [
	{'new_ids': '',
	'StudyDescription': '',
	'DeviceSerialNumber': '',
	'AcquisitionDate': '',
	'StudyInstanceUID': '',
	'SeriesDescription': '',
	'PatientID': 125,
	'StudyTime': '',
	'ImageType': '',
	'AccessionNumber': '',
	'StudyDate': 20170814,
	'Modality': '',
	'SeriesNumber': '',
	'ProtocolName': '',
	'PatientBirthDate': '',
	'SeriesInstanceUID': '',
	'PatientName': ''}]
	
	for i, dict_ in enumerate(parsed_table) :
		shared_items = {k: expected[i][k] for k in expected[i] if k in dict_ and expected[i][k] == dict_[k]}
		assert len(shared_items) == len(expected[i])


def test_fuzz_date():
	
	fuzzed, offset_days = fuzz_date("20180911", fuzz_parameter=2)
	assert fuzzed in ["20180910", "20180909", "20180911", "20180912", "20180913"]
	assert abs(offset_days) <= 2
	with pytest.raises(ValueError):
		fuzz_date("20180911",fuzz_parameter = random.randint(-10000,0))


def test_check_config_file():
	with pytest.raises(ValueError):
		check_config_file({"California Dreaming":1})


def test_check_query_retrieval_level():
	with pytest.raises(ValueError):
		check_query_retrieval_level({"Hello"})


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
		check_tuple({"California" : "*" , "Dreaming" : 1})

	with pytest.raises(ValueError):
		check_tuple({"California" : "" , "Dreaming" : ""})


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


#def test_process_list():
#
#	paths = ["sub-1234/ses-20170425114510","sub-3456/ses-20170525114500","sub-6788/ses-20170625114500"]
#	assert process_list(paths) == [("1234","20170425114510"),("3456","20170525114500"),("6788","20170625114500")]


# TODO update
def test_anonymize():
	in_file="test_data/rubo_sample_file_0003.DCM"
	out_file="test_data/rubo_sample_file_0003_anon.DCM"
	anonymize_dicom_file(in_file,out_file,PatientID = "00042",
						 new_StudyInstanceUID="0000001.01", new_SeriesInstanceUID="000012.01",
						 new_SOPInstanceUID="000000010.101",fuzz_birthdate=True,
						 fuzz_acqdates=True,fuzz_days_shift=10,
						 delete_identifiable_files=True, remove_private_tags= False)
	dataset = pydicom.read_file(out_file)
	attributes = dataset.dir("")
	
	assert dataset.PatientID == "00042"
	assert dataset.PatientName == "00042^sub"
	assert dataset.InstitutionAddress == "Address"
	assert dataset.PatientBirthDate == "19580729" # original date PatientBirthDate 19580719 -> check + 10 days shift
	assert dataset.StudyDate == "19930404" # original StudyDate 19930325
	if "ReferringPhysicianTelephoneNumbers" in attributes:
		assert dataset.ReferringPhysicianTelephoneNumbers == ""
	if "PatientTelephoneNumbers" in attributes:
		assert dataset.PatientTelephoneNumbers == ""
	if "PersonTelephoneNumbers" in attributes:
		assert dataset.PersonTelephoneNumbers == ""
	if "orderCallbackPhoneNumber" in attributes:
		assert dataset.OrderCallbackPhoneNumber == ""
	if "InstitutionName" in attributes: 
		assert dataset.InstitutionName == ""

	if "ReferringPhysiciansAddress" in attributes : 
		assert dataset.ReferringPhysiciansAddress == ""

	if "ReferringPhysicianIDSequence" in attributes : 
		assert dataset.ReferringPhysicianIDSequence == ""

	if "InstitutionalDepartmentName" in attributes : 
		assert dataset.InstitutionalDepartmentName == ""

	if "PhysicianOfRecord" in attributes : 
		assert dataset.PhysicianOfRecord == ""

	if "PerformingPhysicianName" in attributes : 
		assert dataset.PerformingPhysicianName == ""

	if "ReferringPhysiciansAddress" in attributes : 
		assert dataset.ReferringPhysiciansAddress == ""
	
	if "ReferringPhysiciansTelephoneNumber" in attributes : 
		assert dataset.ReferringPhysiciansTelephoneNumber == ""
	
	if "PerformingPhysicianIDSequence" in attributes : 
		assert dataset.PerformingPhysicianIDSequence == ""

	if "NameOfPhysicianReadingStudy" in attributes : 
		assert dataset.NameOfPhysicianReadingStudy == ""

	if "PhysicianReadingStudyIDSequence" in attributes : 
		assert dataset.PhysicianReadingStudyIDSequence == ""

	if "OperatorsName" in attributes : 
		assert dataset.OperatorsName == ""

	if "IssuerOfPatientID" in attributes : 
		assert dataset.IssuerOfPatientID == ""

	if "PatientsBirthTime" in attributes : 
		assert dataset.PatientsBirthTime == ""

	if "OtherPatientIDs" in attributes : 
		assert dataset.OtherPatientIDs == ""

	if "OtherPatientNames" in attributes : 
		assert dataset.OtherPatientNames == ""

	if "PatientBirthName" in attributes : 
		assert dataset.PatientBirthName == ""

	if "PersonAddress" in attributes : 
		assert dataset.PersonAddress == ""

	if "PatientMotherBirthName" in attributes : 
		assert dataset.PatientMotherBirthName == ""

	if "CountryOfResidence" in attributes : 
		assert dataset.CountryOfResidence == ""

	if "RegionOfResidence" in attributes : 
		assert dataset.RegionOfResidence == ""

	if "CurrentPatientLocation" in attributes : 
		assert dataset.CurrentPatientLocation == ""

	if "PatientInstitutionResidence" in attributes : 
		assert dataset.PatientsInstitutionResidence == ""

	if "PersonName" in attributes : 
		assert dataset.PersonName == ""



	dataset.PatientAge = "091"
	dataset.save_as("test_data/temp_output_sample_image.DCM")
	
	anonymize_dicom_file("test_data/temp_output_sample_image.DCM","test_data/temp_output_sample_image.DCM",PatientID = "00042",
						 new_StudyInstanceUID="0000001.01", new_SeriesInstanceUID="000012.01",
						 new_SOPInstanceUID="000000010.101",fuzz_birthdate=True,
						 fuzz_acqdates=False,fuzz_days_shift=5,
						 delete_identifiable_files=True, remove_private_tags= False)

	dataset = pydicom.read_file("test_data/temp_output_sample_image.DCM")
	assert dataset.PatientAge == "90+Y"


def test_anonymize_all_dicoms_within_folder():
	dict_ = anonymize_all_dicoms_within_root_folder(output_folder =".", datapath=".",
													pattern_dicom_files="output_sample_image", rename_patient_directories= False)
	#print(dict_)
	#assert dict_ == {'000003': '__pycache__', '000002': 'test_set', '000000': '.pytest_cache', '000001': '.hypothesis'}


def test_read_line_by_line():
	lines = list(readLineByLine("test_data/findscu_dump_file_example.txt"))[:4]
	assert lines == [
	'I: Requesting Association',
	'I: Association Accepted (Max Send PDV: 32756)',
	'I: Sending Find Request (MsgID 1)',
	'I: Request Identifiers:']


def test_process_name():
	assert process_person_names("Obi-Wan Kenobi") == "*KENOBI"
	assert process_person_names("") == ""


def test_run():
	assert [] == run("echo California Dreaming.")


def test_generate_new_folder_name():
	assert len(generate_new_folder_name()) <= 8
	name = list(generate_new_folder_name())
	assert reduce(lambda x,y : x and y ,[(letter in (string.ascii_uppercase + string.digits)) for letter in name])
	assert generate_new_folder_name(names = ["".join(name)]) != "".join(name)


def test_add_or_retrieve_name():
	folder_name, old_2_new = add_or_retrieve_name("Hello", {})
	assert add_or_retrieve_name("Hello", {"Hello" : folder_name}) == (folder_name, old_2_new)


def test_move_and_rename():
	if os.path.isdir("./dicomdir") : 
		shutil.rmtree("./dicomdir")

	os.mkdir("./dicomdir")
	move_and_rename_files("./test_set","./dicomdir")
	assert len(glob("./test_set/*/*")) == len(glob("./dicomdir/*/*"))
	assert len(glob("./test_set/*")) == len(glob("./dicomdir/*"))
	#print()
	assert len(glob("./test_set/*/*/*/*")) == len(glob("./dicomdir/*/*/*/*"))
	create_dicomdir("./dicomdir")
	os.chdir(os.path.abspath("./src/tests/"))
	assert os.path.join(".","dicomdir","DICOMDIR") in glob(os.path.join(".","dicomdir","*"))

	if os.path.isdir("./dicomdir") : 
		shutil.rmtree("./dicomdir")


def test_move_dumps():

	if os.path.isdir("./dicomdir") : 
		shutil.rmtree("./dicomdir")

	os.mkdir("./dicomdir")
	n_csv_files = sorted(glob("./test_set/sub-*/ses-*/*.csv"))
	n_csv_files = [csv.split(os.sep)[-1] for csv in n_csv_files]

	move_dumps.move("./test_set","./dicomdir")

	assert glob("./test_set/sub-*/ses-*/*.csv") == []
	assert [csv.split(os.sep)[-1] for csv in sorted(glob("./dicomdir/sub-*/ses-*/*.csv"))] == n_csv_files
	

	move_dumps.move("./dicomdir","./test_set")

	assert [csv.split(os.sep)[-1] for csv in sorted(glob("./test_set/sub-*/ses-*/*.csv"))] == n_csv_files
	assert glob("./dicomdir/sub-*/ses-*/*.csv") == []

	shutil.rmtree("./dicomdir")


@given(s = text())
@example(s = 'Obi-Wan Kenobi')
def test_check_date_input(s):
	processed = process_person_names(s)
	if s == "" : assert processed == ""
	else : assert process_person_names(s) == "*"+s.split(" ")[-1].upper()

# def test_convert_to_nifti():
# 	convert_to_nifti("XXXX", "YYYY", "./test_set")
# 	convert_to_nifti("XXXX", "YYYY", "./test_set")
# 	convert_all("./test_set")
# 	if os.path.isdir("./test_set/Nifti"):
# 		shutil.rmtree("./test_set/Nifti")
# 	shutil.rmtree("./test_set/sub-XXXX")


def test_encoding_problem():
	'''
	TODO Implement test for `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc9 in position 2622: invalid continuation byte`
	'''
	pass


"""possible_dates = []
for year in range(1900,2019):
	for month in range(1,13):
		for day in range(1,32):
			if day > 28 and month == 2 : continue
			if day == 31 and month in [4,6,9,11] : continue
			day_add = ""
			month_add = ""
			if day < 10 : day_add = "0"
			if month < 10 : month_add = "0"
			possible_dates.append(str(year)+month_add+str(month)+day_add+str(day))


@given(s = text(alphabet = [str(i) for i in range(10)], min_size=7, average_size=8, max_size=8).filter(lambda x : x in possible_dates), t = integers(min_value = 1))
def hyp_fuzz_date(s,t):
	fuzz_date(s,fuzz_parameter = t)
"""