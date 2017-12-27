#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2017"
__license__= "Apache License, Version 2.0"
__email__= "mkechagiaATaueb.gr"

'''
This program parses jimple files (produced by Soot) 
from a Java API (e.g. Android, Java API, and 3rd-party Java libraries)
and constructs a graph of methods (nodes)
and exceptions (attributes)
that the methods can throw. 
From the method calls (edges)
one can find all the possible exceptions (throw new) that a method can throw,
given a specific depth (3) for the graph nodes.

Input:
The folder with jimple files (Soot output) of an analyzed app and
the version of the API.
Caution! Soot analyzes the API used by the app.
So, we need to analyze only ONE app of version X,
for the analysis of an API of version X.
Then, we run the following script as many times as the number of the different API versions.

Output:
For each API version, .json file (e.g. androi-#_source.json, java-#_source.json)
stored in the JSON folder (eRec/api/JSON).
For your convenience, there are already these files in the JSON folder of the eRec-data.
'''

# libraries for the graphs check https://networkx.github.io/documentation/stable/release/release_dev.html
import pydot
import networkx as nx
import matplotlib.pyplot as plt
# import library for regex
import re
# import library for os walking
import os
import json
import sys

from collections import defaultdict
from collections import OrderedDict
#from odict import OrderedDict
from sets import Set

# graph for methods and exceptions
G=nx.Graph()
# directed graph for the edges
DG=nx.DiGraph(G)
# dictionary for successive nodes
global g_dict
g_dict = {}
# dictionary for methods and exceptions (in method body -intra procedurally and propagated -inter procedurally)
global method_exceptions
method_exceptions = {}
# dictionary for methods and exceptions from the use of the doclet (documentation-doc)
global doc_dict
doc_dict = OrderedDict([])

# android or java
global analysis_type
analysis_type = ""

# patterns for finding method signatures and constructors
p1 = "\s[a-z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws)*.*$"
p2 = "[\s]*\{[\s]*$"
p3 = "\<[c]*[l]*init\>\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p4 = "catch\s"
p6 = "(specialinvoke|staticinvoke|virtualinvoke)\s"
p7 = "throw\s"
p8 = "[a-z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p9 = "\$r[0-9]+"
p10 = "[a-z]+[a-zA-Z0-9\$]*\(.*\)"

# main method
def main():
	path = sys.argv[1] # folder where the app belongs to
	path2 = sys.argv[2] # API version
	analysis_type = sys.argv[3]
	read_folder(path, analysis_type)
	get_propagated_exceptions()
	#print(G.nodes(data=True))
	#print DG.edges()
	print "no of examined methods: ", method_exceptions
	add_dict_to_JSON(analysis_type+"-"+path2, doc_dict)

	print len(method_exceptions)

	method_keys = method_exceptions.keys()
	count_except = 0
	for k, l in enumerate(method_keys):
		attributes = method_exceptions.get(method_keys[k])
		intra = attributes.get('intra_proced')
		inter = attributes.get('inter_proced')
		if (((intra) and (len(intra) > 0)) or ((inter) and (len(inter) > 0))):
			count_except = count_except + 1
	print "no of methods with exceptions: ", count_except

# open and read the files in the read_folder
# get only jimple files
def read_folder(path, analysis_type):
	for subdir, dirs, files in os.walk(path):
		for file in files:
			# search only for files that end with .jimple and come from the API
			e = re.search(analysis_type+"\..*\.jimple$", file)
			if e:
				f = subdir + "/" + file
				parse_jimple(f, analysis_type)

