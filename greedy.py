#!/usr/bin/env python

import sys
import csv
from munkres import Munkres
import os.path
import random
import logging
import pprint
import pickle


DATA_DIR="/tmp/kerst"
LOG_FILE="/tmp/kerst-log"


logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

if __name__ == "__main__":
	if not os.path.exists(os.path.join(DATA_DIR, "leerlingen.csv")):
		sys.exit(1)
	try:
		stemmen_file = open(os.path.join(DATA_DIR, "stemmen.csv"))
	except:
		logging.error("Could not open file: %s" %(os.path.join(DATA_DIR, "stemmen.csv")))
		sys.exit(1)
	try:
		workshops_file = open(os.path.join(DATA_DIR, "workshops.csv"))
	except:
		logging.error("Could not open file: %s" %(os.path.join(DATA_DIR, "workshops.csv")))
		sys.exit(1)
	try:
		leerlingen_file = open(os.path.join(DATA_DIR, "leerlingen.csv"))
	except:
		logging.error("Could not open file: %s" %(os.path.join(DATA_DIR, "leerlingen.csv")))
		sys.exit(1)

	ll_fixed = {}
	ll_voting = {}
	ll_lazy = []

	logging.debug("Collecting all the votes.")
	data = csv.reader(stemmen_file)
	for row in data:
		if (row[12] == "0") or (row[13] == "0"):
			# vote is fixed.
			ll_fixed[int(row[1])] = [int(12), int(13)]
		elif row[2] != "0":
			# User has voted
			ll_voting[int(row[1])] = {
				"want": map(lambda i: int(i), row[2:7]),
				"dont": map(lambda i: int(i), row[7:12])
			}
		else:
			# User is lazy and hasn't voted
			ll_lazy.append(int(row[1]))

	logging.debug("Load all the workshops.")
	# There are 2 rounds for the workshops
	data = csv.reader(workshops_file)
	workshops = {}
	indeling = {}
	for w in data:
		if w[2] == "2": # two rounds
			workshops[int(w[0])] = [int(w[1]), int(w[1])]
			indeling[int(w[0])] = [[], []]
		else: # one round
			workshops[int(w[0])] = [int(w[1]), ]
			indeling[int(w[0])] = [[], ]


	logging.debug("Inserting all fixed votes.")
	for id in ll_fixed.keys():
		w = ll_fixed[id][0]
		workshops[w][0] -= 1
		indeling[w][0].append(id)
		w = ll_fixed[id][1]
		if w:
			workshops[w][1] -= 1
			indeling[w][1].append(id)

	



