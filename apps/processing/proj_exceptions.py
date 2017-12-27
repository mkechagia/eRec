#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2017"
__license__= "Apache License, Version 2.0"
__email__= "mkechagiaATaueb.gr"

'''
This program parses .jimple files (Soot output) from each provided Java project (app)
and extracts API methods and exceptions that developers use (to handle called API methods).
Then, it gets the API methods and exceptions that are documented in the corresponding 
version of the API reference (depending on what API version each app uses).
Finally, it applies set operations on both datasets (app and API)
to find documented/undocumented exceptions.

Input: 
Folder with jimple files (Soot output) from each .jar file (app);
the folder with the .jimple files has the same name with the .jar file,
the soot_log.txt file keeps records regarding the processing when Soot is runnig.

Output: 
exceptions that are documented/undocumented (XX-doc-excps.txt, XX-undoc-excps.txt)
in the used API version; where XX is the name of the given Java API.

Instructions to independently run the script:
- before you run the script, cd to ../eRec/apps/jar/ (path for the folder with the output .jimple files)
- in the following program, the path_jar is for the folder with the apps --- .jar files
- in the following program, set ../eRec/api/JSON/ (path for the folder with the JSON files --- different API versions)

Note 1: soot_log.txt doen't keep the API version that the app uses (as in the case of the Android).
For this, we need to set on our own the API version in the java_version field below.

Note 2: this script can be used for the Java API and for Java libraries (e.g. apache-commons-lang).
We take into consideration only the .java files typically found in src/(main)/java package of the libraries.
E.g. see the structure of the packages of the source code of the apache-commons-lang3-3.6 for instance:
(https://github.com/apache/commons-lang/tree/master/src/main/java/org/apache/commons/lang3)

'''

# for regex
import re
# for os walking
import os
# for json decoding
import json
import sys

# for dictionaries
from collections import defaultdict
from collections import OrderedDict
# for set operations
from sets import Set

# dictionary of API methods and exceptions in a single .jar
global app_dict
app_dict = OrderedDict([])

# patterns for finding method signatures
p1 = "\s[a-zA-Z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws)*.*$"
p2 = "[\s]*\{[\s]*$"
# pattern for constructors
p3 = "\<[c]*[l]*init\>\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
# patterns for thrown exceptions
p4 = "catch\s"
p6 = "(specialinvoke|staticinvoke|virtualinvoke)\s"
p7 = "throw\s"
p8 = "[a-zA-Z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p9 = "\$r[0-9]+"
p10 = "[a-z]+[a-zA-Z0-9\$]*\(.*\)"
# pattern to locate API method in jimple files from Android apks or jars
# (e.g. $r5 = virtualinvoke $r3.<android.view.View: android.view.View findViewById(int)>($i0);)
#p11 = "(specialinvoke|staticinvoke|virtualinvoke).*[\<](java)\..*\s[a-z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
# pattern for catch clause
p12 = "catch.*[\s]+from[\s]+label[0-9]+[\s]+to[\s]+label[0-9]+[\s]+with[\s]+label[0-9]+"
# pattern for new label
p13 = "^[\s]*label[0-9]+\:[\s]*$"
# patterns for cases in a method
p14 = "lookupswitch\(\$i[0-9]+\)"

# folder for the jimple files from the .jar files
global path_jar
path_jar = sys.argv[1] # "../eRec/apps/jar/"
# folder for the JSON files (different versions of the API)
global path_JSON
path_JSON = sys.argv[2] # "../eRec/api/JSON/"
global java_version
java_version = sys.argv[3] # e.g. java 7, java 8, apache-commons-lang-3.6 etc.
global analysis_type
analysis_type = sys.argv[4] # java, apache-commons-lang, etc.

# Open a new file for doc exceptions
global fi
fi = open(analysis_type+"-doc-excps.txt", "wb")
# Open a new file for undoc exceptions
global fo
fo = open(analysis_type+"-undoc-excps.txt", "wb")
global p11
p11 = "(specialinvoke|staticinvoke|virtualinvoke).*[\<]("+analysis_type+")\..*\s[a-z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"

def main():
	# open and parse apk files
	read_folder(path_jar, java_version)
	# Close files
	fi.close()
	fo.close()

