from __future__ import division
import numpy
import copy
import ast
import csv

from db import db, newerpol
from collections import OrderedDict
# import pickle

import matplotlib.pyplot as plt

from newerpol_schema import t_MumsandDads


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

def MumsandDadsViewToPrint(t_person):
    person = list(t_person)
    del person[-4] # Delete study year
    del person[-3] # Delete CID
    del person[3]
    del person[0] # Delete PeopleID
    return person

MumsandDadsViewHeader = [u'username', u'email', u'first_name', u'last_name', u'Status', u'Department', u'UG/PG', u'full_name']

def print_MADView_to_csv(filename, header, data):
    with open('output/'+filename+'.csv', 'w+') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(header)
        for row in data:
            spamwriter.writerow([unicode(s).encode("utf-8") for s in row])

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
        baseInt = 33 # 35 in 2014
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

    def build_department(self, dept_id):
        p_interests, c_interests = {}, {}
        all_freshers, all_parents = [], []

        all_members = self.mg.Metadata.find({"DepartmentId": dept_id})

        for m in all_members:
            collection_object = m['CollectionObject']
            personid = m['_id']

            if m['Collection'] == 'Couples':
                couple = self.mg.Couples.find_one({"_id": collection_object})
                for keys, items in couple.iteritems():
                try:
                    pid = long(keys)
                    if pid in all_parents

                except ValueError:
                    pass # Ie if the ID key

                p_interests[personid] = couple[unicode(personid)]['Interests']

            elif m['Collection'] == 'Freshers':
                fresher = self.mg.Freshers.find_one({"_id": collection_object})

                c_interests[personid] = fresher[unicode(personid)]['Interests']

            else:
                pass

        self.Interests = copy.deepcopy(p_interests)
        self.Interests.update(c_interests)

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

    def FindMissingParents(self, parents):
        all_couples = self.mg.Couples
        all_signed_up = []

        for c in all_couples.find():
            for keys, items in c.iteritems():
                try:
                    pid = long(keys)
                    # print pid
                    # meta = self.mg.Metadata.find_one({"_id": pid})
                    # print meta
                    # person = newerpol.query(t_MumsandDads).filter_by(ID=pid).first()
                    # try:
                    all_signed_up.append(pid)
                    # except TypeError:
                    # 	print '!!ERROR!! PeopleID', pid

                except ValueError:
                    pass # Ie if the ID key

        output = {}

        for d in self.ReturnDepts():
            deptname = d[1]
            potentials = self.newerpol.query(t_MumsandDads).filter_by(PersonStatus='Current', StudentTypeCode=u'UG', OCNameTypeName=unicode(deptname)).all()
            # potentials = self.newerpol.query(t_MumsandDads).filter(PersonStatus=='Current', StudentTypeCode=='UG', OCNameTypeName==deptname).all()
            for p in potentials:
                # print p
                # print all_signed_up
                # print potentials
                try:
                    all_signed_up.remove(p[-4])
                    print 'removing, ', p
                    potentials.remove(p)
                except ValueError:
                    pass

            for index, item in enumerate(potentials):
                potentials[index] = MumsandDadsViewToPrint(item)

            output[deptname] = potentials
        return output

    def FindMissingFreshers(self, freshers):
        all_signed_up = []

        for c in self.mg.Freshers.find():
            for keys, items in c.iteritems():
                try:
                    pid = long(keys)
                    all_signed_up.append(pid)
                except ValueError:
                    pass # Ie if the ID key

        output = {}

        for d in self.ReturnDepts():
            deptname = d[1]
            potentials = self.newerpol.query(t_MumsandDads).filter_by(PersonStatus='Incoming', StudentTypeCode=u'UG', OCNameTypeName=unicode(deptname)).all()
            # potentials = self.newerpol.query(t_MumsandDads).filter(PersonStatus=='Current', StudentTypeCode=='UG', OCNameTypeName==deptname).all()
            for p in potentials:
                # print p
                # print all_signed_up
                # print potentials
                try:
                    all_signed_up.remove(p[-4])
                    print 'removing, ', p
                    potentials.remove(p)
                except ValueError:
                    pass

            for index, item in enumerate(potentials):
                potentials[index] = MumsandDadsViewToPrint(item)

            output[deptname] = potentials
        return output

    def ListParents(self):
        all_couples = self.mg.Couples
        all_signed_up = {}

        for c in all_couples.find():
            for keys, items in c.iteritems():
                try:
                    pid = long(keys)
                    # print pid
                    meta = self.mg.Metadata.find_one({"_id": pid})
                    # print meta
                    person = newerpol.query(t_MumsandDads).filter_by(ID=pid).first()
                    try:
                        all_signed_up[meta['DepartmentId']].append(MumsandDadsViewToPrint(person))
                    except KeyError:
                        all_signed_up[meta['DepartmentId']] = []
                        all_signed_up[meta['DepartmentId']].append(MumsandDadsViewToPrint(person))
                    except TypeError:
                        print '!!ERROR!! PeopleID', pid

                except ValueError:
                    pass # Ie if the ID key

        return all_signed_up


    def ListFreshers(self):
        all_signed_up = {}

        all_freshers = self.mg.Freshers

        for f in all_freshers.find():
            for keys, items in f.iteritems():
                try:
                    pid = long(keys)
                    # print pid
                    meta = self.mg.Metadata.find_one({"_id": pid})
                    person = newerpol.query(t_MumsandDads).filter_by(ID=pid).first()
                    # print meta
                    try:
                        all_signed_up[meta['DepartmentId']].append(MumsandDadsViewToPrint(person))
                    except KeyError:
                        all_signed_up[meta['DepartmentId']] = []
                        all_signed_up[meta['DepartmentId']].append(MumsandDadsViewToPrint(person))
                    except TypeError:
                        print '!!ERROR!! PeopleID', pid

                except ValueError:
                    pass

        return all_signed_up
