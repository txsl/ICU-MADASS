import numpy
import copy

def AreTheyThere(haystack, needle):
	for item in haystack:
		if needle in item:
			print needle, 'already in'
			return True
	print needle, 'not in here'
	return False

class stuff:

	def __init__(self, db):
		self.db = db # This is an SQLSoup class (database connection) If crap string, then things will break.
		#db.PersonInterests.filter(db.PersonInterests.PersonId==14769)
		self.Interests = {}

	def GetInterests(self, PeopleId): # Gets interests for a particular department
		res = numpy.zeros(33) # We have 32 interests, but there's an offset of one
		ints = self.db.PersonInterests.filter(self.db.PersonInterests.PersonId==PeopleId)
		for i in range(ints.count()/2):
			res[ints[i].InterestId] = 1
		return res

	def BuildInterests(self, DeptId): # Builds interests up for an entire Department in to a dict, but tupled to split between parents and children (makes it easier later)
		Pinterests, Cinterests = {}, {}
		# For the parents
		people = self.db.ParentPeople.filter(self.db.ParentPeople.DepartmentId==DeptId)
 
		for person in people:
			Pinterests[person.PersonId] = self.GetInterests(person.PersonId)

		# For the freshers
		people = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId)

		for person in people:
			Cinterests[person.PersonId] = self.GetInterests(person.PersonId)		
		print len(Cinterests), len(Pinterests)
		self.Interests = copy.deepcopy(Pinterests)
		print len(Cinterests), len(Pinterests)
		self.Interests.update(Cinterests)
		print len(Cinterests), len(Pinterests)
		print len(self.Interests)

		return Pinterests, Cinterests

	def StartFamilies(self, DeptId): #This function works on the assumtion that there are no 'dud' parents. Data cleaned by the wonderful @lsproc
		parents = self.db.ParentPeople.filter(self.db.ParentPeople.DepartmentId==DeptId)
		start = []
		spouseless = 0
		for p in parents:
			if not AreTheyThere(start, p.PersonId):
				start.append((p.PersonId, p.ChosenSpouse))
			if p.ChosenSpouse == None:
				print 'no spouse'
				spouseless += 1
		print spouseless
		return start
