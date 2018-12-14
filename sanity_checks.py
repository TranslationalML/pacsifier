from datetime import datetime
from typing import Dict

def check_ip(ip_address : str) -> None: 
	"""
  	Checks if an ip adress is valid. Raises a ValueError if not the case.
  	Args : 
		ip_address : IP address
	"""
	message = "Invalid IP address"
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

def check_port(port : int) -> None : 
	"""
  	Checks if a port value is valid. Raises a ValueError if not the case.
  	Args : 
		port : port number.
	"""
	if port > 65535 : 
		raise ValueError("Port number is too big!")
	if port < 1 : 
		raise ValueError("Port number is smaller or equal to zero!")
	return 

def check_AET(AET : str, server = False) -> None : 
	"""
  	Checks the validity of an AE title. Raises an error if not the case and uses a boolean to print a relevant error message.
  	Args : 
		AET: AE title
		server : boolean indicating if it is a AE title of a server or not.
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
	port : int) -> None : 
	"""
  	Checks if the parameters are valid using helper functions. Raises a ValueError if at least one parameter is invalid.
  	Args : 
		AET : Called AET
		server_ip : server ip
		server_AET : server_AET
		port : port 
	"""
	check_AET(AET)
	check_AET(server_AET, server = True)
	check_port(port)
	check_ip(server_ip)

	return

def check_ids(UID : str, attribute : str = "Patient ID") -> None:
	"""
  	Checks if an id is valid. Raises ValueError if not the case and prints a relevant error message using the argument called attribute.
  	Args : 
		UID : Unique identifier.
		attribute : The attribute name.
	"""
	
	if len(UID) > 64 : 
		raise ValueError(attribute + " is too long")
	return 
	
def check_filter(filter_text : str) -> None : 
	"""
	Checks if an additional input filter is valid. 
	Args : 
		filter_text : additional attribute to the query command.
	"""
	if len(filter_text.split("=")) != 2 : raise ValueError("Invalid filter input.")

def check_tuple(tuple_ : Dict[str,str]) -> None : 
	"""
	Checks that the table has an acceptable input parameters. 
	Args : 
		tuple_ : dictionary that contains all parameters for query.
	"""
	empty = True
	for item in tuple_.values() : 
		if str(item) == "*" : 
			raise ValueError("Can't use * for inputs !")
		if len(str(item)) > 0 : 
			empty = False

	if empty : raise ValueError("Empty line in table ! ")

def check_date_range(date : str) -> None:
	"""
	Checks that a date (possibly a date range) is valid.
	Args : 
		date : date or date range to be checked.
	"""
	if date == "" : return 
	if len(date) == 17: 
		if len(date.split("-")) != 2 : 
			raise ValueError("Invalid date range input!")
		dates = date.split("-")

		check_date(dates[0])
		check_date(dates[1])
	else : check_date(date)
	return

def check_date(date : str) -> None:
	"""
	Checks that a date is valid.
	Args : 
		date : date to be checked.
	"""

	if date == "" : return
	if len(date) != 8 : 
		raise ValueError("Invalid date input")
	try : 
		int(date)
	except ValueError : 
		raise ValueError("Date must contain only numeric characters!")
	year, month, day = int(date[:4]), int(date[4:6]), int(date[6:])

	if year < 1900 or year > datetime.now().year : 
		raise ValueError("Invalid year range!")
	if month not in range(1,13) : 
		raise ValueError("Invalid month range!")
	if day not in range(1,32) : 
		raise ValueError("Invalid day value!")
	return


def check_config_file(config_file : Dict[str,str]) -> None : 
	"""
	Checks that the config file passed as a parameter is valid or not.
	Args: 
		dict : dictionary loaded from the config json file.
	"""
	items = set(config_file.keys())
	if items != set(["server_ip","port","server_AET","AET","move_port","batch_size","batch_wait_time"]) : 
		raise ValueError("Invalid config file!")

def check_query_retrieval_level(query_retrieval_level : str) -> None : 

	valid_levels = ["SERIES","PATIENT","IMAGE","STUDY"]
	if query_retrieval_level not in valid_levels : 
		raise ValueError("Invalid query retrieval level ! ")