def read_folder(path, java_version):
	app_name = ""
	# list app folders (first level subfolders)
	dir_list = os.walk(path).next()[1]
	for k, l in enumerate(dir_list):
		app_name = dir_list[k]
		if ((re.search("^derbyTesting$", app_name)) or (re.search("^asm-3.1$", app_name)) or (re.search("^antlr-3.1.3$", app_name))):
			print "Possible issues with these .jar files ..."
			continue
		else:
			print app_name
			app_path = path + "/" + dir_list[k]
			# search in the files of the app folder
			files = os.listdir(app_path)
			if ((len(files) > 2) and (java_version != "")):
				# update doc_dictionary for the currently used API version
				doc_dict = get_right_API_version(java_version)
				read_files(files, app_path, java_version, doc_dict, app_name)

def read_files(files, app_path, api_ver, doc_dict, app_name):
	for f in files:
		# check for libraries included in Soot
		e = (not re.search("^(java)\..*", f)) and re.search("\.jimple$", f)
		if e:
			j_file = app_path + "/" + f
			parse_jimple(j_file, doc_dict, app_name, api_ver)
		d = re.search("^(java)\..*", f) and re.search("\.jimple$", f)
		if d:
			l = app_path + "/" + f

# get the version of the API platform that the examined app uses
# you hava set the java version when run the script
def get_right_API_version(java_version):
	api_dict = OrderedDict([])
	api_dict = read_right_javadoc_version(java_version)
	return api_dict

# find and read the right JSON file for the corresponding API version
def read_right_javadoc_version(api_version):
	if (api_version) is not None :
		is_api_version = False
		json_file = analysis_type + "-" + api_version + ".json" # for 3rd-party Java libs find the right .json file, i.e.: json_file = "commons-io-2.5.json"
		for subdir, dirs, files in os.walk(path_JSON):
			for name in files:
				if re.search(json_file, name):
					is_api_version = True
					return decode_json_doc(path_JSON + "/" + json_file)
		if (is_api_version == False):
			print 'Not found API version: ', api_version
			raise IOError

# decode json files into dictionary
def decode_json_doc(f_json):
	print "json file ", f_json
	try:
		with open(f_json) as f:
			return json.load(f)
	except ValueError:
		print 'Decoding JSON has been failed: ', f_json

