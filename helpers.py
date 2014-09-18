from __future__ import division
import numpy
import copy
from db import db, newerpol, mg
from collections import OrderedDict
import math
import pickle
import csv
import shelve
import matplotlib.pyplot as plt
from sqlalchemy import Table


class babyMaker:

	def __init__(self, DeptId, DeptName):
		self.DeptId = DeptId
		self.DeptName = DeptName
		self.CamelName = DeptName.replace(' ', '')

		self.work = stuff(db)

	def makeBabies(self):

		self.work.BuildInterests(self.DeptId)

		unallocatedFreshers = self.work.returnFreshers(self.DeptId)
		fams, familiesWithSpace = self.work.StartFamilies(self.DeptId)

		# print fams
		# print len(unallocatedFreshers), len(fams), len(unallocatedFreshers) / (len(fams))
		maxFamSize = math.ceil(len(unallocatedFreshers) / (len(fams)))

		print 'Matching {pars} pairs of parents with {childs} children.\nMax Family size is {famsize}'.format(pars=len(fams), childs=len(unallocatedFreshers), famsize=maxFamSize)

		allocated_score = []

		while unallocatedFreshers:
			scores = {}

			for fam in familiesWithSpace:
				for fresh in unallocatedFreshers:
					score = self.work.CalcSimilarity(fam, fams[fam], fresh)
					scores[(fam, fresh)] = score

			scores = OrderedDict(sorted(scores.items(), key=lambda t: t[1])) # Let's order them, so we can match the best score

			allocated = scores.popitem()

			famId = allocated[0][0]
			fresherId = allocated[0][1]
			score = allocated[1]

			if score == 0:
				print 'score is 0 so finding small families'
				famId = findSmallestFam(fams)
			
			allocated_score.append(score)

			fams[famId].append(fresherId)

			unallocatedFreshers.remove(fresherId)

			print len(fams[famId]), maxFamSize
			if len(fams[famId]) >= maxFamSize:
				print familiesWithSpace
				familiesWithSpace.remove(famId)
				print 'removing family'


			# order = []
			# for key, var in scores:
			# 	order.append(key)

		# print scores
		# print fams

		self.fams = fams
		self.allocated_score = allocated_score
		print 'scores: ', allocated_score

		self.save_matchings()
		self.print_families_to_file()

	def analyse(self):
		sizes = {}
		for rents, children in self.fams.iteritems():
			try:
				sizes[len(children)] += 1

			except KeyError:
				sizes[len(children)] = 1
		print 'Distribution of family sizes:', sizes

		print sizes.keys(), sizes.values()
		plt.figure()
		# plt.ion()
		plt.bar(sizes.keys(), sizes.values())
		plt.show()
		# plt.hist(sizes.values(), bins=len(sizes.keys()), range=sizes.keys())

	def save_matchings(self):
		s = shelve.open('shelves/{fname}'.format(fname=self.CamelName))
		s['DeptName'] = self.DeptName
		s['fams'] = self.fams
		s['allocated_score'] = self.allocated_score
		s.close()

	def open_matchings(self):
		s = shelve.open(('shelves/{fname}').format(fname=self.CamelName))
		self.DeptName = s['DeptName']
		self.fams = s['fams']
		self.allocated_score = s['allocated_score']
		s.close()

	def print_families_to_file(self):
		# convert fams to a list form for csv printing

		toPrint = []

		for rents, children in self.fams.iteritems():
			rentlist = list(rents)
			for c in children:
				toPrint.append([c] + rentlist)

		print toPrint

		header = ['child', 'parent 1', 'parent 2']
		# for i in range(1, int(maxFamSize) + 1):
		# 	header.append('child ' + str(i))

		with open('output/' + self.CamelName + '.csv', 'wb+') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(header)
			for line in toPrint:
				writer.writerow(line)

def printParents():
	work = stuff(db)
	depts = work.ReturnDepts()
	print depts
	for d in depts:
		pointless, fams = work.StartFamilies(d[0])
		toPrint = []
		for f in fams:
			toPrint.append(f)
		DeptName = d[1].split(" ")
		fname = ''
		for l in DeptName:
			fname = fname + l
		fname = fname + '.csv'

		header = ['parent 1', 'parent 2']

		with open('parents/' + fname, 'wb+') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(header)
			for line in toPrint:
				writer.writerow(line)

def findSmallestFam(fams):
	size = 10000 # We're never going to have a family this big (I hope)!
	smallRents = None
	print fams
	for rents, childs in fams.iteritems():
		if len(childs) < size:
			print 'smallest family is', len(childs)
			smallRents = rents
			size = len(childs)
	return smallRents

def AreTheyThere(haystack, needle):
	for item in haystack:
		if needle in item:
			# print needle, 'already in'
			return True
	# print needle, 'not in here'
	return False

