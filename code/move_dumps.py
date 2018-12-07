import shutil
from glob import glob
import os
import sys
import argparse 

def move(dicom_path, output_path):


	#List all csv files within the folder containing the dicom images.
	ls = glob(os.path.join(dicom_path,"sub-*","ses-*","*.csv"))
	
	#Iterate over all csv files paths.
	for l in ls : 
		path = os.path.normpath(l)
		path = path.split(os.sep)

		#Create patient folder if not created yet.
		dir_ = output_path
		subfolder = os.path.join(dir_, path[-3])
		if not os.path.isdir(subfolder):
			os.mkdir(subfolder)

		#Create session folder if not created yet.
		subsubfolder = os.path.join(subfolder, path[-2])
		if not os.path.isdir(subsubfolder):
			os.mkdir(subsubfolder)

		#Move the csv file into the session folder.
		shutil.move(l, os.path.join(subsubfolder, path[-1]))

def main(argv) : 
	parser = argparse.ArgumentParser()

	parser.add_argument('--data_folder', "-d", help = "Path to the dicom folder")
	parser.add_argument('--info_folder', "-o", help = "Path to the folder where all csv files will be moved")

	args = parser.parse_args()
	
	if not args.data_folder or not args.info_folder : 
		parser.print_help()
		sys.exit()

	dicom_path = args.data_folder
	output_path = args.info_folder
	
	move(dicom_path, output_path)

if __name__ == "__main__" : 
	main(sys.argv[1:])