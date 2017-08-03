#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2017"
__license__= "Apache License, Version 2.0"
__email__= "mkechagiaATaueb.gr"


'''
This program parses the javadoc files (extracted from the doclet)
of each available version of an API (e.g. Android, Java, 3rd-party libaries)
and extracts API methods and documented exceptions
(i.e. exceptions in @throws and in throws in method signatures). 

Input: a folder with all available versions of
an API documentation reference (doclet output).
Output: a JSON file for each API version with API methods and exceptions.

Instructions:
- to independently run the doclet and use its output see doclet-instructions.txt
'''

import re
import os
# to store dictionary in JSON format
import json
import sys

from collections import defaultdict

global analysis_type
analysis_type = ""

def main():
	path_doc = sys.argv[1]
	analysis_type = sys.argv[2]
	read_new_javadoc_version(path_doc, analysis_type)

# open the javadoc files of the current API version 
def read_new_javadoc_version(path, analysis_type):
	print path
	# array for the different versions of API in the given folder
	api_versions = []
	for subdir, dirs, files in os.walk(path):
		api_versions = dirs
		break
	# parse the javadoc files of each API version
	for k, l in enumerate(api_versions):
		# initialize a new dictionary for the current API version (API methods and exceptions)
		doc_dict = {}
		# parse javadoc files 
		read_dir_doc(path + api_versions[k] + "/", doc_dict, analysis_type)
		# store the resulted dictionary in JSON file
		add_dict_to_JSON(api_versions[k], doc_dict)
		# calulate API methods and documented exceptions for the current API version
		calculate_API_methods_exceptions(api_versions[k], doc_dict)

# find files that exist in the documentation
def read_dir_doc(path, doc_dict, analysis_type):
	for subdir, dirs, files in os.walk(path):
		for file in files:
			# search only for files from doclet output
			e = re.search("\.javadoc.txt$", file)
			if e:
				fl = re.split("\.", file)
				# only public and protected methods are in the analysis
				p = subdir + "/" + fl[0] + ".javadoc.txt"
				parse_doc(p, doc_dict, analysis_type)

# parse given .txt file (doclet output)
def parse_doc(file, doc_dict, analysis_type):
	# counter for methods
	c = 0
	# dictionary for current examined method 
	dict = {}
	# exceptions dictionary for current examined method
	b = {}
	d = {}

	# keep the current file (class-not embedded)
	file_class = re.search(analysis_type+"/.*\.txt$", file).group()
	f_class = re.sub("/", ".", file_class)
	fl_class = re.sub(".javadoc.txt", "", f_class)

	# open and read file
	f = open(file)
	# add lines to a list
	lines = f.readlines()
	for l, k in enumerate(lines):
		if re.search("Method:", lines[l]):
			c = c + 1
			# keep method name with arguments and class name
			mthd_nm_arg = re.split(":", lines[l])
			mthd_nm = re.split("\n", mthd_nm_arg[1])
			# update method arguments, 
			# e.g. android.accessibilityservice.AccessibilityServiceInfo -> AccessibilityServiceInfo
			upd_method = update_md_args(mthd_nm[0], analysis_type)
			mthd_cl = fl_class + "." + upd_method
			if (mthd_cl in doc_dict.keys()):
				dict = doc_dict.get(mthd_cl)
				# for @throws comments
				b = dict.get("@throws")
				# for throws in method signature
				d = dict.get("throws")
			elif (mthd_cl not in doc_dict.keys()):
				doc_dict.setdefault(mthd_cl, dict)
				# for arguments comparison
				add_to_dict_mtd_args(mthd_cl, dict)
				b = dict.setdefault("@throws", [])
				d = dict.setdefault("throws", [])
			if ((l + 1) < len(lines)):
				if re.search("(Hidden|Method):", lines[l + 1]):
					# case: @hide method
					if re.search("Hidden:", lines[l + 1]):
						dict.setdefault("Hidden:", []).append("Y")
					c = 0
					dict = {}
					continue
				if re.search("Abstract method!", lines[l + 1]):
					if ((l + 2) < len(lines)) and (re.search("(Throws|Exception):", lines[l + 2])):
						dict.setdefault("Abstract:", []).append("Y")
					elif ((l + 2) < len(lines)) and ((re.search("Method:", lines[l + 2])) or (re.search("^\s*$", lines[l + 2]))):
						dict.setdefault("Abstract:", []).append("Y")
						c = 0
						dict = {}
						continue
		# for @throws comments
		elif (re.search("Throws:", lines[l]) and (c == 1)):
			thr = re.split(":", lines[l])
			th = re.split("\n", thr[1])
			t_exc = keep_exc_name(th[0])
			s_t_exc = re.sub("\<[\/]*code\>", "", t_exc)
			dict.setdefault("@throws", []).append(s_t_exc)
			if ((l + 1) < len(lines)):
				if re.search("Method:", lines[l + 1]) or (re.search("^\s*$", lines[l + 1])):
					c = 0
					dict = {}
					continue
		# for throws in method signature
		elif (re.search("Exception:", lines[l]) and (c == 1)):
			thr = re.split(":", lines[l])
			th = re.split("\n", thr[1])
			t_exc = keep_exc_name(th[0])
			dict.setdefault("throws", []).append(t_exc)
			if ((l + 1) < len(lines)):
				if re.search("Method:", lines[l + 1]) or (re.search("^\s*$", lines[l + 1])):
					c = 0
					dict = {}
					continue