# parse current jimple file
def parse_jimple(file, doc_dict, app_name, api_ver):
	# flag for a new method
	is_method = 0
	# class where the method belongs to
	cl_m = ""
	# total method with class
	t_method = ""
	# keep the current method (including the class)
	initial_method = ""
	# method's dictionary (label: lines, API methods, exceptions)
	m_dict = OrderedDict([])
	# method's subdictionary (one dict per label -see above)
	attributes = {}
	# for a new label block
	is_new_level = 0
	# new label's name
	new_label = ""
	# flag for a new label
	is_label = 0

	# keep the file (class-not embedded) that current methods belongs to
	file_class = re.search(".*\.jimple$", file).group()
	fl_class = re.sub(".jimple", "", file_class)
	if (re.search("\$", fl_class)):
		cl_m = re.sub("\$.*.$", "", fl_class)
	else:
		cl_m = fl_class

	f = open(file)
	lines = f.readlines()
	for l, k in enumerate(lines):
		# in case of new method signature
		if ((l + 1 < len(lines)) and not (re.search(p14, lines[l])) and (re.search(p1, lines[l]) and re.search(p2, lines[l + 1])) and (is_new_level == 0) and (is_method == 0)):
			method_sig = re.search(p1, lines[l]).group()
			method_s = re.search(p8, method_sig).group()
			method_nm = re.split("\(", method_s)
			upd_method = update_md_args(method_s)
			t_method = cl_m + "." + upd_method
			# keep only method and cut the previous path
			cl_m_l = re.split("/", cl_m)
			# keep class, method and signature
			tmthd = cl_m_l[len(cl_m_l) - 1] + "." + upd_method
			initial_method = t_method
			# change flag to indicate the existance of a new method signature
			is_method = 1
			# update dictionary of the application -> add new dictionary for a new method
			app_dict.setdefault(initial_method, m_dict)
			# new dictionary for the current method -> intialize dict
			m_dict = OrderedDict([])
			# change flag for new label to 0
			is_new_level = 0
			# not known label name yet
			new_label = ""
			# get a subset of the lines in the current jimple file
			lines_l = lines[l:]
			# in case of there is not any label in the current method
			if (is_exist_label(lines_l) == False):
				# change flag to show that we are in a new level - key -block
				is_new_level = 1
				# define that we haven't got a new label
				new_label = "withoutLabel"
				# add the new label as key in the current method dictionary
				# subdictionary for m_dict
				attributes = {}
				#attributes.setdefault("lines", [])
				attributes.setdefault("api_methods", [])
				attributes.setdefault("exceptions", [])
				m_dict.setdefault(new_label, attributes)
		# in case of a new label, add new label -key in method dictionary
		if ((l + 1 < len(lines)) and (re.search(p13, lines[l])) and (is_method == 1)):
			# in case of a new label, add new label - key in method dictionary
			label_ptrn = re.search(p13, lines[l])
			# change flag to show that we are in a new label - key -block
			is_new_level = 1
			# define the new label's name
			new_label_1 = label_ptrn.group()
			new_label_2 = re.sub("\:\n", "", new_label_1)
			new_label_3 = re.sub("[\s]+", " ", new_label_2)
			new_label_lst = re.split(" ", new_label_3)
			new_label = new_label_lst[1]
			# add the new label as key in the current method dictionary, initializing label's attributes first
			attributes = {}
			#attributes.setdefault("lines", [])
			attributes.setdefault("api_methods", [])
			attributes.setdefault("exceptions", [])
			m_dict.setdefault(new_label, attributes)
		# in case of new line in the current level
		if ((l + 1 < len(lines)) and (is_new_level == 1) and (is_method == 1)):
			# add values (lines) to the current label -key
			#attributes.setdefault("lines", []).append(lines[l])	
			# check if in the current line there exists an API method
			if (re.search(p11, lines[l])):
				api_m = isolate_api_method(lines[l])
				attributes.setdefault("api_methods", []).append(api_m)
			# check if in the next line exists a new label
			if (re.search(p13, lines[l + 1])):
				is_new_level = 0
		# in case of new line and throw in the current level
		if ((l + 2 < len(lines)) and (is_new_level == 1) and (is_method == 1)):
			# exception patterns according to a jimple file (see a jimple file for example)
			thr_exc = re.search(p6, lines[l]) and (re.search(p7, lines[l + 1]) or re.search(p7, lines[l + 2])) and (t_method == initial_method) and (t_method != "")
			if (thr_exc):
				pat1 = ""
				pat2 = ""
				pat3 = ""
				# check in which lines are the right specialinvoke and throw
				if (re.search(p9, lines[l])):
					pat1 = re.search(p9, lines[l]).group()
				if(re.search(p9, lines[l + 1])):
					pat2 = re.search(p9, lines[l + 1]).group()
				if(re.search(p9, lines[l + 2])):
					pat3 = re.search(p9, lines[l + 2]).group()
				if (pat1 == pat2) or (pat1 == pat3):
					t_exc = re.split("\<", lines[l])
					exc = re.split("\:" , t_exc[1])
					e_nm = keep_exc_name(exc[0])
					# exclude Throwable found from Soot
					if (e_nm != "Throwable"):
						# add values (lines) to the current label - key
						#attributes.setdefault("lines", []).append("exc."+e_nm)
						attributes.setdefault("exceptions", []).append(e_nm)
				# check for a new label in the next line
				if (re.search(p13, lines[l + 1])):
					# initialize variable for the next new label
					is_new_level = 0
		# in case of exceptions (catch clause in jimple file)
		catch_ptrn = re.search(p12, lines[l])
		if ((l + 1 < len(lines)) and (catch_ptrn) and (is_method == 1)):
			new_catch = catch_ptrn.group()
			# initialize dictionary for new_catch (as it was for a new label!)
			attributes = {}
			#attributes.setdefault("lines", [])
			attributes.setdefault("api_methods", [])
			attributes.setdefault("exceptions", [])
			m_dict.setdefault(new_catch, attributes)
			#attributes.setdefault("lines", []).append(lines[l])
			locate_labels_in_catch(lines[l], m_dict, attributes)
		# in case of a new method
		if (l + 2 < len(lines)) and not (re.search(p14, lines[l + 1])) and (is_method == 1) and (re.search(p1, lines[l + 1]) and re.search(p2, lines[l + 2])):
			#print m_dict
			# apply set operations on methods from the API and from the .apk files
			apply_set_operations(tmthd, m_dict, doc_dict, app_name, api_ver)
			is_method = 0
			is_new_level = 0
		# in case of lookupswitch
		if (l + 2 < len(lines)) and (re.search(p14, lines[l])):
			continue

