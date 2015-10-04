from __future__ import division
import numpy
import copy
import ast
import csv
import itertools
# from scipy.spatial.distance import jaccard

# from db import db, newerpol
from collections import OrderedDict
# import pickle

import matplotlib.pyplot as plt

# from newerpol_schema import t_MumsandDads

EXTRA_DATA_DEPTS_KEY = {
    "JMC & Computing": "DoC",
}

EXTERNAL_DATA_WEIGHTING = 10
BASE_INT = 36

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

def findSmallestFams(fams):
    size = 10000 # We're never going to have a family this big (I hope)!
    smallRents = []
    for rents, childs in fams.iteritems():
        if len(childs) < size:
            print 'smallest family is', len(childs)
            size = len(childs)

    for rents, childs in fams.iteritems():
        if len(childs) == size:
            smallRents.append(rents)
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

    def __init__(self, mg):
        self.mg = mg
        self.Interests = {}
        self.external_data, self.external_keys = self.generate_ancillary_keys()


    def generate_ancillary_keys(self):
        data, keys = {}, {}

        for dept_id, key in EXTRA_DATA_DEPTS_KEY.iteritems():
            data[dept_id] = {}

            freshers, parents, lone_parents = self.list_all_departmental_members(dept_id, return_lone_parents=True)

            for f_id, obj in freshers.iteritems():
                this_person = obj["raw"]['person']
                try:
                    data[dept_id][f_id] = this_person["ExternalData"][key]
                except KeyError:
                    print "Missing external data for", f_id

            for l_id, obj in lone_parents.iteritems():
                this_person = obj["raw"]["person"]
                try:
                    data[dept_id][f_id] = this_person["ExternalData"][key]
                except KeyError:
                    print "Missing external data for", l_id

            for couple, obj in parents.iteritems():
                for person, person_identifier in zip(couple, ['person_1', 'person_2']):
                    this_person = obj["raw"][person_identifier]
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



    def generate_interest_matrix(self, user_id, interest_list, dept_id=None):
        base_int = BASE_INT
        extra_weighting = EXTERNAL_DATA_WEIGHTING
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


    def list_all_departmental_members(self, dept_id, return_lone_parents=False, match_lone_parents=False):

        if return_lone_parents == True and match_lone_parents == True:
            exit("Cannot return list of lone parents AND match them - only one or the other (or neither)")

        all_members = self.mg.Metadata.find({"Department": dept_id})
        freshers, parents, lone_parents = {}, {}, {}
        parent_count = 0

        for m in all_members:
            
            if m['Username'] == None:
                print "Missing username for:", m
                continue

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
                    # print couple
                    # exit()

            elif m['Collection'] == 'Freshers':
                fresher = self.mg.Freshers.find_one({"_id": collection_object})
                freshers[personid] = {"raw": fresher}

            elif m['Collection'] == 'LoneParents':
                lone_parent = self.mg.LoneParents.find_one({"_id": collection_object})

                if match_lone_parents:
                    lone_parents[personid] = {'raw': lone_parent, 'interests': self.generate_interest_matrix(personid, lone_parent['person']['Interests'], dept_id)}
                else:
                    lone_parents[personid] = {"raw": lone_parent}

                # print lone_parents
                # exit()

            else:
                # They wouldn't be in either collection if they logged in
                    # but didn't actually then register (or got divorced)
                pass

        if match_lone_parents:
            print "matching %i lone parents together" % len(lone_parents)

            while (len(lone_parents) > 0):
                scores = {}
                for subset in itertools.combinations(lone_parents, 2):
                    scores[subset] = numpy.dot(lone_parents[subset[0]]['interests'], lone_parents[subset[1]]['interests'])

                scores = OrderedDict(sorted(scores.items(), key=lambda t: t[1])) # Let's order them, so we can match the best score

                allocated = scores.popitem()
                new_couple = allocated[0]

                parents[tuple(new_couple)] = {"raw": {'person_1': lone_parents[new_couple[0]]['raw']['person'], 'person_2': lone_parents[new_couple[1]]['raw']['person']}}
                # print parents[tuple(new_couple)]

                del lone_parents[new_couple[0]]
                del lone_parents[new_couple[1]]

                if len(lone_parents) == 1:
                    really_lone_parent = lone_parents.items()[0][0]

                    print "ONE LONE PARENT REMAINING: %i. Match them with %s" % (lone_parents.items()[0][0], new_couple)

                    del lone_parents[lone_parents.items()[0][0]]

        # if len(parents) != parent_count/2:
            # exit('Exiting: Something has gone wrong with parent compilation')

        if return_lone_parents:
            return freshers, parents, lone_parents
        else:
            return freshers, parents

    def list_freshers(self, dept_id):
        return self.list_all_departmental_members(dept_id)[0]


    def build_department(self, dept_id):

        p_interests, c_interests = {}, {}
        # all_freshers, all_parents = [], []
        freshers_list, parents_list = [], []
        families_start = {}
        # parent_count = 0

        all_members = self.mg.Metadata.find({"DepartmentId": dept_id})

        freshers, parents = self.list_all_departmental_members(dept_id, match_lone_parents=True)
        

        for f_id, obj in freshers.iteritems():
            
            c_interests[f_id] = self.generate_interest_matrix(f_id, obj["raw"]["person"]["Interests"], dept_id)
            freshers_list.append(f_id)


        for couples, obj in parents.iteritems():
            # store = self.mg.Couples.find_one({"_id": obj["_id"]})

            for person, person_identifier in zip(couples, ['person_1', 'person_2']):
                # print person, obj
                p_interests[person] = self.generate_interest_matrix(person, obj["raw"][person_identifier]["Interests"], dept_id)

            families_start[couples] = []
            parents_list.append(couples)

        self.Interests = copy.deepcopy(p_interests)
        self.Interests.update(c_interests)

        return freshers_list, families_start, parents_list

    def calc_min_score(self, dept_id):
        base_int = BASE_INT
        extra_weighting = EXTERNAL_DATA_WEIGHTING

        output = numpy.zeros(base_int)

        if dept_id in EXTRA_DATA_DEPTS_KEY:
            extra_options = 0

            distrib = {}
            for key in self.external_keys[dept_id]:
                distrib[key] = EXTERNAL_DATA_WEIGHTING * extra_options
                extra_options +=1
            output = numpy.zeros(base_int + extra_options*extra_weighting)

            this_weighting = 1
            output[(base_int + this_weighting):(base_int + this_weighting + extra_weighting)] = 1
        print output
        self.Interests['SpecialMinCalc'] = output
        return self.CalcSimilarity(('SpecialMinCalc', 'SpecialMinCalc'), [], 'SpecialMinCalc')


    def CalcSimilarity(self, parents, children, fresher):
        #
        # fresher self.Jaccard(parents, children, fresher)

        combined = numpy.logical_or(self.Interests[parents[0]], self.Interests[parents[1]])
        for child in children:
            combined = numpy.logical_or(combined, self.Interests[child])
        # return self.Jaccard(combined, self.Interests[fresher])
        return numpy.dot(combined, self.Interests[fresher])

        ## Below is some of Fabian's experimentation with taking between the vectors
        # com_norm = numpy.linalg.norm(combined)
        # ch_norm = numpy.linalg.norm(self.Interests[fresher])
        # dotproduct = numpy.dot(combined, self.Interests[fresher])
        # import math
        # return math.pi-math.acos(dotproduct/(ch_norm*com_norm))

    def ReturnDepts(self):
        metadata = self.mg.Metadata
        depts = metadata.distinct('Department')
        return depts

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
                    #   print '!!ERROR!! PeopleID', pid

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
