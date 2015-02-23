#!/usr/bin/env python
import os
import filecmp
dir1 = '/var/www/files'
dir2 = '/var/www/files2'


to_del = []

fileset = set(os.listdir(dir1))
fileset2= set(os.listdir(dir2))

dups = fileset.intersection(fileset2)

for fname in dups:
    f1=os.path.join(dir1,fname)
    f2=os.path.join(dir2,fname)
    if not filecmp.cmp(f1,f2):
        if os.stat(f1).st_mtime > os.stat(f2).st_mtime:
            to_del.append(f2)
        elif os.stat(f1).st_mtime < os.stat(f2).st_mtime:
            to_del.append(f1)
        else:
            print "same timestamp: %s" % (fname,)
    else:
        print "identical file: %s" % (fname,)
        to_del.append(f1)

for d in to_del:
    print d
    os.unlink(d)



