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

def cost_matrix(votes, places):
	# Lower cost is better
	cost = [[0 for i in xrange(len(places))] for j in xrange(len(votes))]
	for person in xrange(len(votes)):
		# Give points for the preferred workshops
		for rank in xrange(len(votes[person]["want"])): # wants rank=0 most
			for p in xrange(len(places)):
				if places[p] == votes[person]["want"][rank]:
					cost[person][p] = rank-5
		# Give the "dont" workshops an high cost
		for d in xrange(len(votes[person]["dont"])):
			for p in xrange(len(places)):
				if places[p] == votes[person]["dont"][d]:
					cost[person][p] = 5 # high cost
	return cost
	


if __name__ == "__main__":
	if not os.path.exists(os.path.join(DATA_DIR, "leerlingen.csv")):
		sys.exit(1)
	try:
		stemmen_file = open(os.path.join(DATA_DIR, "stemmen.csv"))
	except:
		logging.error("Could not open file: %s" %(os.path.join(DATA_DIR, "stemmen.csv")))
		sys.exit(1)
	try:
		workshops_file = open(os.path.join(DAT_DIR, "stemmen.csv"))
	except:
		logging.error("Could not open file: %s" %(os.path.join(DATA_DIR, "stemmen.csv")))
		sys.exit(1)
	try:
		leerlingen_file = open(os.path.join(DATA_DIR, "leerlingen.csv"))
	except:
		logging.error("Could not open file: %s" %(os.path.join(DATA_DIR, "leerlingen.csv")))
		sys.exit(1)

	logging.debug("Collecting all the votes.")
	data = csv.reader(stemmen_file)
	# Collect all the votes
	votes = []
	for row in data:
		votes.append({
			"name": row[1],
			"want": map(lambda i: int(i), row[2:7]),
			"dont": map(lambda i: int(i), row[7:12])
		})

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


	logging.debug("Generating cost matrix.")
	cost = cost_matrix(votes, places[0])
	
	logging.debug("Execute munkres algorithm.")
	# Now solve the first round
	m = Munkres()
	indices = m.compute(cost)
	

	logging.debug("Utilizing results")
	students_with_vote = set([a for a, b in indices])
	students_without_vote = set(students.keys()) - students_with_vote
	# Put students without vote in random place

	for person, place in indices:
		for i in xrange(len(votes[person]["want"])):
			if votes[person]["want"][i] == places[0][place]:
				del(votes[person]["want"][i])
				break
		#print votes[person]["name"], "\t->\t", places[0][place]
		workshops[places[0][place]]["indeling"][0].append(votes[person]["name"])
		if workshops[places[0][place]]["rondes"] != 2:
			no_second_round.add(votes[person]["name"])
	

	logging.debug("Computing second round.")
	for n in no_second_round:
		for i in xrange(len(votes)):
			if votes[i]["name"] == n:
				del(votes[i])
				break
	cost = cost_matrix(votes, places[1])
	indices = m.compute(cost)

	for person, place in indices:
		workshops[places[1][place]]["indeling"][1].append(votes[person]["name"])

	f = open("second_round.pickle", "wb")
	pickle.dump(workshops, f)
	f.close()



# There is a bug in this code somewhere..
	logging.debug("Lazy students...")
	# Put all student who did not vote in random groups
	available = []
	lazy = {}
	for w in workshops.keys():
		if workshops[w]["open"]:
			if workshops[w]["plaatsen"] > len(workshops[w]["indeling"][0]):
				available.append(w)
	for s in students_without_vote:
		if not available:
			logging.error("Not enough room")
			break
		w = random.choice(available)
		workshops[w]["indeling"][0].append(s)
		if workshops[w]["rondes"] != 2:
			no_second_round.add(s)
		lazy[s] = w
		if workshops[w]["plaatsen"] <= len(workshops[w]["indeling"][0]):
			for i in xrange(len(available)):
				if available[i] == w:
					del(available[i])
					break
	f = open("first_lazy.pickle", "wb")
	pickle.dump(workshops,f)
	f.close()

	available = []
	for w in workshops.keys():
		if workshops[w]["open"] and (workshops[w]["rondes"] == 2):
			if workshops[w]["plaatsen"] > len(workshops[w]["indeling"][1]):
				available.append(w)
	for s in students_without_vote - no_second_round:
		w = random.choice(list(set(available) - set([lazy[s]])))
		workshops[w]["indeling"][1].append(s)
		if workshops[w]["plaatsen"] <= len(workshops[w]["indeling"][1]):
			for i in xrange(len(available)):
				if available[i] == w:
					del(available[i])
					break

# end of bug area

	out = {}
	for w in workshops.keys():
		for l in workshops[w]["indeling"][0]:
			out[int(l)] = [w]
	for w in workshops.keys():
		if workshops[w]["rondes"] == 2:
			for l in workshops[w]["indeling"][1]:
				out[int(l)].append(w)
		
	f = open("out.csv", "w")
	for l in out.keys():
		if len(out[l]) == 2:
			f.write("%d,%d,%d\n" % (l, out[l][0], out[l][1]))
		else:
			f.write("%d,%d,\n" % (l, out[l][0]))

	f.close()
	


