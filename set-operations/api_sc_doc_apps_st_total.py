#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2017"
__license__= "Apache License, Version 2.0"
__email__= "mkechagiaATaueb.gr"

'''
This program compares pairs of API methods and exceptions
from the API source code (intra and inter procedural analysis)
with pairs of API methods and exceptions
from the API reference documentation, apps, and stack traces.

Input: .json file from Java APIs, stack traces, as well as undocumented exceptions from apps.

Output: report of the results from the application of set operations on API source code,
		documentation, apps, and stack traces.

Note: You can comment out operations that you don't want to run and
	  remove comments to print the resulted sets of API methods and operations.
'''

import re
import os
import sys
import json
# for removing elements from a list
import copy

from collections import defaultdict
from collections import OrderedDict
from sets import Set

# for API reference documentation (doc)
global doc_dict
doc_dict = OrderedDict([])

# for API source code (sc)
global sc_dict
sc_dict = OrderedDict([])

# for the crashes (st)
global st_dict
st_dict = OrderedDict([])

# for the applications (apps)
global apps_dict
apps_dict = OrderedDict([])

# for common API methods and exceptions in sc and doc
global sc_doc_dict
sc_doc_dict = OrderedDict([])

# for common API methods and exceptions in apps and doc
global apps_doc_dict 
apps_doc_dict = OrderedDict([])

# for common overloaded methods
global com_list
com_list = []

global analysis_type
analysis_type = ""

global checked_exc_list
checked_exc_list = ["AccountsException","AclNotFoundException","AndroidException","BackingStoreException","Base64DataException","BrokenBarrierException","CertificateException","CloneNotSupportedException","DataFormatException","DatatypeConfigurationException","DestroyFailedException","ErrnoException","ExecutionException","FileNotFoundException","FormatException","GeneralSecurityException","IOException","IntentFilter.MalformedMimeTypeException","IntentSender.SendIntentException","InterruptedException","InvalidPreferencesFormatException","JSONException","KeyChainException","LambdaConversionException","LastOwnerException","MediaCasException","MediaCryptoException","MediaDrmException","NetworkStats.NonMonotonicException","NoHttpResponseException","NotOwnerException","OperationApplicationException","ParseException","ParserConfigurationException","PrivilegedActionException","ReflectiveOperationException","SAXException","Settings.SettingNotFoundException","SQLException","SipException","SSLException","SSLHandshakeException","SSLPeerUnverifiedException","SurfaceTexture.OutOfResourcesException","TimeoutException","TooManyListenersException","TransformerException","URISyntaxException","UnsupportedCallbackException","XPathException","XmlPullParserException"]

global unchecked_exc_list
unchecked_exc_list = ["ActivityNotFoundException","AndroidRuntimeException","AnnotationTypeMismatchException","ArrayIndexOutOfBoundsException","ArithmeticException","ArrayStoreException","BadParcelableException","BufferOverflowException","BufferUnderflowException","ClassCastException","CompletionException","ConcurrentModificationException","CursorIndexOutOfBoundsException","DOMException","DateTimeException","EmptyStackException","EnumConstantNotPresentException","FileSystemAlreadyExistsException","FileSystemNotFoundException","FileUriExposedException","Fragment.InstantiationException","GLException","ICUUncheckedIOException","IllegalArgumentException","IllegalMonitorStateException","IllegalStateException","IncompleteAnnotationException","IndexOutOfBoundsException","InflateException","KeyCharacterMap.UnavailableException","LSException","MalformedParameterizedTypeException","MediaCodec.CryptoException","MissingResourceException","MustOverrideException","NegativeArraySizeException","NetworkOnMainThreadException","NoSuchElementException","NoSuchPropertyException","NullPointerException","OperationCanceledException","ParcelFormatException","ParseException","ProviderException","ProviderNotFoundException","RSRuntimeException","RejectedExecutionException","RemoteViews.ActionException","Resources.NotFoundException","RSDriverException","RSIllegalArgumentException","RSInvalidStateException","RuntimeException","SQLException","SQLiteUnfinalizedObjectsException","SQLiteDoneException","SQLiteException","SecurityException","StaleDataException","SuperNotCalledException","Surface.OutOfResourcesException","SurfaceHolder.BadSurfaceTypeException","TimeFormatException","TypeNotPresentException","UncheckedIOException","UndeclaredThrowableException","UnsupportedOperationException","ViewRootImpl.CalledFromWrongThreadException","WindowManager.BadTokenException","WindowManager.InvalidDisplayException","WrongMethodTypeException"]

