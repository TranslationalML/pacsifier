import shutil
from glob import glob
import os
import tqdm
import sys
import json
import pandas as pd

def main(argv):

	dicom_path = argv[0]
	output_path = argv[1]
	json_file = argv[2]
	table = pd.read_csv(argv[3])
	with open(json_file) as j :
		dict_ = json.load(j)
	dict_ = {v: k for k, v in dict_.items()}

	for i in table.index:
		
		ls = glob(os.path.join(dicom_path,"sub-{}".format(dict_[str(int(table["PatientID"][i]))]),"ses-{}".format(table["StudyDate"][i])+"*","*","*"))
		
		for l in ls : 
			path = os.path.normpath(l)
			path = path.split(os.sep)

			dir_ = output_path
			subfolder = os.path.join(dir_, path[-4])
			if not os.path.isdir(subfolder):
				os.mkdir(subfolder)

			subsubfolder = os.path.join(subfolder, path[-3])
			
			if not os.path.isdir(subsubfolder):
				os.mkdir(subsubfolder)
			subsubsubfolder = os.path.join(subfolder, path[-2])
			
			if not os.path.isdir(subsubsubfolder):
				os.mkdir(subsubsubfolder)
			shutil.move(l, os.path.join(subsubsubfolder, path[-1]))

if __name__ == "__main__" : 
	main(sys.argv[1:])