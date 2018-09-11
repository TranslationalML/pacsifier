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
	date = datetime(day = day, month = month, year = year)
	date = (date + timedelta(days = fuzz)).strftime("%Y%m%d")
	return date

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

	dataset.PatientID = PatientID
	dataset.PatientName = PatientName
	dataset.InstitutionAddress = "Address"
	dataset.ReferringPhysicianTelephoneNumbers = ""
	dataset.PatientTelephoneNumbers = ""
	dataset.PersonTelephoneNumbers = ""
	dataset.OrderCallbackPhoneNumber = ""
	age = dataset.PatientAge
	studyUID = dataset.StudyInstanceUID
	dataset.StudyInstanceUID = studyUID.replace(old_id , dataset.PatientID)

	if int(age[:3]) > 89 : 
		dataset.PatientAge = "90+Y"

	# Same as above but for blanking data elements that are type 2.
	for name in ['PatientBirthDate']:
	    if name in dataset:
	        dataset.data_element(name).value = fuzz_date(dataset.data_element(name).value)
	        
	# write thoutput_foldere 'anonymized' DICOM out under the new filename
	dataset.save_as(output_filename)

def anonymize_all(
	output_folder : str = ".",
	datapath : str  = os.path.join("..","data"),
	subject_dicom_path : str = os.path.join("ses-*","*","*")) -> Dict[str,str]:
	"""
	Anonymizes all dicom images located at the datapath in the structure specified by subject_dicom_path parameter.
	Args : 
		output_folder (string) : path where anonymized images will be located.
		datapath (string) : The path to the dicom images.
		subject_dicom_path (string) : the (generic) path to the dicom images starting from the patient folder.
	Returns : 
		dict : Dictionary keeping track of the new patientIDs and old patientIDs mappings.
	"""

	#Listing patient files.
	patients_folders = next(os.walk(datapath))[1]

	old2new_idx = {patients_folders[i] : str(i).zfill(6) for i in range(len(patients_folders))}

	for patient in tqdm(patients_folders) : 
		current_path = os.path.join(datapath, patient, subject_dicom_path)
		files = glob(current_path)

		for file in files:
			
			anonymize(file,os.path.join(output_folder,file), PatientID = old2new_idx[patient], PatientName = "Obi Ben Kanobi")
		os.rename(os.path.join(datapath , patient), os.path.join(datapath,"sub-anony-"+old2new_idx[patient]))
	new2old_idx = {new : old.replace("sub-","") for old, new in old2new_idx.items()}

	return new2old_idx

def main(argv):
	
	json_path = argv[0]
	data_path = argv[1]

	print("Anonymizing ...")

	#Anonymizing all files.
	mapper = anonymize_all(output_folder = data_path, datapath = data_path)

	#dumping new ids to a json file.
	with open(os.path.join(json_path,'mapper.json'), 'w') as fp:
		json.dump(mapper, fp)

if __name__ == "__main__" : 
	main(sys.argv[1:])