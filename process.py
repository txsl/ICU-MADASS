from db import db
from helpers import *

helper = stuff(db)

depts = helper.ReturnDepts()

for d in depts:
	print 'Making babies in', d[1]
	makeBabies(d[0], d[1])

exit('All done!')