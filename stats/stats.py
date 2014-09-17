import urllib2, json, csv
from time import localtime, strftime

record_time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
name_time = strftime("%Y%m%d_%H%M%S", localtime())

response = urllib2.urlopen('https://www.imperialcollegeunion.org/mumsanddads/stats.php')
html = response.read()

data = json.loads(html)

depts = {}

# Build list of departments
for i in data['Freshers']:
    depts[i] = {}

for dept in depts:
    depts[dept]['ParentsExpected'] = data['Parents'][dept]['Expected']
    depts[dept]['ParentsActual'] = data['Parents'][dept]['Actual']
    depts[dept]['ParentsProposals'] = data['Proposals'][dept]['Count']

    depts[dept]['FreshersExpected'] = data['Freshers'][dept]['Expected']
    depts[dept]['FreshersActual'] = data['Freshers'][dept]['Actual']

# print depts

with open(name_time+'_stats.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['Department', 'ParentsExpected', 'ParentsActual', 'ParentsProposals', 'FreshersExpected', 'FreshersActual'])

    for key, value in sorted(depts.items()):
        # print key, value
        writer.writerow([key, value['ParentsExpected'], value['ParentsActual'], value['ParentsProposals'], value['FreshersExpected'], value['FreshersActual']])

    writer.writerow(["Data obtained: " + record_time])
