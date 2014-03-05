#!/usr/bin/python
import os
import psycopg2

conn = psycopg2.connect('dbname=repository user=rhaptos')
cur = conn.cursor()

files=os.listdir('.')
# creates a unique set of contentids and versions from filenames
idvers = set([tuple([f.split('-')[0]]+['.'.join(f.split('-')[1].split('.')[:2])]) for f in files if '-' in f])

extends = {'zip':'offline.zip',
            'pdf':'pdf',
            'xml':'xml',
            'epub':'epub'}

for id, ver in idvers:
    cur.execute("""select uuid, 
                 concat_ws('.',major_version,minor_version) as new_ver
                 from modules 
                 where moduleid = %s and version = %s 
                 order by revised desc limit 1""", (id,ver))
    res = cur.fetchall()
    if res:
        uuid = res[0][0]
        new_ver = res[0][1]
        for ext,lext in extends.items():
            fname = '{}-{}.{}'.format(id,ver,lext)
            if fname in files:
                new_fname = '{}@{}.{}'.format(uuid,new_ver,ext)
                print fname, '->', new_fname
                os.link(fname,new_fname)


