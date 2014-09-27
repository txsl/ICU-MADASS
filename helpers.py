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

EXTRA_DATA_DEPTS_KEY = {
    8: "CH_AUX",
    13: "PH_TUT"
}

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
        self.external_data, self.external_keys = self.generate_ancillary_keys()


    def generate_ancillary_keys(self):
        data, keys = {}, {}

        for dept_id, key in EXTRA_DATA_DEPTS_KEY.iteritems():
            data[dept_id] = {}

            freshers, parents = self.list_all_departmental_members(dept_id)

            for f_id, obj in freshers.iteritems():
                this_person = obj["raw"][unicode(f_id)]
                try:
                    data[dept_id][f_id] = this_person["ExternalData"][key]
                except KeyError:
                    print "Missing external data for", f_id

            for couple, obj in parents.iteritems():
                for person in couple:
                    this_person = obj["raw"][unicode(person)]
                    try:
                        data[dept_id][person] = this_person["ExternalData"][key]
                    except KeyError:
                        print "Missing external data for", person

            unique_keys = []

            for key in data[dept_id].itervalues():
                if key not in unique_keys:
                    unique_keys.append(key)

            keys[dept_id] = unique_keys

        return data, keys


    def returnFreshers(self, DeptId):
        exit("This function is now defunct")
        freshers = self.db.FresherPeople.filter(self.db.FresherPeople.DepartmentId==DeptId)
        ids = []
        for f in freshers:
            ids.append(f.PersonId)
        return ids

    def GetInterests(self, PeopleId, Chem): # Gets interests for a particular department
        exit("This function is now defunct")
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
        exit("This function is now defunct")
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

    def generate_interest_matrix(self, user_id, interest_list, dept_id=None):
        base_int = 36
        extra_weighting = 10
        extra_options = 0

        output = numpy.zeros(base_int)

        if dept_id in EXTRA_DATA_DEPTS_KEY:
            distrib = {}
            for key in self.external_keys[dept_id]:
                distrib[key] = extra_weighting * extra_options
                extra_options +=1
            output = numpy.zeros(base_int + extra_options*extra_weighting)
            try:
                key = self.external_data[dept_id][user_id]
            except KeyError:
                print "Once again, missing data for", user_id

            this_weighting = distrib[key]
            output[(base_int + this_weighting):(base_int + this_weighting + extra_weighting)] = 1

        for i in (interest_list):
            output[int(i)] = 1

        return output


    def list_all_departmental_members(self, dept_id):
        all_members = self.mg.Metadata.find({"DepartmentId": dept_id})

        freshers, parents = {}, {}
        parent_count = 0

        for m in all_members:
            collection_object = m['CollectionObject']
            personid = int(m['_id'])

            if m['Collection'] == 'Couples':
                parent_count +=1
                couple = self.mg.Couples.find_one({"_id": collection_object})
                this_couple = []

                # to extract the keys (IDs) from each couple
                for keys, items in couple.iteritems():
                    try:
                        pid = long(keys)
                        this_couple.append(pid)
                    except ValueError:
                        pass # Ie if the ID key

                this_couple = tuple(this_couple)

                # if we haven't looked at the couple already,
                        # add them to our list and dict
                if this_couple not in parents:
                    parents[this_couple] = {"raw": couple}

            elif m['Collection'] == 'Freshers':
                fresher = self.mg.Freshers.find_one({"_id": collection_object})
                freshers[personid] = {"raw": fresher}

            else:
                # They wouldn't be in either collection if they logged in
                    # but didn't actually then register (or got divorced)
                pass

        if len(parents) != parent_count/2:
            exit('Exiting: Something has gone wrong with parent compilation')

        return freshers, parents

    def list_freshers(self, dept_id):
        return self.list_all_departmental_members(dept_id)[0]


    def build_department(self, dept_id):

        p_interests, c_interests = {}, {}
        # all_freshers, all_parents = [], []
        freshers_list, parents_list = [], []
        families_start = {}
        # parent_count = 0

        # all_members = self.mg.Metadata.find({"DepartmentId": dept_id})

        freshers, parents = self.list_all_departmental_members(dept_id)

        for f_id, obj in freshers.iteritems():
            c_interests[f_id] = self.generate_interest_matrix(f_id, obj["raw"][unicode(f_id)]["Interests"], dept_id)
            freshers_list.append(f_id)


        for couples, obj in parents.iteritems():
            # store = self.mg.Couples.find_one({"_id": obj["_id"]})

            for person in couples:
                p_interests[person] = self.generate_interest_matrix(person, obj["raw"][unicode(person)]["Interests"], dept_id)

            families_start[couples] = []
            parents_list.append(couples)

        self.Interests = copy.deepcopy(p_interests)
        self.Interests.update(c_interests)

        return freshers_list, families_start, parents_list


    def StartFamilies(self, DeptId): #This function works on the assumtion that there are no 'dud' parents. Data cleaned by the wonderful @lsproc
        exit("This function is now defunct")
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
        # print parents, children, fresher
        # print self.Interests
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
