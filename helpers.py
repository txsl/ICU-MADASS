from __future__ import division
import numpy
import copy
from db import db
from collections import OrderedDict
import math
import pickle
import csv

def makeBabies(DeptId,  DeptName):

	work = stuff(db)

	work.BuildInterests(DeptId)

	unallocatedFreshers = work.returnFreshers(DeptId)
	fams, familiesWithSpace = work.StartFamilies(DeptId)

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

	header = ['parent 1', 'parent 2']
	for i in range(1, int(maxFamSize) + 1):
		header.append('child ' + str(i))

	fname = ''
	for l in DeptName:
		fname = fname + l
	fname = fname + '.csv'

	with open(fname, 'wb+') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(header)
		for line in toPrint:
			writer.writerow(line)

def AreTheyThere(haystack, needle):
	for item in haystack:
		if needle in item:
			# print needle, 'already in'
			return True
	# print needle, 'not in here'
	return False

class stuff:

	def __init__(self, db):
		self.db = db # This is an SQLSoup class (database connection) If crap string, then things will break.
		#db.PersonInterests.filter(db.PersonInterests.PersonId==14769)
		self.Interests = {}

	def returnFreshers(self, DeptId):
		freshers = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId)
		ids = []
		for f in freshers:
			ids.append(f.PersonId)
		return ids

	def GetInterests(self, PeopleId): # Gets interests for a particular department
		res = numpy.zeros(33) # We have 32 interests, but there's an offset of one
		ints = self.db.PersonInterests.filter(self.db.PersonInterests.PersonId==PeopleId)
		for i in range(ints.count()):
			res[ints[i].InterestId] = 1
		return res

	def BuildInterests(self, DeptId): # Builds interests up for an entire Department in to a dict, but tupled to split between parents and children (makes it easier later)
		Pinterests, Cinterests = {}, {} # Like this as a hangover, in case we want to return these rather than just keep them
		# For the parents
		people = self.db.ParentPeople.filter(self.db.ParentPeople.DepartmentId==DeptId)
 
		for person in people:
			Pinterests[person.PersonId] = self.GetInterests(person.PersonId)

		# For the freshers
		people = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId)

		for person in people:
			Cinterests[person.PersonId] = self.GetInterests(person.PersonId)		

		self.Interests = copy.deepcopy(Pinterests)

		self.Interests.update(Cinterests)

	def StartFamilies(self, DeptId): #This function works on the assumtion that there are no 'dud' parents. Data cleaned by the wonderful @lsproc
		parents = self.db.ParentPeople.filter(self.db.ParentPeople.DepartmentId==DeptId)
		start = {}
		fam_list = []
		spouseless = 0
		for p in parents:
			if not AreTheyThere(start, p.PersonId):
				if p.ChosenSpouse is not None:
					start[(p.PersonId, p.ChosenSpouse)] = [] # Ie each family has an empty list of children to start off with
					fam_list.append((p.PersonId, p.ChosenSpouse))
				else:
					# print 'no spouse'
					spouseless += 1
		print 'spouseless: ', spouseless
		return start, fam_list

	# def CalcFamInterests(self, parents, children):
	# 	print parents[0], parents[1]
	# 	print self.Interests[parents[0]], self.Interests[parents[1]]
		
	# 	return combined

	def CalcSimilarity(self, parents, children, fresher):
		# print parents
		combined = numpy.add(self.Interests[parents[0]], self.Interests[parents[1]])
		for child in children:
			combined = numpy.add(combined, self.Interests[child])
		combined = numpy.divide(combined, 2 + len(children))
		return numpy.dot(combined, self.Interests[fresher])

	def ReturnDepts(self):
		depts = self.db.Departments.all()
		r = []
		for d in depts:
			r.append((d.DepartmentId, d.DepartmentNameTypeName))
		return r
		