global err_list
err_list = ["AnnotationFormatError","AssertionError","AssertionFailedError","CoderMalfunctionError","FactoryConfigurationError","IOError","LinkageError","ServiceConfigurationError","ThreadDeath","TransformerFactoryConfigurationError","VirtualMachineError","AbstractMethodError","AssertionFailedError","BootstrapMethodError","ClassCircularityError","ClassFormatError","ComparisonFailure","ExceptionInInitializerError","GenericSignatureFormatError","IllegalAccessError","IncompatibleClassChangeError","InstantiationError","InternalError","NoClassDefFoundError","NoSuchFieldError","NoSuchMethodError","OutOfMemoryError","StackOverflowError","UnknownError","UnsatisfiedLinkError","UnsupportedClassVersionError","VerifyError","ZipError"]

def main():
	# path for .json file for the API documetation (doc)
	path_doc2 = sys.argv[1]
	
	# path for .json file for the API source code (sc)
	path_sc2 = sys.argv[2]
	
	# path for .txt file for undoc exceptions in applications (apps)
	path_apps = sys.argv[3]

	# path for .txt file for the statck traces (st)
	path_st = sys.argv[4]

	# type of the analysis
	analysis_type = sys.argv[5] # android, java, 3rd-party library

	# for all API versions
	doc_dict = decode_json(path_doc2)
	print len(doc_dict.keys())
	sc_dict = decode_json(path_sc2)
	print len(sc_dict.keys())
	apps_dict = get_apps_dict_total(path_apps, analysis_type)
	st_dict = get_st_dict(path_st)

	# set operations
	sc_doc_dict = find_com_api_methd_sc_doc_total(doc_dict, sc_dict)
	calc_sc_undoc_exc(sc_doc_dict)
	apps_doc_dict = find_com_api_methd_apps_doc_total(doc_dict, apps_dict)
	find_com_api_methd_apps_doc_sc_total(doc_dict, apps_dict, sc_dict)
	find_com_api_methd_st_apps(apps_doc_dict, st_dict, apps_dict)
	find_com_api_methd_st_sc()
	find_com_api_methd_st_apps_sc_total(apps_doc_dict, sc_doc_dict, st_dict, apps_dict, sc_dict)

# decode json files into dictionary
def decode_json(f_json):
	try:
		with open(f_json) as f:
			return json.load(f)
	except ValueError:
		print ('Decoding JSON has been failed: ', f_json)

