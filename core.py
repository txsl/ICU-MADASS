from __future__ import division
from collections import OrderedDict
import math
import csv
import shelve
import matplotlib.pyplot as plt
from db import db, mg, newerpol

from helpers import *

class babyMaker:

    def __init__(self, DeptId, DeptName):
        self.DeptId = DeptId
        self.DeptName = DeptName
        self.CamelName = DeptName.replace(' ', '')

        self.work = stuff(db, mg, newerpol)

    def makeBabies(self):

        unallocatedFreshers, fams, familiesWithSpace = self.work.build_department(self.DeptId)
        # exit()

        # unallocatedFreshers = self.work.returnFreshers(self.DeptId)
        # fams, familiesWithSpace = self.work.StartFamilies(self.DeptId)

        maxFamSize = math.ceil(len(unallocatedFreshers) / (len(fams)))
        print 'Matching {pars} pairs of parents with {childs} children.\nMax Family size is {famsize}'.format(pars=len(fams), childs=len(unallocatedFreshers), famsize=maxFamSize)
        print math.ceil(183/53), 183/53
        # exit()
        allocated_score = []

        while unallocatedFreshers:
            scores = {}

            for fam in familiesWithSpace:
                for fresh in unallocatedFreshers:
                    score = self.work.CalcSimilarity(fam, fams[fam], fresh)
                    scores[(fam, fresh)] = score
            print scores, unallocatedFreshers
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
