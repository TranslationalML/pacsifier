"""
Test functions requiring connectivity to a DICOM server
"""
import sys
sys.path.insert(0, '../../')
sys.path.insert(0, '../')

from execute_commands import *
import pacsman
from pacsman import *
from sanity_checks import *
import pytest
from anonymize_Dicoms import *
from convert import *
import os
import pydicom
import shutil
from functools import reduce
from hypothesis import given, example
from create_DICOMDIR import *
import move_dumps
from hypothesis.strategies import text, integers

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! for coverage execute : py.test --cov=../../ testing.py !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ../../ points to the project folder !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# TODO update for DICOMserverUK
def test_retrieve():
	pass

	table = read_csv(os.path.join("..","..","files","test.csv"), dtype=str).fillna("")
	config_path = os.path.join("..","..","files","config.json")

	with open(config_path) as f:
		parameters = json.load(f)
	
	out_directory = os.path.join(".","test_set")
	#retrieve_dicoms_using_table(table, parameters, out_directory, False, False)

	#assert glob("./test_set/sub-*/ses-*/*/*") == []
	#retrieve_dicoms_using_table(table, parameters, out_directory, False, True)

	#assert glob("./test_set/sub-*/ses-*/*/*") == []
	retrieve_dicoms_using_table(table, parameters, out_directory, True, True)
	assert glob("./test_set/sub-*/ses-*/*/*")[:6] == ['./test_set/sub-XXX/ses-YYY/foo/bar', 'XXX' ]


# TODO update this to use DICOMserverUK
def test_check_output_info():
	pass

	#pacsman.main(["--info", "--queryfile test.csv", "--out_directory ./tests/test_set",  "--config ./files/config.json"])
	#subjects = glob("./test_set/*")
	#sessions = glob("./test_set/sub-*/ses-*")
	#csv_files = glob("./test_set/sub-*/ses-*/*.csv")

	# assert subjects == ['./test_set/sub-XXX']
	# assert sessions == ['./test_set/sub-XXX/ses-YYY', './test_set/sub-XXX/ses-ZZZ']
	#assert csv_files == ['./test_set/sub-XXX/ses-YYY/foo.csv', ... ]
