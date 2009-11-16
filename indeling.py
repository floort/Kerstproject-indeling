#!/usr/bin/env python

import sys
import csv
from munkres import Munkres




if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage:"
		print sys.argv[0], "data.csv"
		sys.exit(1)
	data = csv.reader(open(sys.argv[1]))
	
	# Collect all the workshops and votes
	votes = []
	workshops = set()
	for row in data:
		# Columns [2:12] contain the workshops
		for w in row[2:12]:
			workshops.add(int(w))
		votes.append({
			"name": row[1],
			"want": map(lambda i: int(i), row[2:7]),
			"dont": map(lambda i: int(i), row[7:12])
		})
	print "Workshops: ", workshops
	print "Votes: ", votes
	
	# Create empty cost matrix
	size = len(votes)
	cost = [[0 for j in xrange(size)] for i in xrange(size)]
	print cost

