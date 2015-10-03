import argparse
from prettytable import PrettyTable

from db import mg
from core import *
from helpers import *

parser = argparse.ArgumentParser(description='ICU MADASS Matching System')

parser.add_argument('-d', '--depts', nargs='*', help='Optional for only processing certain departments')
parser.add_argument('-a', '--anal', action='store_true', help='Raise this flag to run some analysis on the computed data')
parser.add_argument('--dry', action='store_true', help='Raise this flag to use data calculated and stored from before')
parser.add_argument('-l', '--list', action='store_true', help='List all Departments')
parser.add_argument('-c', '--current', action='store_true', help='List all married couples in each department')

args = vars(parser.parse_args())

helper = stuff(mg)
depts = helper.ReturnDepts()

if args['list']:
    print 'Departments:'
    
    x = PrettyTable(["Department"])
    for dnames in depts:
        x.add_row([dnames])
    print x
    
    exit()

if args['current']:
    parents = helper.ListParents()
    for depts, people in parents.iteritems():
        name = db.Departments.filter(db.Departments.DepartmentId==depts).one()
        print_MADView_to_csv('current_parents/'+name.DepartmentNameTypeName, MumsandDadsViewHeader, people)
    
    missing_parents = helper.FindMissingParents(parents)
    for depts, people in missing_parents.iteritems():
        print_MADView_to_csv('missing_parents/'+depts, MumsandDadsViewHeader, people)


    freshers = helper.ListFreshers()
    for depts, people in freshers.iteritems():
        name = db.Departments.filter(db.Departments.DepartmentId==depts).one()
        print_MADView_to_csv('current_children/'+name.DepartmentNameTypeName, MumsandDadsViewHeader, people)

    missing_freshers = helper.FindMissingFreshers(freshers)
    for depts, people in missing_freshers.iteritems():
        print_MADView_to_csv('missing_children/'+depts, MumsandDadsViewHeader, people)


    exit()

if args['depts']:
    print "Making babies for specified Departments..."
    for selectd in args['depts']:
        b = babyMaker(selectd)
        
        if not args['dry']:
            print 'Making babies in', selectd
            b.makeBabies()
        else:
            b.open_matchings()
        
        if args['anal']:
            b.analyse()

else:
    print "Making babies for the entire University. Hold on tight: it's gona get warm..."
    for dnames in depts:
        print 'Making babies in', dnames
        b = babyMaker(dnames)
        b.makeBabies()
        if args['anal']:
            b.analyse()


exit('All done!')