# find common API exceptions from source code and documentation (from all API versions)
def find_com_api_methd_sc_doc_total(doc_dict, sc_dict):
	common_api = []
	sc_doc_keys = sc_doc_dict.keys()
	# count methods with undocumented exceptions
	count = 0
	sc_keys = sc_dict.keys()
	doc_keys = doc_dict.keys()
	sc_api = Set(sc_dict.keys())
	doc_api = Set(doc_dict.keys())
	# common API methods in API reference and source code
	common_api = list(sc_api.intersection(doc_api))
	for k, l in enumerate(common_api):
		# API source code exceptions
		sc_exc = Set(sc_dict.get(common_api[k]))
		# API documentation exceptions
		doc_exc = Set(doc_dict.get(common_api[k]))
		t_exc = sc_exc.difference(doc_exc)
		# delete wrong exceptions
		l_t_exc = list(t_exc)
		list_orig = copy.deepcopy(l_t_exc)
		for c, d in enumerate(list_orig):
			if not (re.search("(Exception|Error)", list_orig[c])):
				l_t_exc.remove(list_orig[c])
		if (len(l_t_exc) > 0):
			# uncommon exceptions for source code and documentation
			#print "API method: ", common_api[k], " uncommon excep (sc Vs. doc): ", ','.join(l_t_exc)
			count = count + 1
			# update dictionary
			for i, r in enumerate(l_t_exc):
				# keep only method name; not the arguments to compare afterwards with the stack traces
				api_mthd = re.split("\(", common_api[k])
				if (api_mthd[0] in sc_doc_dict.keys()):
					# for overloaded methods
					com_list.append(api_mthd[0])
				# keep API method and undocumented exceptions	
				sc_doc_dict.setdefault(api_mthd[0], []).append(l_t_exc[i])

	print "No of common API methods in API documentation reference (API doc) and API source code (API sc): ", len(common_api)
	print "No of common API methods in API doc and API sc, but with undocumented exceptions: ", count, "\n"

	return sc_doc_dict

# calculate the number of the undocumented exceptions
# that can be found from the static analysis
# in the source code
def calc_sc_undoc_exc(sc_doc_dict):
	# total number of undocumented exceptions for a method
	count = 0
	# number of checked and undocumented exceptions
	count_checked = 0
	# number of unchecked and undocumented exceptions
	count_unchecked = 0

	l_keys = sc_doc_dict.keys()
	for k,l in enumerate(l_keys):
		l_exc = sc_doc_dict[l_keys[k]]
		count = count + len(l_exc)
		for m, n in enumerate(l_exc):
			# take care of the SQLException; it can be checked or unchecked
			if l_exc[m] in checked_exc_list:
				count_checked = count_checked + 1
			elif l_exc[m] in unchecked_exc_list:
				count_unchecked = count_unchecked + 1
			elif l_exc[m] in err_list:
				count_unchecked = count_unchecked + 1
			else:
				print "Exception from sc not checked neither unchecked: " + l_exc[m]
	
	print count # total undocumented exceptions found
	print count_checked
	print count_unchecked

# extract dictionary for stack traces
def get_st_dict(path):
	dict = {}
	# api exception
	a_exc = {}
	# root exception
	r_exc = {}
	method = ""
	frq = 0
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	for l, k in enumerate(lines):
		dict = {}
		ln = ""
		# split line to find the triplets
		if (re.search("\s+", lines[l])):
			ln = re.sub("\s+", "", lines[l])
		# split line to find the triplets
		line = re.split("\s", ln)
		elem = re.split(",", line[0])
		#android_method = re.split("\.", elem[1])
		# keep only method name
		#method = android_method[len(android_method) - 1]
		# frq -> the times an api method appears in crashes
		frq = elem[0]
		method = elem[1]
		# because method is equal to elem[1]
		api_exc = keep_exc_name(elem[2])
		root_exc = keep_exc_name(elem[3])
		if (method not in st_dict.keys()):
			st_dict.setdefault(method, dict)
			a_exc = dict.setdefault("a_exc", []).append(api_exc)
			r_exc = dict.setdefault("r_exc", []).append(root_exc)
			f_mtd = dict.setdefault("f_mtd", []).append(frq)
		else:
			dict = st_dict.get(method)
			a_exc = dict.get("a_exc")
			if (api_exc not in a_exc):
				a_exc = dict.setdefault("a_exc", []).append(api_exc)
			r_exc = dict.get("r_exc")
			if (root_exc not in r_exc):
				r_exc = dict.setdefault("r_exc", []).append(root_exc)
	return st_dict

