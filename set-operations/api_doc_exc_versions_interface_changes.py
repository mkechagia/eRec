#!/usr/bin/env python

'''
To run, update the following paths, go to cmd, and type:
python2 ./api_doc_exc_versions_interface_changes.py ./eRec-data/JSON/ android
'''

__author___= "Maria Kechagia"
__copyright__= "Copyright 2018"
__license__= "Apache License, Version 2.0"
__email__= "mkechagiaATaueb.gr"

'''
This program investigates the evolution of
the exception interfaces of the API methods.
We track only changes in the declared exceptions in
method signatures (i.e. throws).

Input: directory with .json files from Java APIs (documentation).

Output: report of the results of set operations on API documentation;
		it gives the evolution of the exception interfaces.
		How many times the exception interface changes?
		If it changes many times, it may break the client apps.

NOTE: You can comment out operations that you don't want to run and
	  remove comments to print the resulted sets of API methods and operations.
'''

import re
import os
import sys
import json

from collections import defaultdict
from collections import OrderedDict
from sets import Set

# for API reference documentation (doc)
global doc_dict
doc_dict = OrderedDict([])

def main():
	# path for .json file for the API documetation (doc)
	path_doc = sys.argv[1] # ./eRec-data/JSON/

	# type of the analysis
	analysis_type = sys.argv[2] # android, java, 3rd-party library

	track_exc_interface_changes(path_doc, analysis_type)

# check how often exception interfaces change
def track_exc_interface_changes(path_doc, analysis_type):
	doc_dict_r = OrderedDict([])
	
	for subdir, dirs, files in os.walk(path_doc):
		# we check Android API levels 14-23
		for i in range(14, 23):
			file = "android-" + str(i) + ".json"
			print file
			# dictionary for the new API version
			doc_dict_r = OrderedDict([])
			j_file = subdir + file
			doc_dict_r = decode_json(j_file)
			doc_dict_r_keys = doc_dict_r.keys()
			
			for k, l in enumerate(doc_dict_r_keys):
				if (not re.search("(T|test)", doc_dict_r_keys[k])):
					# flag to distinguish new API methods
					new_method = False
					if (doc_dict_r_keys[k] not in doc_dict.keys()):
						# in the first position is the counter for the changes
						doc_dict.setdefault(doc_dict_r_keys[k], []).append(0)
						new_method = True
					# get the exceptions of the new API version
					doc_exc = doc_dict_r.get(doc_dict_r_keys[k])
					# take into account only the exception interface i.e. throws in method signature
					sig_throws = Set(doc_exc.get('throws'))
					t_doc_exc = list(sig_throws)
					# flag to check for change in the interface
					change = False
					# get exceptions stored in dictionary for all the API versions
					values = doc_dict.get(doc_dict_r_keys[k])
					
					# new exceptions found in new API version
					if (len(t_doc_exc) > 0):
						prev_val = Set(values)
						next_val = Set(t_doc_exc)
						# elements in prev_val but not in next_val
						dif_prev_next_val = prev_val.difference(next_val)
						# elements in next_val but not in prev_val
						dif_next_prev_val = next_val.difference(prev_val)
						#print "api level"+ file
						#print "api" + doc_dict_r_keys[k]
						#print "prev_list" + str(prev_val)
						#print "next_val" + str(next_val)
						# length is greater than 1 because in the first position is the counter for the changes
						if (len(list(dif_prev_next_val)) > 1):
							if (new_method is False):
								# there are removed exceptions in new API version
								change = True
								# count change
								list_of_api_elems = doc_dict[doc_dict_r_keys[k]]
								list_of_api_elems[0] = list_of_api_elems[0] + 1
								remove_exceptions(list(dif_prev_next_val), doc_dict, doc_dict_r_keys[k])
								print file + ", api method: " + doc_dict_r_keys[k] + ", removed exceptions 1: " + str(list(dif_prev_next_val))
						if (len(list(dif_next_prev_val)) > 0):
							if (new_method is False):
								# there are added exceptions in new API version
								change = True
								list_of_api_elems = doc_dict[doc_dict_r_keys[k]]
								list_of_api_elems[0] = list_of_api_elems[0] + 1
								print file + ", api method: " + doc_dict_r_keys[k] + ", added exceptions: " + str(list(dif_next_prev_val))
							# add new exceptions in doc_dict (methods and exceptions from all versions)
							for c, d in enumerate(t_doc_exc):
								if (t_doc_exc[c] not in values):
									doc_dict.setdefault(doc_dict_r_keys[k], []).append(t_doc_exc[c])
					# no new exceptions in new API version
					elif (len(t_doc_exc) == 0):
						# in the first position is the counter for the changes
						if (len(values) <= 1):
							if (new_method is False):
								# there is no change in the exception interface
								continue
						elif ((len(values) > 1)):
							if (new_method is False):
								# there is change (removed exceptions) in the new API version
								change = True
								list_of_api_elems = doc_dict[doc_dict_r_keys[k]]
								list_of_api_elems[0] = list_of_api_elems[0] + 1
								remove_exceptions(values, doc_dict, doc_dict_r_keys[k])
								print file + ", api method: " + doc_dict_r_keys[k] + ", removed exceptions 2: " + str(values)
	return doc_dict

# decode json files into dictionary
def decode_json(f_json):
	try:
		with open(f_json) as f:
			return json.load(f)
	except ValueError:
		print 'Decoding JSON has been failed: ', f_json

# remove old exceptions from API
def remove_exceptions(prev_list_dif, curr_dict, api):
	for k, l in enumerate(prev_list_dif):
		if (prev_list_dif[k] in curr_dict[api]):
			curr_dict[api].remove(prev_list_dif[k])

# run main
if __name__ == "__main__":
	main()