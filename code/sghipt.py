import shutil
from glob import glob
import os

def main():
	ls = glob("/home/localadmin/Bureau/for_davide/sub-*/ses-*/*.csv")
	for l in ls : 
		dir_ = "/home/localadmin/Bureau/teff"
		subfolder = os.path.join(dir_, l.split("/")[5])
		if not os.path.isdir(subfolder):
			os.mkdir(subfolder)

		subsubfolder = os.path.join(subfolder, l.split("/")[6])
		if not os.path.isdir(subsubfolder):
			os.mkdir(subsubfolder)

		shutil.move(l, os.path.join(subsubfolder,l.split("/")[-1]))

if __name__ == "__main__" : 
	main()