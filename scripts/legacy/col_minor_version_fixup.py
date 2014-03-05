#!/usr/bin/python
import psycopg2
import psycopg2.extras

con = psycopg2.connect('dbname=repo_new user=rhaptos port=5433')
cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

colident={}

cur.execute("select uuid,module_ident,major_version,minor_version from modules where portal_type = 'Collection'")

for r in cur.fetchall():
    colident[(r['uuid'],r['major_version'],r['minor_version'])] = r['module_ident']

for uuid,major,minor in colident:
    if minor > 1:
        cur.execute('select count(*) from modulekeywords where module_ident = %s', colident[uuid,major,minor])
        res=cur.fetchone()
        if res['count'] > 0:
            cur.execute('insert into modulekeywords (module_ident,keywordid) select %s, keywordid from modulekeywords where module_ident = %s', (colident[uuid,major,minor],colident[uuid,major,1]))
            print 'Keywords:',uuid,major,minor,cur.statusmessage

        cur.execute('select count(*) from moduletags where module_ident = %s', colident[uuid,major,minor])
        res=cur.fetchone()
        if res['count'] > 0:
            cur.execute('insert into moduletags (module_ident,tagid) select %s, tagid from moduletags where module_ident = %s', (colident[uuid,major,minor],colident[uuid,major,1]))
            print 'Subjects:',uuid,major,minor,cur.statusmessage
        conn.commit()
