from db import db
from helpers import *
import argparse

parser = argparse.ArgumentParser(description='ICU MADASS Matching System')

parser.add_argument('-d', '--depts', type=long, nargs='*', help='Optional for only processing certain departments')

args = vars(parser.parse_args())['depts']

helper = stuff(db)
depts = dict(helper.ReturnDepts())


if args:
    print "Making babies for specified Departments..."
    for selectd in args:
        print 'Making babies in', depts[selectd]
        makeBabies(selectd, depts[selectd])
else:
    print "Making babies for the entire University. Hold on tight: it's gona get warm..."
    for ids, dnames in depts.iteritems():
        print 'Making babies in', dnames
        makeBabies(ids, dnames)


exit('All done!')