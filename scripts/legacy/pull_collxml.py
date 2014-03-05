#!/usr/bin/python
import psycopg2
con=psycopg2.connect('dbname=repository user=rhaptos')
cur=con.cursor()
cur.execute("select uuid::text||'@'||concat_ws('.',major_version,minor_version)||'.xml',convert_from(file,'utf-8') from modules natural join module_files natural join files f where filename = 'collection.xml'")
res=cur.fetchall()
len(res)
for r in res:
    print r[0]
    f= open(r[0],'w')
    f.write(r[1])
    f.close()
