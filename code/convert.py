from glob import glob
from PACSMAN.code.execute_commands import run
import os
from tqdm import tqdm
import sys
import nipype

def process_list(paths : list) -> list:
	"""
	Extracts subject and session identifiers as stored in data folder.
	Args :
		paths (list) : list of paths
	Returns :
		list : list of tuples like (subject, session).
	"""
	tuples = []
	for l in paths : 
		path = os.path.normpath(l)
		path = path.split(os.sep)
		tuples.append((path[-2].split("-")[-1], path[-1].split("-")[-1]))
	return tuples

def convert_to_nifti(subject : str, session : str , base : str) -> None:
	"""
	Converts the subject and session in base directory corresponding dicom files to nifti.
	Args :
		subject (string) : subject identifier
		session (string) : session identifier
		base (string) : directory path
	"""

	#Get the directory where this file is (PACSMANS/code)
	dirname = os.path.dirname(__file__)

	#Creating the command.
	command = "heudiconv -d  {}/sub-{}/ses-{}/*/* -o {} -f {} -s {} -ss {} -c dcm2niix -b --overwrite".format(
		base,
		"{subject}",
		"{session}",
		os.path.join(base,"Nifti"),
		os.path.join(dirname,"heuristic.py"),
		subject,
		session)
	
	#Running the command.
	run(command)

def convert_all(base : str) -> None:
	"""
	Converts all dicom files within base directory to nifti files.
	Args :
		base (string) : base directory path.
	"""

	global_path = os.path.join(base, "sub-*","*")

	paths = glob(global_path )
	tuples = process_list(paths)

	abs_path = os.path.abspath(base)

	print("Converting dicom files within path " + abs_path + " to nifti ..." )
	for tuple_ in tqdm(tuples) :
		convert_to_nifti(tuple_[0], tuple_[1], abs_path)


def main(argv) :
	convert_all(argv[0])

if __name__ == "__main__" :
	main(sys.argv[1:])
