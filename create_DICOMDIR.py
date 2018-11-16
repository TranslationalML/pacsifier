import sys
import os
import warnings
import string 
import numpy as np
import random
from PACSMAN.code.execute_commands import run
from glob import glob
import shutil
from pydicom.filereader import read_dicomdir
warnings.filterwarnings("ignore")

numbers = [str(i) for i in range(10)]
command = "dcmmkdir --recurse {}"
names = []

def generate_new_folder_name(names : list = []) -> str:
	"""
	Generates a folder/file name having between 4 and 8 characters of capital letters and digits.
	Args : 
		names (list) : new names already generated for other folders.
	Returns : 
		str : Generated folder/file name.
	"""
	generated = ""
	new_names = names + [""]
	
	while (generated in new_names):
		N = random.randint(4,8)
		generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

	return generated
def add_or_retrieve_name(current_folder : str, old_2_new : dict) -> tuple: 
	"""
	Checks if the current folder has had a generated new name. If that is the case, return its new name, otherwise, generate a new name.
	Args : 
		current_folder (str) : Current folder to be considered.
		old_2_new (dict) : Dictionary keeping track of mapping between old and new folder/file names.
	Returns : 
		tuple : tuple containing the new name and the updated mapping between old and new name.
	"""
	folder_name = None 

	if current_folder not in old_2_new.keys():
		folder_name = generate_new_folder_name()
		old_2_new[current_folder] = folder_name
		names.append(folder_name)
		
	else : 
		folder_name = old_2_new[current_folder]

	return folder_name, old_2_new
def move_and_rename_files(dicom_path : str, output_path : str) -> None : 
	"""
	Copies all the files within the dicom hierarchy into new hierarchy with appropriate names for DICOMDIR creation.
	Args : 
		dicom_path (str) : Current folder to be considered.
		output_path (str) : Path where the new dicom hierarchy will be stored.
	"""

	#List all dicom files paths. 
	ls = glob(os.path.join(dicom_path,"sub-*","ses-*","*","*"))
	old_2_new = {}

	#Iterating over dicom files
	for l in ls : 
	
		path = os.path.normpath(l)
		path = path.split(os.sep)
		
		dir_ = output_path

		#Creating subject folder with 8 characters names.
		current_folder = path[-4]
		folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
		subfolder = os.path.join(dir_, folder_name)

		if not os.path.isdir(subfolder):
			os.mkdir(subfolder)

		#Creating session folder with 8 characters names.
		current_folder = path[-3]
		folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
		subsubfolder = os.path.join(subfolder, folder_name)

		if not os.path.isdir(subsubfolder):
			os.mkdir(subsubfolder)

		#Creating series folder with 8 characters names.
		current_folder = path[-2]
		folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
		subsubsubfolder = os.path.join(subsubfolder, folder_name)
		
		if not os.path.isdir(subsubsubfolder):
			os.mkdir(subsubsubfolder)

		#Copying dicom files into the previously created series folder with 8 characters or less names.
		file_name = generate_new_folder_name(names = names)
		shutil.copyfile(l, os.path.join(subsubsubfolder, file_name))
def create_dicomdir(out_path : str) -> None : 
	"""
	Create a DICOMDIR of all dicoms with the path passed as parameter.
	Args : 
		out_path (str) : Path of dicoms
	"""
	os.chdir(os.path.abspath(out_path))
	run(command.format("./"))

def main(argv):
	
	in_path = argv[0]
	out_path = argv[1]

	move_and_rename_files(in_path, out_path)
	create_dicomdir(out_path)
	
if __name__ == "__main__":
	main(sys.argv[1:])