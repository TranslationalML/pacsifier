import pydicom
from datetime import datetime, timedelta
from glob import glob
import sys
import os
from tqdm import tqdm
import random
import json
from typing import Dict
import argparse

def fuzz_date(date : str, fuzz_parameter : int = 60) -> str: 
	"""
	Fuzzes date in a range of fuzz_parameter days prior to fuzz_parameter days after.
	Args : 
		date: date in YYYYMMDD format.
		fuzz_parameter: the number of days by which the date will be fuzzed.
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

def anonymize_dicom_file(
	filename : str,
	output_filename : str, 
	PatientID : str = "test1",
	PatientName : str = "test1") -> None:
	"""
	Anonymizes the dicom image located at filename by affecting  patient id, patient name and date.
	Args : 
		filename: path to dicom image.
		output_filename: output path of anonymized image. 
		PatientID: the new patientID after anonymization.
		PatientName: The new PatientName after anonymization.
	"""

	# Load the current dicom file to 'anonymize'
	try:
		dataset = pydicom.read_file(filename)
	except pydicom.errors.InvalidDicomError: 
		print("Error at file at path :  " + filename)
		pass
	
	ninety_plus = False
	attributes = dataset.dir("")

	#Update attributes to make it anonymous.
	if "PatientID" in attributes : 
		old_id = dataset.PatientID
		dataset.PatientID = PatientID

	if "PatientName" in attributes : 
		dataset.PatientName = PatientName

	if "InstitutionAddress" in attributes: 
		dataset.InstitutionAddress = "Address"

	if "InstitutionName" in attributes: 
		dataset.InstitutionName = ""
		#/home/localadmin/Bureau/trippin/sub-124568/ses-20180108152705/0001-Scano2.0/CT.1.2.392.200036.9116.2.6.1.3268.2054951902.1515392849.707206
	
	if "ReferringPhysicianTelephoneNumbers" in attributes : 
		dataset.ReferringPhysicianTelephoneNumbers = ""

	if "ReferringPhysicianName" in attributes : 
		dataset.ReferringPhysicianName = ""
	
	if "PatientTelephoneNumbers" in attributes : 
		dataset.PatientTelephoneNumbers = ""
	
	if "PersonTelephoneNumbers" in attributes : 
		dataset.PersonTelephoneNumbers = ""
	
	if "OrderCallbackPhoneNumber" in attributes : 
		dataset.OrderCallbackPhoneNumber = ""

	if "ReferringPhysiciansName" in attributes : 
		dataset.ReferringPhysiciansName = ""

	if "ReferringPhysiciansAddress" in attributes : 
		dataset.ReferringPhysiciansAddress = ""

	if "ReferringPhysiciansTelephoneNumber" in attributes : 
		dataset.ReferringPhysiciansTelephoneNumber = ""

	if "ReferringPhysicianIDSequence" in attributes : 
		dataset.ReferringPhysicianIDSequence = ""

	if "InstitutionalDepartmentName" in attributes : 
		dataset.InstitutionalDepartmentName = ""

	if "PhysicianOfRecord" in attributes : 
		dataset.PhysicianOfRecord = ""

	if "PerformingPhysicianName" in attributes : 
		dataset.PerformingPhysicianName = ""

	if "PerformingPhysicianIDSequence" in attributes : 
		dataset.PerformingPhysicianIDSequence = ""

	if "NameOfPhysicianReadingStudy" in attributes : 
		dataset.NameOfPhysicianReadingStudy = ""

	if "PhysicianReadingStudyIDSequence" in attributes : 
		dataset.PhysicianReadingStudyIDSequence = ""

	if "OperatorsName" in attributes : 
		dataset.OperatorsName = ""

	if "IssuerOfPatientID" in attributes : 
		dataset.IssuerOfPatientID = ""

	if "PatientsBirthTime" in attributes : 
		dataset.PatientsBirthTime = ""

	if "OtherPatientIDs" in attributes : 
		dataset.OtherPatientIDs = ""

	if "OtherPatientNames" in attributes : 
		dataset.OtherPatientNames = ""

	if "PatientBirthName" in attributes : 
		dataset.PatientBirthName = ""

	if "PersonAddress" in attributes : 
		dataset.PersonAddress = ""

	if "PatientMotherBirthName" in attributes : 
		dataset.PatientMotherBirthName = ""

	if "CountryOfResidence" in attributes : 
		dataset.CountryOfResidence = ""

	if "RegionOfResidence" in attributes : 
		dataset.RegionOfResidence = ""

	if "CurrentPatientLocation" in attributes : 
		dataset.CurrentPatientLocation = ""

	if "PatientInstitutionResidence" in attributes : 
		dataset.PatientsInstitutionResidence = ""

	if "PersonName" in attributes : 
		dataset.PersonName = ""

	
	try : 
		age = dataset.PatientAge

		#If age attribute is an empty string, skip this step all together
		if age != '' :
			if int(age[:3]) > 89 : 

				ninety_plus = True
				dataset.PatientAge = "90+Y"
				dataset.PatientBirthDate = "19010101"
				
	except AttributeError : 
		pass

	#The StudyInstanceUID contains the old id. therefore, the old id should be replaced by the new anonymous one.
	if "StudyInstanceUID" in attributes : 
		studyUID = dataset.StudyInstanceUID
		dataset.StudyInstanceUID = studyUID.replace(old_id , PatientID)

	for name in ['PatientBirthDate']:
		if name in dataset:

			#Assign a new fuzzed birth date.
			new_date = fuzz_date(dataset.data_element(name).value)
			dataset.data_element(name).value = new_date
			if not ninety_plus : 

				#Change the age of the patient according to the new fuzzed birth date.
				new_age = str(int((datetime.strptime(dataset.StudyDate, "%Y%m%d") - datetime.strptime(new_date, "%Y%m%d")).days / 365))
				try : 
					dataset.PatientAge = str(new_age).zfill(3) + "Y"
				except AttributeError : pass
	
	# write the 'anonymized' DICOM out under the new filename

	dataset.save_as(output_filename)

def anonymize_all_dicoms_within_folder(
	output_folder : str = ".",
	datapath : str  = os.path.join(".","data"),
	subject_dicom_path : str = os.path.join("ses-*","*","*"),
	new_ids : str = None,
	rename : bool = True) -> Dict[str,str]:
	"""
	Anonymizes all dicom images located at the datapath in the structure specified by subject_dicom_path parameter.
	Args : 
		output_folder: path where anonymized images will be located.
		datapath: The path to the dicom images.
		subject_dicom_path: the (generic) path to the dicom images starting from the patient folder.
		new_ids (string) : The anonymous ids to be set after anonymizing the original ids. 
		rename (boolean) : A boolean to determine if the folder name which is named after the old ids would be renamed into the anonymized ids.
	Returns : 
		dict : Dictionary keeping track of the new patientIDs and old patientIDs mappings.
	"""

	#Listing patient files.
	
	patients_folders = next(os.walk(datapath))[1]
	if new_ids == None : 
		new_ids = {patients_folders[i] : str(i).zfill(6) for i in range(len(patients_folders))}

	#Keep a mapping from old to new ids in a dictionary.
	
	old2new_idx = {patients_folders[i] : new_ids[patients_folders[i]] for i in range(len(patients_folders))}
	old2set_idx = {}
	#Loop over patients...
	for patient in tqdm(patients_folders) : 
		new_id = old2new_idx[patient]
		current_path = os.path.join(datapath, patient, subject_dicom_path)
		
		if os.path.isfile(os.path.join(datapath,patient,"new_id.txt")) : 
			new_id  = open(os.path.join(datapath,patient,"new_id.txt")).read().splitlines()[0]
			old2set_idx[new_id] = patient.split("-")[-1]
			os.remove(os.path.join(datapath,patient,"new_id.txt"))
			
		#List all files within patient folder...
		files = glob(current_path)

		#Loop over all dicom files within a patient directory and anonymize them.
		for file in files:
			
			path = os.path.normpath(file)
			path = path.split(os.sep)
			
			if not os.path.isdir(os.path.join(output_folder,os.path.join(*path[-4:-3]))):
				os.mkdir(os.path.join(output_folder,os.path.join(*path[-4:-3])))

			if not os.path.isdir(os.path.join(output_folder,os.path.join(*path[-4:-2]))):
				os.mkdir(os.path.join(output_folder,os.path.join(*path[-4:-2])))

			if not os.path.isdir(os.path.join(output_folder,os.path.join(*path[-4:-2]))):
				os.mkdir(os.path.join(output_folder,os.path.join(*path[-4:-1])))

			anonymize_dicom_file(file,os.path.join(output_folder,os.path.join(*path[-4:])), PatientID = new_id, PatientName = "Obi Ben Kanobi")
		
		#If the patient folders are to be renamed.
		if rename :
			try:
				print(os.path.join(output_folder , patient))
				os.rename(os.path.join(output_folder , patient), os.path.join(output_folder,"sub-"+new_id))
			except OSError : os.rename(os.path.join(output_folder , patient), os.path.join(output_folder,"sub-"+old2new_idx[patient]+"_2"))
	

	#return a mapping from new ids to old ids as a dictionary.
	new2old_idx = {new : old.replace("sub-","") for old, new in old2new_idx.items()}

	#dumping new ids to a json file.
	with open(os.path.join(output_folder,'mapper.json'), 'w') as fp:
		if len(old2set_idx.keys()) == 0 : 
			json.dump(new2old_idx, fp)
		else : json.dump(old2set_idx, fp)

	return new2old_idx

def main(argv):
	parser = argparse.ArgumentParser()
	
	parser.add_argument("--in_folder",	"-d",	help = "Directory to the dicom files to be anonymized.",				default = os.path.join(".","data"))
	parser.add_argument("--out_folder", "-o",	help = "Output directory where the anonymized dicoms will be saved.",	default = os.path.join(".","data"))
	parser.add_argument("--new_ids", 	"-n", 	help = "List of new ids.")
	args = parser.parse_args()


	data_path = args.in_folder
	output_folder = args.out_folder
	
	print("Anonymizing dicom files within path {}".format(os.path.abspath(data_path)))

	#Anonymizing all files.
	new_ids = args.new_ids
	if args.new_ids :
		new_ids = json.load(open(args.new_ids, "r"))

	mapper = anonymize_all_dicoms_within_folder(output_folder = output_folder, datapath = data_path, new_ids = new_ids)

if __name__ == "__main__" : 
	main(sys.argv[1:])