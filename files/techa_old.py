import shutil
from glob import glob
import os
import tqdm
import sys
import json
import pandas as pd

def main(argv):

	dicom_path = argv[0]
	json_file = argv[1]
	table = pd.read_csv(argv[2])
	print(json_file)
	with open(json_file) as j :
		dict_ = json.load(j)
	dict_ = {v: k for k, v in dict_.items()}

	for i in table.index:
		try:
			ls = glob(os.path.join(dicom_path,"sub-{}".format(dict_[str(int(table["PatientID"][i]))]),"ses-{}".format(table["StudyDate"][i])+"*","*","*"))
			if len(ls) == 0 : 
				print("lol")
				print(os.path.join(dicom_path,"sub-{}".format(dict_[str(int(table["PatientID"][i]))]),"ses-{}".format(table["StudyDate"][i])))
				with open("not_found.txt","a") as f:
					f.write(os.path.join(dicom_path,"sub-{}".format(dict_[str(int(table["PatientID"][i]))]),"ses-{}".format(table["StudyDate"][i])))

		except KeyError : 
			with open("missing_keys","a") as f:
				f.write(str(int(table["PatientID"][i])))
				continue

if __name__ == "__main__" : 
	main(sys.argv[1:])