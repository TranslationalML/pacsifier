import shutil
from glob import glob
import os
import tqdm
import sys
import json
import pandas as pd
import pydicom

def main(argv):

	dicom_path = argv[0]
	output_path = argv[1]
	json_file = argv[2]
	table = pd.read_csv(argv[3])
	with open(json_file) as j :
		dict_ = json.load(j)
	dict_ = {v: k for k, v in dict_.items()}

	for i in table.index:
		try:
			ls = glob(os.path.join(dicom_path,"sub-{}".format(dict_[str(int(table["PatientID"][i]))]),"ses-{}".format(table["StudyDate"][i])+"*","*","*"))
		except KeyError : 
			with open("missing_keys","a") as f:
				f.write(str(int(table["PatientID"][i])))
				continue

		for l in ls : 
			try :  
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
				#shutil.move(l, os.path.join(subsubsubfolder, path[-1]))
			except FileNotFoundError: 
				with open("not_found.txt","a") as f:
					f.write(os.path.join(subfolder,path[-4],path[-3],path[-2]) )
					continue


if __name__ == "__main__" : 
	main(sys.argv[1:])