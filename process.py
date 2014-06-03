from db import db
from helpers import *
import argparse

parser = argparse.ArgumentParser(description='ICU MADASS Matching System')

parser.add_argument('-d', '--depts', type=long, nargs='*', help='Optional for only processing certain departments')
parser.add_argument('-a', '--anal', action='store_true', help='Raise this flag to run some analysis on the computed data')

args = vars(parser.parse_args())

helper = stuff(db)
depts = dict(helper.ReturnDepts())


if args['depts']:
    print "Making babies for specified Departments..."
    for selectd in args['depts']:
        print 'Making babies in', depts[selectd]
        makeBabies(selectd, depts[selectd], analysis=args['anal'])
else:
    print "Making babies for the entire University. Hold on tight: it's gona get warm..."
    for ids, dnames in depts.iteritems():
        print 'Making babies in', dnames
        makeBabies(ids, dnames, analysis=args['anal'])


exit('All done!')