# For keeping the same as in the following
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, android.util.AttributeSet)
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, AttributeSet)
# Also, if there is an arg from an embedded class, change $ to . 
# i.e. setOnItemSelectedListener(AdapterView.OnItemSelectedListener)
def update_md_args(method_sig, analysis_type):
	# list for the method signature args 
	method_sig_args = []
	# keep only the args of the method
	m_args = re.split("\(", method_sig)
	# split the method args to seek methods related to eac library
	l_args = re.split(",", m_args[1])
	for l, k in enumerate(l_args):
		n_sp = re.sub(" ", "", l_args[l])
		if (re.search(analysis_type, n_sp) and not re.search("\$", n_sp)):
			s_args = re.split("\.", n_sp)
			last_elem = s_args[len(s_args) - 1]
			if (re.search("\)", last_elem)):
				last_part = re.sub("\)", '', last_elem)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(last_elem)
		elif (re.search(analysis_type, n_sp) and re.search("\$", n_sp)):
			n_eb = re.sub("\$", ".", n_sp)
			s_args = re.split("\.", n_eb)
			last_el1 = s_args[len(s_args) - 1]
			last_el2 = s_args[len(s_args) - 2]
			last_elem = last_el2 + "." + last_el1
			if (re.search("\)", last_elem)):
				last_part = re.sub("\)", '', last_elem)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(last_elem)
		else:
			if (re.search("\)", n_sp)):
				last_part = re.sub("\)", '', n_sp)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(n_sp)
	return m_args[0] + "(" + ", ".join(method_sig_args) + ")"

# add method args in dict (for args comparison)
# caution! take care of <any> args in javadoc (e.g. for AccountManagerCallBack<Boolean> callback)
# caution! take care of vargs e.g. in android.animation.AnimatorSet.playSequentially(Animator...) but Animator[] in javadoc
def add_to_dict_mtd_args(mthd_cl, dict):
	args = []
	# split method to method name and args
	method_nm = re.split("\(", mthd_cl)
	method_args_1 = re.sub("\)", "", method_nm[1])
	method_args_2 = re.sub("[\s]*", "", method_args_1)
	if re.search(",", method_args_2):
		args = re.split(",", method_args_2)
		for k, l in enumerate(args):
			dict.setdefault("args", []).append(args[k])
	else:
		args = []
		dict.setdefault("args", []).append(method_args_2)

# keep only exception names (e.g. java.lang.IllegalArgumentException -> IllegalArgumentException)
# do not keep embedded exceptions (e.g. IntentSender$SendIntentException -> IntentSender.SendIntentException)
def keep_exc_name(exc):
	# for case java.lang.IllegalArgumentException
	if re.search("\.", exc):
		e_nm = re.split("\.", exc)
		l_elem = e_nm[len(e_nm) - 1]
		# for a case such as IntentSender$SendIntentException
		if re.search("\$", l_elem):
			n_emb = re.split("\$", l_elem)
			return n_emb[1]
		else:
			return l_elem
	# for a case such as IllegalArgumentException
	else:
		return exc

# calculate API methods and documented exceptions from doc_dict (current API version)
def calculate_API_methods_exceptions(api_version, doc_dict):
	count_doc = 0
	total = 0
	dict = {}
	keys = doc_dict.keys()
	total = len(keys)
	for k, l in enumerate(keys):
		dict = doc_dict.get(keys[k])
		# for @throws comments
		b = dict.get("@throws")
		# for throws in method signature
		d = dict.get("throws")
		if ((len(b) > 0) or (len(d) > 0)):
			count_doc = count_doc + 1
	
	# caution! take care of test methods in the API; here, we count all the methods.
	print "No of API methods with documented exceptions in version ", api_version, ": ", count_doc
	print "No of API methods in total in version ", api_version, ": ", total

# store dictionary in JSON file for permanent use
def add_dict_to_JSON(api_version, doc_dict):
	file_name = api_version+'.json'
	with open(file_name, 'w') as fp:
		json.dump(doc_dict, fp, indent = 4)

# run main
if __name__ == "__main__":
	main()