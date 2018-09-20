import pydicom

def main():
	filename = "/home/localadmin/Bureau/PACSMAN/data/sub-1051363/ses-20150203160809/MPRAGE_P3/MR.1.3.12.2.1107.5.2.43.67014.201502031612481792906060"
	dataset = pydicom.read_file(filename)
	attributes = dataset.dir("")

	for name in attributes : 
		try:
			if dataset.PatientID in dataset.data_element(name).value : 
				print(name)
		except TypeError: 
			continue
if __name__ == "__main__":
	main()