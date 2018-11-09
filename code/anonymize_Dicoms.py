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

def anonymize_dicom_file(
	filename : str,
	output_filename : str, 
	PatientID : str = "test1",
	PatientName : str = "test1") -> None:
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
	attributes = dataset.dir("")

	#Update attributes to make it anonymous.
	try : 
		if "PatientID" in attributes : 
			old_id = dataset.PatientID
			dataset.PatientID = PatientID

		if "PatientName" in attributes : 
			dataset.PatientName = PatientName

		if "InstitutionAddress" in attributes: 
			dataset.InstitutionAddress = "Address"
		
		if "ReferringPhysicianTelephoneNumbers" in attributes : 
			dataset.ReferringPhysicianTelephoneNumbers = ""
		
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

		if "PerformingPhysiciansName" in attributes : 
			dataset.PerformingPhysiciansName = ""

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

		
	#Keep track of failures in a text file.
	except AttributeError : 
		text_file = open("fails.txt", "a")

		text_file.write(filename + "\n")
		text_file.close()
		return
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
	datapath : str  = os.path.join("..","data"),
	subject_dicom_path : str = os.path.join("ses-*","*","*"),
	new_ids = None,
	rename = True) -> Dict[str,str]:
	"""
	Anonymizes all dicom images located at the datapath in the structure specified by subject_dicom_path parameter.
	Args : 
		output_folder (string) : path where anonymized images will be located.
		datapath (string) : The path to the dicom images.
		subject_dicom_path (string) : the (generic) path to the dicom images starting from the patient folder.
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
			new_id  = open(os.path.join(datapath,patient,"new_id.txt")).read().splitlines()[0].zfill(6)
			old2set_idx[new_id] = patient.split("-")[-1]
			os.remove(os.path.join(datapath,patient,"new_id.txt"))
			
		#List all files within patient folder...
		files = glob(current_path)

		#Loop over all dicom files within a patient directory and anonymize them.
		for file in files:
			anonymize_dicom_file(file,os.path.join(output_folder,file), PatientID = new_id, PatientName = "Obi Ben Kanobi")
		
		#If the patient folders are to be renamed.
		if rename :
			try:
				os.rename(os.path.join(datapath , patient), os.path.join(datapath,"sub-"+new_id))
			except OSError : os.rename(os.path.join(datapath , patient), os.path.join(datapath,"sub-"+old2new_idx[patient]+"_2"))
	

	#return a mapping from new ids to old ids as a dictionary.
	new2old_idx = {new : old.replace("sub-","") for old, new in old2new_idx.items()}

	#dumping new ids to a json file.
	with open(os.path.join(datapath,'mapper.json'), 'w') as fp:
		if len(old2set_idx.keys()) == 0 : 
			json.dump(new2old_idx, fp)
		else : json.dump(old2set_idx, fp)

	return new2old_idx

def main(argv):
	
	data_path = argv[0]
	output_folder = argv[1]
	
	print("Anonymizing dicom files within path {}".format(os.path.abspath(data_path)))

	#Anonymizing all files.
	mapper = anonymize_all_dicoms_within_folder(output_folder = output_folder, datapath = data_path)

if __name__ == "__main__" : 
	main(sys.argv[1:])