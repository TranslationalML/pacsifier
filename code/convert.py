from glob import glob
from execute_commands import run
import os
from tqdm import tqdm
import sys


def list_files(path : str) -> list : 
	"""
	returns a list of all files within path passed as parameter.
	Args : 
		path (string) :directory path
	Returns : 
		list : list of paths.
	"""
	return glob(path)

def process_list(paths : list) -> list: 
	"""
	Extracts subject and session identifiers as stored in data folder.
	Args : 
		paths (list) : list of paths
	Returns : 
		list : list of tuples like (subject, session).
	"""
	tuples = [(path.split("/")[-2].split("-")[-1], path.split("/")[-1].split("-")[-1]) for path in paths]
	return tuples

def convert(subject : str, session : str , base : str) :
	"""
	Converts the subject and session in base directory corresponding dicom files to nifti.
	Args : 
		subject (string) : subject identifier
		session (string) : session identifier
		base (string) : directory path
	"""
	
	command = "docker run --rm -it -v {}:/base -v {}/Nifti/code/heuristic.py:/base/Nifti/code/heuristic.py nipy/heudiconv:latest -d /base/sub-{}/ses-{}/*/* -o /base/Nifti -f /base/Nifti/code/heuristic.py -s {} -ss {} -c dcm2niix -b --overwrite".format(
		base,
		base,
		"{subject}",
		"{session}",
		subject,
		session)
	
	return run(command) 
#glob("../data/Nifti/sub-*/*")
def convert_all(base) :
	"""
	Converts all dicom files within base directory to nifti files
	Args : 
		base (string) : base directory path.
	"""
	
	global_path = os.path.join(base, "sub-*","*")
	paths = list_files(global_path )
	tuples = process_list(paths)
	
	abs_path = os.path.abspath(base)
	print("Converting dicom files to nifti")
	for tuple_ in tqdm(tuples) :
		run = convert(tuple_[0], tuple_[1], abs_path)


def main(argv) : 
	convert_all(argv[0])

if __name__ == "__main__" : 
	main(sys.argv[1:])