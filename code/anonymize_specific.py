from anonymize import *

def load_new_ids(path_to_query_file : str) -> list : 

	new_ids = list(read_csv(path_to_query_file , dtype=str).fillna("")["new_ids"])
	return new_ids