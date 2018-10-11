import pydicom
from datetime import datetime, timedelta
from glob import glob
import sys
import os
from tqdm import tqdm
import random
import json
from typing import Dict

def fuzz_date(date : str, fuzz_parameter : int = 60) -> str: 
	"""
	Fuzzes date in a range of fuzz_parameter days prior to fuzz_parameter days after.
	Args : 
		date (string) : date.
		fuzz_parameter (int) : the parameter by which the date will be fuzzed.
	Returns : 
		string : new fuzzed date.
	"""
	if fuzz_parameter <= 0 : 
		raise ValueError("Fuzz parameter must be strictly positive!")

	year = int(date[:4])
	month = int(date[4:6])
	day = int(date[6:8])

	#Generating random fuzz parameter.
	fuzz = random.randint(-fuzz_parameter, fuzz_parameter)

	#Processing new date.
	date_time = datetime(day = day, month = month, year = year) # type : datetime
	str_date = (date_time + timedelta(days = fuzz)).strftime("%Y%m%d") # type : str
	
	del date_time
	return str_date
	
def anonymize(
	filename : str,
	output_filename : str, 
	PatientID : str = "test1",
	PatientName : str = "test1"):
	"""
	Anonymizes the dicom image located at filename by affecting  patient id, patient name and date.
	Args : 
		filename (string) : path to dicom image.
		output_filename (string) : output path of anonymized image. 
		PatientID (string) : the new patientID after anonymization.
		PatientName (string) : The new PatientName after anonymization.
	"""

	# Load the current dicom file to 'anonymize'
	dataset = pydicom.read_file(filename)
	ninety_plus = False
	#Update attributes to make it anonymous.
	try : 
		old_id = dataset.PatientID

		dataset.PatientID = PatientID
		dataset.PatientName = PatientName
		dataset.InstitutionAddress = "Address"
		dataset.ReferringPhysicianTelephoneNumbers = ""
		dataset.PatientTelephoneNumbers = ""
		dataset.PersonTelephoneNumbers = ""
		dataset.OrderCallbackPhoneNumber = ""
	except AttributeError : 
		text_file = open("fails.txt", "a")

		text_file.write(filename + "\n")
		text_file.close()
		return
	try : 
		age = dataset.PatientAge
		if age != "" : 
			if int(age[:3]) > 89 : 

				ninety_plus = True
				dataset.PatientAge = "90+Y"
				dataset.PatientBirthDate = "19010101"
	except AttributeError : 
		pass

	studyUID = dataset.StudyInstanceUID
	dataset.StudyInstanceUID = studyUID.replace(old_id , PatientID)


	for name in ['PatientBirthDate']:
		if name in dataset:
			new_date = fuzz_date(dataset.data_element(name).value)
			dataset.data_element(name).value = new_date
			if not ninety_plus : 
				new_age = str(int((datetime.strptime(dataset.StudyDate, "%Y%m%d") - datetime.strptime(new_date, "%Y%m%d")).days / 365))
				try : 
					dataset.PatientAge = str(new_age).zfill(3) + "Y"
				except AttributeError : pass
	# write the 'anonymized' DICOM out under the new filename
	dataset.save_as(output_filename)


def main(argv):

	path = argv[0]
	patientID= argv[1]

	dicoms = glob(path+"/*/*/*") 
	for dicom in tqdm(dicoms) :
		anonymize(dicom,dicom,patientID,"Obi Ben Kanobi")

if __name__ == "__main__" : 
	main(sys.argv[1:])