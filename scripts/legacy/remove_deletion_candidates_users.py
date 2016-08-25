import sys
import csv
f=open(sys.argv[1])
reader=csv.reader(f)
headers=reader.next()
d=open(sys.argv[2])
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
f=open(sys.argv[3],'w')
writer=csv.writer(f)
writer.writerows(keep)
f.close()
