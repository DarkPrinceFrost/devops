import csv
f=open('users_2015_01_07.csv')
reader=csv.reader(f)
headers=reader.next()
d=open('candidates_deletion_2015-01-07_14_43.txt')
candidates=d.read().splitlines()
candict={}.fromkeys(candidates)
keep=[]
keep.append(headers)
reader=csv.reader(f)
for row in reader:
  if row[1] not in candict:
    keep.append(row)
len(keep)
f.close()
f=open('users_keep_2015_01_07.csv','w')
writer=csv.writer(f)
writer.writerows(keep)
f.close()