# find common API methods and exceptions between sc, doc, and st
def find_com_api_methd_st_sc(): 
	count = 0
	st_api = Set(st_dict.keys())
	sc_doc_api = Set(sc_doc_dict.keys())
	# TO take care of the arguments, uncomment!
	#common_api_1 = Set(com_list)
	#common_api = list(common_api_1.intersection(st_api))
	# common API methods in API doc, sc, st
	common_api = list(sc_doc_api.intersection(st_api))
	for k, l in enumerate(common_api):
		# exceptions from the stack traces
		st_exc = st_dict.get(common_api[k])
		api_exc = Set(st_exc.get("a_exc"))
		root_exc = Set(st_exc.get("r_exc"))
		t_st_exc = api_exc.union(root_exc)
		# API sc, doc exceptions
		sc_doc_exc = Set(sc_doc_dict.get(common_api[k]))
		# common exceptions between stack traces and API source code
		t_exc = sc_doc_exc.intersection(t_st_exc)
		if (len(t_exc) > 0):
			#print ("API method: ", common_api[k], " common excep in sc and st: ", ','.join(list(t_exc)))
			count = count + 1
	
	print "No of common API methods in stack traces (st), API source code (API sc), and API documentation reference (API doc): ", len(common_api)
	print "No of common API methods in st, API sc, but with undocumented exceptions: ", count, "\n"

	return sc_doc_dict

# find common API methods and exceptions between apps and stack traces (apps and st)
def find_com_api_methd_st_apps(apps_doc_dict, st_dict, apps_dict):
	count = 0
	st_api = Set(st_dict.keys())
	apps_doc_api = Set(apps_doc_dict.keys())
	# TO take care of the arguments, uncomment!
	#common_api_1 = Set(com_list)
	common_api = list(st_api.intersection(apps_doc_api))
	# common API methods in API doc, sc, st
	#common_api = list(apps_doc_api.intersection(st_api))
	for k, l in enumerate(common_api):
		# exceptions from the stack traces
		st_exc = st_dict.get(common_api[k])
		api_exc = Set(st_exc.get("a_exc"))
		root_exc = Set(st_exc.get("r_exc"))
		t_st_exc = api_exc.union(root_exc)
		# API sc, doc exceptions
		apps_doc_exc = Set(apps_doc_dict.get(common_api[k]))
		# common exceptions between stack traces and API source code
		t_exc = apps_doc_exc.intersection(t_st_exc)
		if (len(t_exc) > 0):
			#print ("API method: ", common_api[k], " common excep in apps and st (not in doc): ", ','.join(list(t_exc)))
			count = count + 1

	print "No of common API methods in stack traces (st) and apps: ", len(common_api)
	print "No of common pairs of API methods and undocumented exceptions in st and apps: ", count, "\n"

# find common API methods and exceptions between apps, source code, and stack traces
def find_com_api_methd_st_apps_sc_total(apps_doc_dict, sc_doc_dict, st_dict, apps_dict, sc_dict):
	#print (sc_doc_dict)
	count = 0
	st_api = Set(st_dict.keys())
	apps_doc_api = Set(apps_doc_dict.keys())
	sc_doc_api = Set(sc_doc_dict.keys())
	# TO take care of the arguments, uncomment!
	#common_api_1 = Set(com_list)
	common_api1 = st_api.intersection(apps_doc_api)
	common_api = list(common_api1.intersection(sc_doc_api))
	# common API methods in API doc, sc, st
	#common_api = list(apps_doc_api.intersection(st_api))
	for k, l in enumerate(common_api):
		# exceptions from the stack traces
		st_exc = st_dict.get(common_api[k])
		api_exc = Set(st_exc.get("a_exc"))
		root_exc = Set(st_exc.get("r_exc"))
		frq = st_exc.get("f_mtd")
		t_st_exc = api_exc.union(root_exc)
		# API sc, doc exceptions
		apps_doc_exc = Set(apps_doc_dict.get(common_api[k]))
		sc_doc_exc = Set(sc_doc_dict.get(common_api[k]))
		# common exceptions between stack traces and API source code
		t_exc1 = apps_doc_exc.intersection(t_st_exc)
		t_exc = t_exc1.intersection(sc_doc_exc)
		l_t_exc = list(t_exc)
		if (len(l_t_exc) > 0):
			#dict = apps_dict.get(common_api[k])
			#for m, n in enumerate(l_t_exc):
				#frq = dict.get(l_t_exc[m])
				#print "API method: ", common_api[k], " common excep in apps, sc, st (not in doc): ", l_t_exc[m], " frq: ", int(frq)
			#print ("API method: ", common_api[k], " common excep in apps, sc, st (not in doc): ", ','.join(l_t_exc), " : ", frq)
			count = count + 1
	
	print "No of common API methods in stack traces (st), apps, API source code (sc), and API documentation reference (API doc): ", len(common_api)
	print "No of common pairs of API methods and undocumented exceptions (in st, apps, sc, but not in doc) : ", count, "\n"

