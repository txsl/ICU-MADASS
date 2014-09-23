import csv
from os import listdir
from os.path import isfile, join

mypath = 'output/current_parents/'
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

try:
    onlyfiles.remove('.DS_Store')
except ValueError:
    pass

def check(group):
    data_current = {}
    data_missing = {}
    header = [u'username', u'email', u'first_name', u'last_name', u'Status', u'Department', u'UG/PG', u'full_name']

    for f in onlyfiles:
        with open('output/current_'+group+'/'+f, 'rb') as csvfile:
            # spamreader = csv.reader(csvfile)
            data_current[f] = list(list(rec) for rec in csv.reader(csvfile, delimiter=','))

    for f in onlyfiles:
        with open('output/missing_'+group+'/'+f, 'rb') as csvfile:
            # spamreader = csv.reader(csvfile)
            data_missing[f] = list(list(rec) for rec in csv.reader(csvfile, delimiter=','))

    for key, data in data_current.iteritems():
        data.pop(0)
        for line in data:
            if line in data_missing[key]:
                print 'ERROR', line
                data_missing[key].remove(line)

    for f in onlyfiles:
        with open('output/missing_'+group+'/'+f, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile)
            for line in data_missing[f]:
                spamwriter.writerow(line)

check('children')
check('parents')