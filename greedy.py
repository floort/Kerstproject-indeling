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
OUT_FILE="/tmp/kerst/indeling.csv"


logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

if __name__ == "__main__":
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

	ll_fixed = {}
	ll_voting = {}
	ll_lazy = []

	logging.debug("Collecting all the votes.")
	data = csv.reader(stemmen_file)
	for row in data:
		if (row[12] != "0") or (row[13] != "0"):
			# vote is fixed.
			ll_fixed[int(row[1])] = [int(row[12]), int(row[13])]
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
		if w != -1:
			workshops[w][1] -= 1
			indeling[w][1].append(id)

	logging.debug("Inserting regular votes.")
	voters = ll_voting.keys()
	# Handle voters in a random order
	random.shuffle(voters)
	done = [] # All voters who don't need to goto the second round
	todo = [] # Could not have their desired workshops
	for id in voters:
		ok = 0
		for v in ll_voting[id]["want"]:
			if workshops[v][0] > 0:
				workshops[v][0] -= 1
				indeling[v][0].append(id)
				if len(workshops[v]) == 1:
					done.append(id) # no second round
				else:
					# remove vote for second round
					ll_voting[id]["want"] = filter(lambda c: c!=v, ll_voting[id]["want"])
				ok = 1
				break
		if not ok:
			todo.append(id)
	for id in todo:
		available = filter(lambda w: len(indeling[w][0])<workshops[w][0], workshops.keys())
		w = random.choice(available)
		workshops[w][0] -= 1
		indeling[w][0].append(id)
		if len(workshops[w]) == 1:
			done.append(id)

	logging.debug("Inserting regular voters (round 2)")
	done = set(done)
	todo = []
	# The last voter from first round can pick first
	voters.reverse()
	for id in voters:
		ok = 0
		# skip the voters who do a double round
		if id in done: continue
		
		for v in ll_voting[id]["want"]:
			if len(workshops[v]) == 1: continue
			if workshops[v][1] > 0:
				workshops[v][1] -= 1
				indeling[v][1].append(id)
				ok = 1
				break
		if not ok:
			todo.append(id)
	for id in todo:
		available = filter(
			lambda w: len(indeling[w][1])<workshops[w][1], 
			filter(
				lambda w: len(workshops[w]) > 1, 
				workshops.keys()
			)
		)
		w = random.choice(available)
		workshops[w][1] -= 1
		indeling[w][1].append(id)


	logging.debug("Inserting none-voters")
	for id in ll_lazy:
		for r in [0,1]:
			if r == 0:
				available = filter(lambda w: len(indeling[w][0])<workshops[w][0], workshops.keys())
			else:
				available = filter(
					lambda w: len(indeling[w][1])<workshops[w][1],
					filter(lambda w: len(workshops[w]) > 1, workshops.keys())
				)
			w = random.choice(available)
			workshops[w][r] -= 1
			indeling[w][r].append(id)

	# Restructure the data before writing
	out = {}
	for id in ll_voting.keys() + ll_fixed.keys() + ll_lazy:
		out[id] = [-1, -1]
	for w in indeling.keys():
		for r in xrange(len(indeling[w])):
			for id in indeling[w][r]:
				out[id][r] = w
	f = open(OUT_FILE, "w")
	for id in out.keys():
		f.write("%d, %d, %d\n"%(id, out[id][0], out[id][1]))
	f.close()



