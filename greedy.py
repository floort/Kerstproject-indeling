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

	logging.debug("Load all the worshops.")
	# There are 2 rounds for the workshops
	data = csv.reader(workshops_file)
	places = [[],[]]
	workshops = {}
	for w in data:
		workshops[int(w[0])] = {
			"name": w[1],
			"plaatsen": int(w[2]),
			"rondes": int(w[3]),
			"open": int(w[4]),
			"indeling": [[] for i in range(int(w[3]))]
		}
		if int(w[4]) == 1: # Workshop is open
			places[0] += [int(w[0])] * int(w[2])
			if int(w[3]) == 2: # Workshop has 2 rounds
				places[1] += [int(w[0])] * int(w[2])
	logging.debug("Places: %d %d" % (len(places[0]), len(places[1])))

	logging.debug("Get all the students.")
	# All students
	data = csv.reader(leerlingen_file)
	students = {}
	no_second_round = set()
	for s in data:
		students[int(s[0])] = {
			"klas": s[1],
			"naam": s[2],
			"tussenvoegsel": s[3],
			"achternaam": s[4],
			"mentor": s[5]
		}




