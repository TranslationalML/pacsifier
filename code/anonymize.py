import pydicom
from datetime import datetime, timedelta
from glob import glob
import sys
import os
from tqdm import tqdm
import random

def fuzz_date(date, fuzz_parameter = 60): 
    
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


def main(argv): 
	path = argv[0]
	print("Anonymizing ...")
	files = glob(os.path.join(path,'*'))

	for file in tqdm(files) : 
		
		anonymize(file, file)

if __name__ == "__main__" : 
	main(sys.argv[1:])