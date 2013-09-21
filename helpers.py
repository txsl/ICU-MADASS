import numpy

class stuff:

	def __init__(self, db):
		self.db = db # This is an SQLSoup class (database connection) If crap string, then things will break.
		#db.PersonInterests.filter(db.PersonInterests.PersonId==14769)

	def GetInterests(self, PeopleId): # Gets interests for a particular department
		res = numpy.zeros(33) # We have 32 interests, but there's an offset of one
		ints = self.db.PersonInterests.filter(self.db.PersonInterests.PersonId==PeopleId)
		for me in ints:
			print me
		for i in range(ints.count()/2):
			res[ints[i].InterestId] = 1
		return res

	def BuildInterests(self, DeptId, Parents): # Builds interests up for an entire Department in to a dict
		interests = {}
		if Parents:  # Selecting whether to query the parent or child table
			people = self.db.ParentPeople.filter(self.db.ParentPeople.DepartmentId==DeptId)
		else:
			people = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId) 
		for person in people:
			interests[person.PersonId] = self.GetInterests(person.PersonId)
		print interests
		return interests