# For keeping the same as in the following
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, android.util.AttributeSet)
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, AttributeSet)
# Also, if there is an arg from an embedded class, change $ to . 
# i.e. setOnItemSelectedListener(AdapterView.OnItemSelectedListener)
def update_md_args(method_sig):
	# list for the method signature args 
	method_sig_args = []
	# keep only the args of the method
	m_args = re.split("\(", method_sig)
	# split the method args to seek android or java case
	l_args = re.split(",", m_args[1])
	for l, k in enumerate(l_args):
		n_sp = re.sub(" ", "", l_args[l])
		if (re.search("java", n_sp) and not re.search("\$", n_sp)):
			s_args = re.split("\.", n_sp)
			last_elem = s_args[len(s_args) - 1]
			if (re.search("\)", last_elem)):
				last_part = re.sub("\)", '', last_elem)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(last_elem)
		elif (re.search("java", n_sp) and re.search("\$", n_sp)):
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

# search if there exists a label in the current method
def is_exist_label(lines):
	label = False
	for l, k in enumerate(lines):
		# there exists at least one label
		if ((l + 1 < len(lines)) and (re.search(p13, lines[l]))):
			label = True
			break
		# next new method
		if (l + 2 < len(lines)) and (re.search(p1, lines[l + 1]) and re.search(p2, lines[l + 2])):
			break
	return label

# find method calls to the Java API in each app method's body
def isolate_api_method(line):
	new_api_method = ""
	line_spl = re.split("\<", line)
	java_elems = re.split("\:", line_spl[1])
	java_cls = java_elems[0]
	if re.search(p1, java_elems[1]):
		method_elems = re.split("\>", re.search(p1, java_elems[1]).group())
		java_method = re.sub(" ", "", method_elems[0])
		java_mthd_cls = java_cls + "." + java_method
		new_api_method = update_md_args(java_mthd_cls)
		#print "\n*API method* ", new_api_method, "\n"
		return new_api_method

# keep only exception names (e.g. java.lang.IllegalArgumentException -> IllegalArgumentException)
# do not keep embedded exception (e.g. IntentSender$SendIntentException -> IntentSender.SendIntentException)
def keep_exc_name(exc):
	# for case java.lang.IllegalArgumentException
	if re.search("\.", exc):
		e_nm = re.split("\.", exc)
		l_elem = e_nm[len(e_nm) - 1]
		# for case IntentSender$SendIntentException
		if re.search("\$", l_elem):
			n_emb = re.split("\$", l_elem)
			#n_emb = re.sub("\$", ".", l_elem)
			return n_emb[1]
		else:
			return l_elem
	# for case IllegalArgumentException (there is not java.lang)
	else:
		return exc

# find labels, API methods, and exceptions and add them in catch's dictionary accordingly
def locate_labels_in_catch(line, m_dict, attributes):
	# list for the labels in catch (e.g. catch java.lang.Throwable from label1 to label2 with label3;)
	labels_lst = []
	# keys (labels) from dictionary
	m_dict_keys = m_dict.keys()
	# states for labels
	state = 0
	# last label to search for new exceptions
	last_label = ""
	# list of actual labels (in case for instance we have from label 2 to label 4 with label 2)
	actual_labels_lst = []

	# split catch
	catch_elem = re.split("[\s]+", line)
	# get the exception (referred in the catch clause -jimple file)
	exc = keep_exc_name(catch_elem[2])
	for c, e in enumerate(catch_elem):
		ptrn_l = re.search("label[0-9]+", catch_elem[c])
		# search for label in catch statement
		if (ptrn_l):
			ptrn = ptrn_l.group()
			labels_lst.append(ptrn)
	# search for the labels and their attributes in the current method's dictionary
	for k, l in enumerate(m_dict_keys):
		# "first " label in catch
		if (m_dict_keys[k] == labels_lst[0]) and (state == 0):
			state = 1
			actual_labels_lst.append(m_dict_keys[k])
			# get api methods from current label and add them in the catch dictionary
			api_mthds = get_label_api_methods(m_dict_keys[k], m_dict)
			for j, g in enumerate(api_mthds):
				attributes.setdefault("api_methods", []).append(api_mthds[j])
		# "next " label in catch
		elif (m_dict_keys[k] not in labels_lst) and (state == 1):
			actual_labels_lst.append(m_dict_keys[k])
			# get api methods from current label and add them in the catch dictionary
			api_mthds = get_label_api_methods(m_dict_keys[k], m_dict)
			for j, g in enumerate(api_mthds):
				attributes.setdefault("api_methods", []).append(api_mthds[j])
		# "second  " label in catch
		elif (m_dict_keys[k] == labels_lst[1]) and (state == 1):
			state = 2
			actual_labels_lst.append(m_dict_keys[k])
			# get api methods from current label and add them in the catch dictionary
			api_mthds = get_label_api_methods(m_dict_keys[k], m_dict)
			for j, g in enumerate(api_mthds):
				attributes.setdefault("api_methods", []).append(api_mthds[j])
		# "third " label in catch
		elif (m_dict_keys[k] == labels_lst[2]) and (state == 2):
			state = 0
			actual_labels_lst.append(m_dict_keys[k])
			exc = get_label_exception(labels_lst[2], m_dict, exc)
			# update exceptions of the current catch clause
			for j, g in enumerate(exc):
				attributes.setdefault("exceptions", []).append(exc[j])
		# "third " label in catch
		elif (labels_lst[2] in m_dict_keys) and (state == 2):
			state = 0
			actual_labels_lst.append(labels_lst[2])
			exc = get_label_exception(labels_lst[2], m_dict, exc)
			for j, g in enumerate(exc):
				attributes.setdefault("exceptions", []).append(exc[j])
			
