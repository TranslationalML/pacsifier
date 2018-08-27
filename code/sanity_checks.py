from datetime import datetime

def check_ip(ip_address : str) : 
	"""
  	Checks if an ip adress is valid. Raises a ValueError if not the case.
  	Args : 
		ip_address (string) : ip_address
	"""
	message = "Invalid ip address"
	if len(ip_address.split(".")) != 4 : 
		raise ValueError(message)
	ip_splitted = ip_address.split(".")

	for i in ip_splitted : 
		if i == "" or len(i) > 3: 
			raise ValueError(message)
		try: 
			int(i)
		except ValueError:
			raise ValueError(message)
	return

def check_port(port : int) : 
	"""
  	Checks if a port value is valid. Raises a ValueError if not the case.
  	Args : 
		port (int) : port number.
	"""
	if port > 65535 : 
		raise ValueError("Port number is too big!")
	if port < 1 : 
		raise ValueError("Port number is smaller or equal to zero!")
	return 

def check_AET(AET : str, server = False) : 
	"""
  	Checks the validity of an AE title. Raises an error if not the case and uses a boolean to print a relevant error message.
  	Args : 
		AET (string) : AE title
		server (boolean) : boolean indicating if it is a AE title of a server or not.
	"""
	add = ""
	if server : add = "Server"
	if AET == "" : 
		raise ValueError("Empty "+add+ " AET passed")
	if len(AET) > 16 : 
		raise ValueError(add + "AET is too long")
	return 

def check_parameters_inputs(
	AET : str,
	server_ip : str,
	server_AET : str,
	port : int) : 
	"""
  	Checks if the parameters are valid using helper functions. Raises a ValueError if at least one parameter is invalid.
  	Args : 
		AET (string) : Called AET
		server_ip (string) : server ip
		server_AET (string) : server_AET
		port (int) : port 
	"""

	
	check_AET(AET)
	check_AET(server_AET, server = True)
	check_port(port)
	check_ip(server_ip)

	return

def check_dates(date : str) :
	"""
  	Checks if a date is valid. Raises a ValueError if not the case.
  	Args : 
		date (string) : date
	"""

	message = "Invalid date input" 
	splitted_date = date.split("/")

	for split in splitted_date : 
		try : 
			int(split)
		except ValueError : 
			raise ValueError(message)
	
	if(len(splitted_date) != 3 
		or int(splitted_date[1]) > 12 
		or int(splitted_date[1]) < 1 
		or int(splitted_date[0]) < 1 
		or int(splitted_date[0]) > 31 
		or int(splitted_date[2]) < 0
		or int(splitted_date[2]) > 99): 
		raise ValueError(message)

	return

def check_ids(UID : str, attribute : str = "Patient ID"):
	"""
  	Checks if an id is valid. Raises ValueError if not the case and prints a relevant error message using the argument called attribute.
  	Args : 
		UID (string) : Unique identifier.
		attribute (string) : The attribute name.
	"""
	
	if UID == "" : 
		raise ValueError("Emtpy " + attribute+" passed")
	if len(UID) > 64 : 
		raise ValueError(attribute + " is too long")
	return 
	
def check_filter(filter_text : str) : 
	"""
	Checks if an additional input filter is valid. 
	Args : 
		filter_text (string) : 
	"""
	if len(filter_text.split("=")) != 2 : raise ValueError("Invalid filter input.")