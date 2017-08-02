#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2017"
__license__= "Apache License, Version 2.0"
__email__= "mkechagiaATaueb.gr"

'''
This program gathers API method signatures and might-thrown exceptions
from all API versions.

Input: .json files (from all API versions) from Android, Java's platform, and libraries' API reference and source code.

Output: .json file for the API reference (total versions) and
		.json file for the API source code (total versions).

Note 1: You need to run this script only once to store the data from all the API versions into one .json file.
	    Wait, it will take some time for the script to finish!
Note 2: When running the script give as an argument the path where all the .json files from the API versions exist (../eRec/api/JSON/)
		The .json files have been created in a previous step (see the instructions),
		from the static analysis (using doclet and Soot) on each API version.

'''

import re
import os
import sys

import json

from collections import defaultdict
from collections import OrderedDict
from sets import Set

# dictionary for methods and exceptions from the API reference documentation (doc)
global doc_dict
doc_dict = OrderedDict([])

# android, java, 3rd-party libraries e.g. apache-commons-lang
global analysis_type
analysis_type = ""

# dictionary for methods and exceptions from the API source code (sc)
global sc_dict
sc_dict = OrderedDict([])

def main():
	# path (../eRec/api/JSON/) for .json files (from all API versions) for the documetation (doc) and source code (sc)
	path = sys.argv[1]
	analysis_type = sys.argv[2]
	
	# dictionary from all API reference documentation versions (and total_versions.json)
	doc_dict = update_doc_dict_total_ver(path, analysis_type)
	add_dict_to_JSON(doc_dict, analysis_type)

	# dictionary from all API (source code) versions (total_versions_sc.json)
	sc_dict = update_sc_dict_total_ver(path, analysis_type)
	add_dict_to_JSON_sc(sc_dict, analysis_type)

# store API methods and exceptions from documentation -all versions
def update_doc_dict_total_ver(path, analysis_type):
	doc_dict_r = OrderedDict([])
	for subdir, dirs, files in os.walk(path):
		for file in files:
			if (re.search(analysis_type + "-[0-9.]+.json$", file)):
				doc_dict_r = OrderedDict([])
				j_file = subdir + file
				doc_dict_r = decode_json(j_file)
				print 'API methods in ', file, ': ', len(doc_dict_r) # number of methods in each version
				doc_dict_r_keys = doc_dict_r.keys()
				for k, l in enumerate(doc_dict_r_keys):
					# update keys
					if (doc_dict_r_keys[k] not in doc_dict.keys()):
						doc_dict.setdefault(doc_dict_r_keys[k], [])
					# update exceptions
					doc_exc = doc_dict_r.get(doc_dict_r_keys[k])
					at_throws = Set(doc_exc.get('@throws'))
					sig_throws = Set(doc_exc.get('throws'))
					t_doc_exc = list(at_throws.union(sig_throws))
					if (len(t_doc_exc) > 0):
						values = doc_dict.get(doc_dict_r_keys[k])
						for c, d in enumerate(t_doc_exc):
							if (t_doc_exc[c] not in values):
								doc_dict.setdefault(doc_dict_r_keys[k], []).append(t_doc_exc[c])
	return doc_dict

# store dictionary for API documentation (doc) in JSON file for permanent use (all API versions)
def add_dict_to_JSON(doc_dict, analysis_type):
	file_name = "total_versions_" + analysis_type + ".json"
	with open(file_name, 'w') as fp:
		json.dump(doc_dict, fp, indent = 4)

# storer API methods and exceptions from source code -all versions
def update_sc_dict_total_ver(path, analysis_type):
	sc_dict_r = OrderedDict([])
	# for total API versions
	for subdir, dirs, files in os.walk(path):
		for file in files:
			if (re.search(analysis_type + "-[0-9.]+_source.json$", file)):
				sc_dict_r = OrderedDict([])
				j_file = subdir + file
				sc_dict_r = decode_json(j_file)
				print 'API methods in ', file, ': ', len(sc_dict_r) # number of methods in each version
				sc_dict_r_keys = sc_dict_r.keys()
				for k, l in enumerate(sc_dict_r_keys):
					# update keys
					if (sc_dict_r_keys[k] not in sc_dict.keys()):
						sc_dict.setdefault(sc_dict_r_keys[k], [])
					# update exceptions
					sc_exc = sc_dict_r.get(sc_dict_r_keys[k])
					intra = Set(sc_exc.get('intra_proced'))
					inter = Set(sc_exc.get('inter_proced'))
					t_sc_exc = intra.union(inter)
					if (len(t_sc_exc) > 0):
						values = sc_dict.get(sc_dict_r_keys[k])
						l_t_sc_exc = list(t_sc_exc)
						for c, d in enumerate(l_t_sc_exc):
							if (l_t_sc_exc[c] not in values):
								sc_dict.setdefault(sc_dict_r_keys[k], []).append(l_t_sc_exc[c])
	return sc_dict

# store dictionary for API source code (sc) in JSON file for permanent use (all API versions)
def add_dict_to_JSON_sc(sc_dict, analysis_type):
	file_name = "total_versions_sc_" + analysis_type + ".json"
	with open(file_name, 'w') as fp:
		json.dump(sc_dict, fp, indent = 4)

# decode json files into dictionary
def decode_json(f_json):
	try:
		with open(f_json) as f:
			return json.load(f)
	except ValueError:
		print 'Decoding JSON has been failed: ', f_json

# run main
if __name__ == "__main__":
	main()