# parse current jimple file
def parse_jimple(file, analysis_type):
	method_s = ""
	cl_m = ""
	initial_method = ""
	upd_method = ""
	t_method = ""

	# keep the file (class-not embedded) that current methods belongs to
	file_class = re.search(analysis_type+"\..*\.jimple$", file).group()
	fl_class = re.sub(".jimple", "", file_class)
	if (re.search("\$", fl_class)):
		cl_m = re.sub("\$.*.$", "", fl_class)
	else:
		cl_m = fl_class

	f = open(file)
	lines = f.readlines()
	for l, k in enumerate(lines):
		if (l + 1 < len(lines)):
			# in case of new method signature
			if re.search(p1, lines[l]) and re.search(p2, lines[l + 1]):
				method_sig = re.search(p1, lines[l]).group()
				method_s = re.search(p8, method_sig).group()
				method_nm = re.split("\(", method_s)
				upd_method = update_md_args(method_s, analysis_type)
				t_method = cl_m + "." + upd_method
				initial_method = t_method
				if (t_method not in G.nodes()):
					G.add_node(t_method)
					#G.node[t_method].setdefault('throws', [])
					G.node[t_method].setdefault('throw new', [])
					print "node:", t_method
			# in case of new constructor?
			if re.search(p3, lines[l]) and re.search(p2, lines[l + 1]):
				initial_method = ""
		# exception in throw new (in method body)
		if (l + 2 < len(lines)):
			if re.search(p6, lines[l]) and (re.search(p7, lines[l + 1]) or re.search(p7, lines[l + 2])) and (t_method == initial_method) and (t_method != ""):
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
						#print t_method, " ", e_nm
						G.node[t_method].setdefault('throw new', []).append(e_nm)
		# in case of a method call in the current method
		if re.search(p6, lines[l]) and (t_method == initial_method):
			jmp_1 = re.split("\<", lines[l])
			jmp_2 = re.split("\>", jmp_1[1])
			m_jmp = jmp_2[0]
			n_m_jmp = re.sub('\$', '.', m_jmp)
			if re.search(":", n_m_jmp):
				l_n_m_jmp = re.split("\:", str(n_m_jmp))
				if re.search(p10, n_m_jmp):
					called_method_sig = (re.search(p10, n_m_jmp)).group()
					mthd = l_n_m_jmp[0],".",called_method_sig
					n_mthd = ''.join(mthd)
					#print "called method", n_mthd
					# new node for the called method signature
					called_method = update_md_args(n_mthd, analysis_type)
					if (called_method not in G.nodes()):
						G.add_node(called_method)
						#G.node[called_method].setdefault('throws', [])
						G.node[called_method].setdefault('throw new', [])
					# new directed edge from the current method to the called method
					DG.add_edge(t_method, called_method)
					#print "directed graph ",t_method," ",called_method

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
	# split the method args to seek android or java case
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

# get the successors of each node and their exceptions (throw new)
def get_propagated_exceptions():
	state = 0
	g_dict = {}
	list_success_exc = []
	successors = []
	for nd in DG:
		g_dict = {}
		list_success_exc = []
		# get exceptions from the node itself -depth 0
		if nd in G.nodes():
			# add method in dictionary
			attributes = {}
			method_exceptions.setdefault(nd, attributes)
			attributes.setdefault("intra_proced", [])
			attributes.setdefault("inter_proced", [])
			exc_lst = G.node[nd].get('throw new')
			for n, t in enumerate(exc_lst):
				#list_success_exc.append(exc_lst[n])
				attributes.setdefault("intra_proced", []).append(exc_lst[n])
			# dictionary for node's successors
			g_dict = dict(nx.bfs_successors(DG, nd))
			# dictionary keys as successors
			g_keys = g_dict.keys()
			successors = []
			# check level and exceptions of each successor
			for k, l in enumerate(g_keys):
				if (DG.has_edge(nd, g_keys[k])):
					state = 1
					# get list of exceptions from the current successor
					exc_lst = G.node[g_keys[k]].get('throw new')
					for e, x in enumerate(exc_lst):
						#list_success_exc.append(exc_lst[e])
						attributes.setdefault("inter_proced", []).append(exc_lst[e])
					# get the successors of the key k
					successors = g_dict.get(g_keys[k])
					if (len(successors) > 0):
						for s, c in enumerate(successors):
							state = 2
							# get list of exceptions from successors
							exc_lst = G.node[successors[s]].get('throw new')
							for p, a in enumerate(exc_lst):
								#list_success_exc.append(exc_lst[p])
								attributes.setdefault("inter_proced", []).append(exc_lst[p])
							# get the successors of the the successors of key k
							successors_2 = g_dict.get(successors[s])
							if ((successors_2 is not None) and (len(successors_2) > 0)):
								for r, t in enumerate(successors_2):
									state = 3
									# get list of exceptions from successors
									exc_lst = G.node[successors_2[r]].get('throw new')
									for e, x in enumerate(exc_lst):
										#list_success_exc.append(exc_lst[e])
										attributes.setdefault("inter_proced", []).append(exc_lst[e])

# store dictionary in JSON file for permanent use
def add_dict_to_JSON(api_version, doc_dict):
	file_name = api_version+'_source.json'
	with open(file_name, 'w') as fp:
		json.dump(method_exceptions, fp, indent = 4)

# run main
if __name__ == "__main__":
	main()