# check if there is an exception in the current label
def get_label_exception(label, m_dict, e):
	exc = []
	exc.append(e)
	# get the exceptions of the third label
	attr = m_dict.get(label)
	label_exceptions = attr.get("exceptions")
	if (len(label_exceptions) > 0):
		for l, b in enumerate(label_exceptions):
			# add found exceptions in the list of catch exceptions
			exc.append(label_exceptions[l])
	return exc

# check if there is an API method in the current label
def get_label_api_methods(label, m_dict):
	api_methds = []
	# get the API methods from the current label
	attributes = m_dict.get(label)
	label_api_methods = attributes.get("api_methods")
	if (len(label_api_methods) > 0):
		api_methds = label_api_methods
	return api_methds

# optional method
# print possibly found API methods and exceptions from the current examined app method
def print_api_methods_and_exceptions(m_dict):
	m_dict_keys = m_dict.keys()
	for k, l in enumerate(m_dict_keys):
		# get the values for each label in the method
		attributes = m_dict.get(m_dict_keys[k])
		lb = attributes.get('api_methods')
		excp = attributes.get('exceptions')
		if (re.search("(catch).*", m_dict_keys[k])) and (len(lb) > 0): 
			#print m_dict_keys[k]
			#print "Label ", m_dict_keys[k]
			for d, b in enumerate(lb):
				print lb[d],":",','.join(excp)

# compare API methods and exceptions between app_dict and doc_dict
def apply_set_operations(tmthd, m_dict, doc_dict, app_name, api_ver):
	if (doc_dict.keys()):
		m_dict_keys = m_dict.keys()
		doc_dict_keys = doc_dict.keys()
		for k, l in enumerate(m_dict_keys):
			if (re.search("(catch).*", m_dict_keys[k])):
				attributes = m_dict.get(m_dict_keys[k])
				# get values from dictionary for catch label attributes
				api_mthd = attributes.get('api_methods')
				excp = attributes.get('exceptions')
				for m, n in enumerate(api_mthd):
					for d, c in enumerate(doc_dict_keys):
						if (api_mthd[m] == doc_dict_keys[d]):
							# exception set from app
							exc_set_app = set(excp)
							# exception set from doc
							dict = doc_dict.get(doc_dict_keys[d])
							at_ths = set(dict.get("@throws"))
							ths = set(dict.get("throws"))
							# common exceptions in the app and API
							exc_set_api = at_ths.union(ths)
							set_doc_list = list(exc_set_app.intersection(exc_set_api))
							if (len(set_doc_list) > 0):
								#print "app name: ", app_name, "api_mthd: ", api_mthd[m], "common exceptions found: ", exc_set_app.intersection(exc_set_api)
								fi.write(str(app_name + ":" + api_ver + ":" + tmthd + ":" + api_mthd[m] + ":" + ','.join(list(exc_set_app.intersection(exc_set_api))) + "\n"));
							# uncommon exceptions in the app and API
							set_undoc = exc_set_app.difference(exc_set_api)
							set_undoc_list = list(set_undoc)
							if ((len(set_undoc) > 0) and (set_undoc_list[0] != "Throwable") and (set_undoc_list[0] != "Exception")):
								# write -> app_name:api_version:app_method:called_API_method:exceptions
								fo.write(str(app_name + ":" + api_ver + ":" + tmthd + ":" + api_mthd[m] + ":" + ','.join(list(exc_set_app.difference(exc_set_api))) + "\n"));
								#print app_name,":",api_ver,":",tmthd,":",api_mthd[m],":",','.join(list(exc_set_app.difference(exc_set_api)))
	else:
		print "API version not available!" + api_ver
	#print tmthd, " ", app_name

# run main
if __name__ == "__main__":
	main()