# keep only exception names (e.g. java.lang.IllegalArgumentException -> IllegalArgumentException)
# do not keep embedded exception (e.g. IntentSender$SendIntentException -> IntentSender.SendIntentException)
def keep_exc_name(exc):
	excp = ""
	# for case java.lang.IllegalArgumentException
	if re.search("\.", exc):
		e_nm = re.split("\.", exc)
		l_elem = e_nm[len(e_nm) - 1]
		# for case IntentSender$SendIntentException
		if re.search("\$", l_elem):
			n_emb = re.split("\$", l_elem)
			#n_emb = re.sub("\$", ".", l_elem)
			excp = n_emb[1]
		else:
			excp = l_elem
	# for case IllegalArgumentException (there is not java.lang)
	else:
		if re.search("(Exception|Error)", exc):
			excp = exc
		else:
			excp = ""
	return excp

# extract dictionary for apps and correct duplicates
def get_apps_dict_total(path, analysis_type):
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	for l, k in enumerate(lines):
		# split line to find the api methods and exceptions
		#line = re.split("[0-9]+\s+", lines[l])
		if (re.search("\s+"+analysis_type+"\.", lines[l])):
			line = re.split("\s+"+analysis_type+"\.", lines[l])
			elem = re.split(":", line[1])
			# frequency that a pair of API method and exception appears in apps
			frq = line[0]
			# clean api methods and add to dict
			api_m_1 = re.sub("\)\s*", ")", elem[0])
			api_m = analysis_type+"."+api_m_1
			if (api_m not in apps_dict.keys()):
				dict = {}
				apps_dict.setdefault(api_m, dict)
			# clean exceptions
			if (len(elem) > 1):
				exc = re.sub("\n\s*", "", elem[1])
				exc_s = re.sub("\s*", "", exc)
				# keep only valid exception types
				if (re.search(",", exc_s)):
					exc_l = re.split(",", exc_s)
					# delete wrong exceptions
					list_orig = copy.deepcopy(exc_l)
					for c, d in enumerate(list_orig):
						if not (re.search("(Exception|Error)$", list_orig[c])):
							exc_l.remove(list_orig[c])
					# update apps_dict
					if (len(exc_l) > 0):
						for e, f in enumerate(exc_l):
							dict = apps_dict.get(api_m)
							if (exc_l[e] not in dict.keys()):
								dict[exc_l[e]] = int(frq)
							else:
								current_f = dict.get(exc_l[e])
								dict[exc_l[e]] = int(current_f) + int(frq)
				else:
					if (re.search("(Exception|Error)", exc_s)):
						dict = apps_dict.get(api_m)
						if (exc_s not in dict.keys()):
							dict[exc_s] = int(frq)
						else:
							current_f = dict.get(exc_s)
							dict[exc_s] = int(current_f) + int(frq)
	return apps_dict