class stuff:

	def __init__(self, db, mg, newerpol):
		self.db = db # This is an SQLSoup class (database connection) If crap string, then things will break.
		#db.PersonInterests.filter(db.PersonInterests.PersonId==14769)
		self.mg = mg
		self.newerpol = newerpol
		self.Interests = {}

	def returnFreshers(self, DeptId):
		freshers = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId)
		ids = []
		for f in freshers:
			ids.append(f.PersonId)
		return ids

	def GetInterests(self, PeopleId, Chem): # Gets interests for a particular department
		baseInt = 33
		extraWeighting = 10 # How many 'interests' are we giving these external ones?
		extraOptions = 6

		res = numpy.zeros(baseInt) # We have 32 interests, but there's an offset of one
		if Chem:
			res = numpy.zeros(baseInt + (extraOptions * extraWeighting))
		ints = self.db.PersonInterests.filter(self.db.PersonInterests.PersonId==PeopleId)
		for i in range(ints.count()):
			res[ints[i].InterestId] = 1
		
		if Chem:
			try:
				anc = self.db.PersonExternalData.filter(self.db.PersonExternalData.PersonId==PeopleId)
				# print PeopleId
				# print anc[0].DataValue
				anc = anc[0].DataValue
				distrib = {
							'MPC': 0,
							'MEDBIO': extraWeighting,
							'CHEMENG': extraWeighting*2,
							'LANG': extraWeighting*3,
							'HUMANITIES': extraWeighting*4,
							'': extraWeighting*5,
				}
				res[(baseInt + distrib[anc]):(baseInt + distrib[anc] + extraWeighting)] = 1
				# print res
			except IndexError:
				print PeopleId, "doesn't have an entry in the External Data Table"
		return res

	def BuildInterests(self, DeptId): # Builds interests up for an entire Department in to a dict, but tupled to split between parents and children (makes it easier later)
		Pinterests, Cinterests = {}, {} # Like this as a hangover, in case we want to return these rather than just keep them
		# For the parents
		people = self.db.ParentPeople.filter(self.db.ParentPeople.DepartmentId==DeptId)
 
		for person in people:
			if DeptId == 8:
				Pinterests[person.PersonId] = self.GetInterests(person.PersonId, True)
			else:
				Pinterests[person.PersonId] = self.GetInterests(person.PersonId, False)
		# For the freshers
		people = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId)

		for person in people:
			if DeptId == 8:
				Cinterests[person.PersonId] = self.GetInterests(person.PersonId, True)		
			else:
				Cinterests[person.PersonId] = self.GetInterests(person.PersonId, False)

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
		combined = numpy.logical_or(self.Interests[parents[0]], self.Interests[parents[1]])
		for child in children:
			combined = numpy.logical_or(combined, self.Interests[child])
		# combined = numpy.divide(combined, 2 + len(children))
		return numpy.dot(combined, self.Interests[fresher])

		## Below is some of Fabian's experimentation with taking between the vectors
		# com_norm = numpy.linalg.norm(combined)
		# ch_norm = numpy.linalg.norm(self.Interests[fresher])
		# dotproduct = numpy.dot(combined, self.Interests[fresher])
		# import math
		# return math.pi-math.acos(dotproduct/(ch_norm*com_norm))

	def ReturnDepts(self):
		depts = self.db.Departments.filter(self.db.Departments.OptedOut==0)
		r = []
		for d in depts:
			r.append((d.DepartmentId, d.DepartmentNameTypeName))
		return r

	def ListParents(self):
		all_couples = self.mg.Couples
		# all_couples.distinct()
		# s = self.newerpol.MumsandDads
		# s = s.alias['MumsandDads']
		# newerpol_table = db.map(s, primary_key=[s.CID])
		# print newerpol_table.all()

		# pa_t = Table("MumsandDads", self.newerpol._metadata, autoload=True)
		# pa = u.map(pa_t,primary_key=[pa_t.c.CID])
		# pa.all()

		# print all_couples.collection_names()
		all_signed_up = {}

		for c in all_couples.find():
			for keys, items in c.iteritems():
				try:
					pid = long(keys)
					# print pid
					meta = self.mg.Metadata.find_one({"_id": pid})
					# print meta
					try:
						all_signed_up[meta['DepartmentId']].append(pid)
					except KeyError:
						all_signed_up[meta['DepartmentId']] = []
						all_signed_up[meta['DepartmentId']].append(pid)
					except TypeError:
						print '!!ERROR!! PeopleID', pid

				except ValueError:
					pass

		print all_signed_up
				# for k in keys:
					# print k
					# try:
					# 	pid = float(k)
					# 	print pid, k
					# except ValueError:
					# 	pass

	def ListFreshers(self):
		print 'Freshers'
		all_signed_up = {}

		all_freshers = self.mg.Freshers

		for f in all_freshers.find():	
			for keys, items in f.iteritems():
				try:
					pid = long(keys)
					# print pid
					meta = self.mg.Metadata.find_one({"_id": pid})
					# print meta
					try:
						all_signed_up[meta['DepartmentId']].append(pid)
					except KeyError:
						all_signed_up[meta['DepartmentId']] = []
						all_signed_up[meta['DepartmentId']].append(pid)
					except TypeError:
						print '!!ERROR!! PeopleID', pid

				except ValueError:
					pass
		print all_signed_up
