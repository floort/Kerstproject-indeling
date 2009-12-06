#!/usr/bin/env python

import sys
import csv
from munkres import Munkres




if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage:"
		print sys.argv[0], "stemmen.csv workshops.csv leerlingen.csv"
		print " = stemmen.csv = "
		print '"vote_id","leerling_id","want1",..,"want5","no1",..,"no5","0"'
		print " = workshops.csv = "
		print '"workshhop_id","naam","aantal_rondes","open"'
		print " = leerlingen.csv = "
		print '"id","klas","naam","tussenv","achternaam","mentor"'
		sys.exit(1)
	
	data = csv.reader(open(sys.argv[1]))
	# Collect all the votes
	votes = []
	for row in data:
		votes.append({
			"name": row[1],
			"want": map(lambda i: int(i), row[2:7]),
			"dont": map(lambda i: int(i), row[7:12])
		})

	# TODO: find out the places available for each workshop
	# For now assume each workshop has 2 places
	places = []
	for w in workshops:
		places += [w,w,w]

	
	# Create empty cost matrix and fill in the cost for each assignment
	# NOTE: Lower "cost" is better
	cost = [[0 for j in xrange(len(places))] for i in xrange(len(votes))]
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
	
	
	# Now solve!
	m = Munkres()
	indices = m.compute(cost)
	for person, place in indices:
		print votes[person]["name"], "\t->\t", places[place]



