from db import db
from helpers import *
import argparse

parser = argparse.ArgumentParser(description='ICU MADASS Matching System')

parser.add_argument('-d', '--depts', type=long, nargs='*', help='Optional for only processing certain departments')
parser.add_argument('-a', '--anal', action='store_true', help='Raise this flag to run some analysis on the computed data')
parser.add_argument('--dry', action='store_true', help='Raise this flag to use data calculated and stored from before')

args = vars(parser.parse_args())

helper = stuff(db)
depts = dict(helper.ReturnDepts())


if args['depts']:
    print "Making babies for specified Departments..."
    for selectd in args['depts']:
        b = babyMaker(selectd, depts[selectd])
        
        if not args['dry']:
            print 'Making babies in', depts[selectd]
            b.makeBabies()
        else:
            b.open_matchings()
        
        if args['anal']:
            b.analyse()

else:
    print "Making babies for the entire University. Hold on tight: it's gona get warm..."
    for ids, dnames in depts.iteritems():
        print 'Making babies in', dnames
        makeBabies(ids, dnames, analysis=args['anal'])


exit('All done!')