# compare pairs of API methods and exceptions from documentation and apps analysis (total API versions)
def find_com_api_methd_apps_doc_total(doc_dict, apps_dict):
	counter = 0
	common_c = 0
	apps_api = Set(apps_dict.keys())
	doc_api = Set(doc_dict.keys())
	# common API methods in API reference and apps
	common_api = list(apps_api.intersection(doc_api))
	#print len(apps_api) -> 2550
	#print len(doc_api) -> 84421
	#print len(common_api) -> 2549
	for k, l in enumerate(common_api):
		# keep only method name; not the arguments to compare with the stack traces
		api_mthd = re.split("\(", common_api[k])
		if (api_mthd[0] not in apps_doc_dict.keys()):
			apps_doc_dict.setdefault(api_mthd[0], [])
		# API documentation exceptions
		doc_exc = Set(doc_dict.get(common_api[k]))
		# apps exceptions
		apps_exc = apps_dict.get(common_api[k])
		# apps_exc is a dictionary: keys are exception types; values are the frequencies
		t_apps_exc = Set(apps_exc.keys())
		# exceptions that exist in apps NOT in doc (total API versions)
		t_exc = t_apps_exc.difference(doc_exc)
		if (len(t_exc) > 0):
			counter = counter + 1
			# get frequencies for each pair of api method - exception
			l_t_exc = list(t_exc)
			for m, n in enumerate(l_t_exc):
				frq = apps_exc.get(l_t_exc[m])
				#print frq, ":" , common_api[k], " : ", l_t_exc[m]
				apps_doc_dict.get(api_mthd[0], []).append(l_t_exc[m])
				#print l_t_exc[m]
				#print frq, ":" , common_api[k]
		# exceptions that exist in apps and in doc (total API versions)
		t_exc_1 = t_apps_exc.intersection(doc_exc)
		l_t_exc1 = list(t_exc_1)
		if (len(l_t_exc1) > 0):
			for m, n in enumerate(l_t_exc1):
				frq = apps_exc.get(l_t_exc1[m])
				#print frq, ":" , common_api[k], ":", l_t_exc1[m]
				#print frq, ":" , common_api[k]
			common_c = common_c + 1
			#print common_api[k], ":", ",".join(list(t_exc_1))

	print "No of common API methods in API documentation reference (API doc) and apps: ", len(common_api)
	print "No of common API methods in API doc and apps, but with undocumented exceptions: ", counter, "\n"
	#print "No of common pairs of API methods and exceptions in API doc and apps: ", common_c

	return apps_doc_dict

# compare pairs of api methods and exceptions from documentation, apps, and API source code analysis
def find_com_api_methd_apps_doc_sc_total(doc_dict, apps_dict, sc_dict):
	counter = 0
	c = 0
	counter_api_m_sc_doc_apps = 0
	apps_api = Set(apps_dict.keys())
	doc_api = Set(doc_dict.keys())
	sc_api_keys = sc_dict.keys()
	sc_api = Set(sc_dict.keys())
	# common API methods in API reference and apps
	common_api = list(apps_api.intersection(doc_api))
	for k, l in enumerate(common_api):
		if (common_api[k] in sc_api_keys):
			counter_api_m_sc_doc_apps = counter_api_m_sc_doc_apps + 1
			# API documentation exceptions
			doc_exc = doc_dict.get(common_api[k])
			#at_throws = Set(doc_exc.get('@throws'))
			#sig_throws = Set(doc_exc.get('throws'))
			#t_doc_exc = at_throws.union(sig_throws)
			# apps exceptions
			apps_exc = apps_dict.get(common_api[k])
			t_apps_exc = Set(apps_exc.keys())
			# exceptions that exist in apps but not in doc
			t_exc = t_apps_exc.difference(doc_exc)
			if (len(t_exc) > 0):
				counter = counter + 1
			# common exceptions in apps and doc
			t_exc_1 = t_apps_exc.intersection(doc_exc)
			#if (len(t_exc_1) > 0):
				#print common_api[k], " ", t_exc_1
			# API source code exceptions
			sc_exc = Set(sc_dict.get(common_api[k]))
			#intra = Set(sc_exc.get('intra_proced'))
			#inter = Set(sc_exc.get('inter_proced'))
			#t_sc_exc = intra.union(inter)
			# exceptions in apps and sc but not in doc
			#sc_apps = t_exc.intersection(t_sc_exc)
			sc_apps = t_exc.intersection(sc_exc)
			#if (len(sc_apps) > 0):
			#	c = c + 1
				#print (common_api[k], " ", sc_apps)
			# exceptions in apps and sc but not in doc
			#sc_apps = t_exc.intersection(t_sc_exc)
			l_sc_apps = list(sc_apps)
			if (len(l_sc_apps) > 0):
				dict = apps_dict.get(common_api[k])
				for m, n in enumerate(l_sc_apps):
					frq = dict.get(l_sc_apps[m])
					print "API method: ", common_api[k], " common excep in apps, sc (not in doc): ", l_sc_apps[m], " frq: ", int(frq)
				c = c + 1
				#print common_api[k], " ", sc_apps

	print "No of common API methods in API source code (API sc), API reference documentation (API doc), and apps: ", counter_api_m_sc_doc_apps
	print "No of common API methods in apps, API sc, API doc with undocumented exceptions (in apps and API sc, but not in API doc): ", c, "\n"

