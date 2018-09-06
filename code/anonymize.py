import pydicom
from datetime import datetime, timedelta
from glob import glob
import sys
import os
from tqdm import tqdm
import random
import json

def fuzz_date(date, fuzz_parameter = 60): 
	"""
	
	"""
	year = int(date[:4])
	month = int(date[4:6])
	day = int(date[6:8])

	fuzz = random.randint(-fuzz_parameter, fuzz_parameter)

	date = datetime(day = day, month = month, year = year)
	date = (date + timedelta(days = fuzz)).strftime("%Y%m%d")
	return date

def anonymize(filename, output_filename, PatientID = "test1", PatientName = "test1"):
	# Load the current dicom file to 'anonymize'
	dataset = pydicom.read_file(filename)

	dataset.PatientID = PatientID
	dataset.PatientName = PatientName

	# Same as above but for blanking data elements that are type 2.
	for name in ['PatientBirthDate']:
	    if name in dataset:
	        dataset.data_element(name).value = fuzz_date(dataset.data_element(name).value)
	        
	# write the 'anonymized' DICOM out under the new filename
	dataset.save_as(output_filename)

def anonymize_all(output_folder = ".",datapath = os.path.join("..","data"), subject_dicom_path = os.path.join("ses-*","*","*")):
	
	#Listing patient files.
	patients_folders = next(os.walk(datapath))[1]
	
	old2new_idx = {patients_folders[i] : str(i).zfill(6) for i in range(len(patients_folders))}
	
	for patient in tqdm(patients_folders) : 
		current_path = os.path.join(datapath, patient, subject_dicom_path)
		files = glob(current_path)

		for file in files:
			
			anonymize(file,os.path.join(output_folder,file), PatientID = old2new_idx[patient], PatientName = "FIFISIDKOM")
		os.rename(os.path.join(datapath , patient), os.path.join(datapath,"sub-"+old2new_idx[patient]))
	new2old_idx = {new : old.replace("sub-","") for old, new in old2new_idx.items()}
	
	return new2old_idx

def main(argv): 
	json_path = argv[0]
	print("Anonymizing ...")

	#Anonymizing all files.
	mapper = anonymize_all()

	#dumping new ids to a json file.
	with open(os.path.join(json_path,'mapper.json'), 'w') as fp:
		json.dump(mapper, fp)

if __name__ == "__main__" : 
	main(sys.argv[1:])