import shutil
from glob import glob
import os
import tqdm
import sys

def main(argv):

	dicom_path = argv[0]
	output_path = argv[1]
	ls = glob(os.path.join(dicom_path,"sub-*","ses-*","*.csv"))
	
	for l in ls : 
		path = os.path.normpath(l)
		path = path.split(os.sep)

		dir_ = output_path
		subfolder = os.path.join(dir_, path[-3])
		if not os.path.isdir(subfolder):
			os.mkdir(subfolder)

		subsubfolder = os.path.join(subfolder, path[-2])
		if not os.path.isdir(subsubfolder):
			os.mkdir(subsubfolder)

		shutil.move(l, os.path.join(subsubfolder, path[-1]))

if __name__ == "__main__" : 
	main(sys.argv[1:])