# compare pairs of api methods and exceptions from documentation, apps, and API source code analysis
def find_com_api_methd_apps_doc_sc(doc_dict, apps_dict, sc_dict):
	counter = 0
	c = 0
	counter_api_m_sc_doc_apps = 0
	apps_api = Set(apps_dict.keys())
	doc_api = Set(doc_dict.keys())
	sc_api_keys = sc_dict.keys()
	sc_api = Set(sc_dict.keys())
	# common API methods in API reference and apps
	common_api = list(apps_api.intersection(doc_api))
	for k, l in enumerate(common_api):
		if (common_api[k] in sc_api_keys):
			counter_api_m_sc_doc_apps = counter_api_m_sc_doc_apps + 1
			# API documentation exceptions
			doc_exc = doc_dict.get(common_api[k])
			at_throws = Set(doc_exc.get('@throws'))
			sig_throws = Set(doc_exc.get('throws'))
			t_doc_exc = at_throws.union(sig_throws)
			# apps exceptions
			apps_exc = Set(apps_dict.get(common_api[k]))
			# exceptions that exist in apps but not in doc
			t_exc = apps_exc.difference(t_doc_exc)
			if (len(t_exc) > 0):
				counter = counter + 1
			# common exceptions in apps and doc
			t_exc_1 = apps_exc.intersection(t_doc_exc)
			#if (len(t_exc_1) > 0):
				#print common_api[k], " ", t_exc_1
			# API source code exceptions
			sc_exc = sc_dict.get(common_api[k])
			intra = Set(sc_exc.get('intra_proced'))
			inter = Set(sc_exc.get('inter_proced'))
			t_sc_exc = intra.union(inter)
			# exceptions in apps and sc but not in doc
			sc_apps = t_exc.intersection(t_sc_exc)
			l_sc_apps = list(sc_apps)
			if (len(l_sc_apps) > 0):
				dict = apps_dict.get(common_api[k])
				for m, n in enumerate(l_sc_apps):
					frq = dict.get(l_sc_apps[m])
					print "API method: ", common_api[k], " common excep in apps, sc (not in doc): ", l_sc_apps[m], " frq: ", int(frq)
				c = c + 1
				#print common_api[k], " ", sc_apps
	print "No of common apis in doc and apps: ", len(common_api)
	print "No of api methods with undocumented exceptions in apps (doc Vs. apps): ", counter
	print "Common apis in sc, doc, apps: ", counter_api_m_sc_doc_apps
	print "Methods with common exc in apps, sc, not in doc: ", c

# run main
if __name__ == "__main__":
	main()