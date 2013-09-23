from __future__ import division
from db import db
from helpers import *
from collections import OrderedDict
import math
import pickle
import csv

work = stuff(db)



work.BuildInterests(4)
# print len(p), len(c)

# work.CalcFamInterests(fams[0], [])

# work.CalcSimilarity(fams[0],129093)

unallocatedFreshers = work.returnFreshers(4)
fams, familiesWithSpace = work.StartFamilies(4)

print fams
print len(unallocatedFreshers), len(fams), len(unallocatedFreshers) / (len(fams))
maxFamSize = math.ceil(len(unallocatedFreshers) / (len(fams)))

print 'Max Family Size is', maxFamSize

while unallocatedFreshers:
	scores = {}

	for fam in familiesWithSpace:
		for fresh in unallocatedFreshers:
			score = work.CalcSimilarity(fam, fams[fam], fresh)
			scores[(fam, fresh)] = score

	scores = OrderedDict(sorted(scores.items(), key=lambda t: t[1])) # Let's order them, so we can match the best score

	allocated = scores.popitem()

	famId = allocated[0][0]
	fresherId = allocated[0][1]

	print allocated

	fams[famId].append(fresherId)

	unallocatedFreshers.remove(fresherId)

	print len(fams[famId]), maxFamSize
	if len(fams[famId]) == maxFamSize:
		familiesWithSpace.remove(famId)
		print 'removing family'


	# order = []
	# for key, var in scores:
	# 	order.append(key)

# print scores
print fams

# convert fams to a list form for csv printing

toPrint = []

for rents, children in fams.iteritems():
	toPrint.append(list(rents) + children)

print toPrint

with open('output.csv', 'wb+') as csvfile:
	writer = csv.writer(csvfile)
	for line in toPrint:
		writer.writerow(line)


exit('All done!')