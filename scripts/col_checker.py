#!/usr/bin/python
import requests

def walk(tree):
    if type(tree) == dict:
        if tree.has_key('id'):
            if tree['id'] != 'subcol':
                yield tree['id']
        if tree.has_key('contents'):
            for id in walk(tree['contents']):
                    yield id
    elif type(tree) == list:
        for item in tree:
            for id in walk(item):
                yield id    

with open('col.uuids') as f:
   colids=f.readlines()

print len(colids)

def check_col(c):
    for uid in walk(c['tree']):
        u,v = uid.split('@');
        r=requests.get('http://archive.cnx.org/contents/%s' % u)
        l=r.url.split('@')[1]
        if l != v:
            yield u,v,l

for cid in colids:
    r = requests.get('http://archive.cnx.org/contents/%s' % cid[:-1])
    if r:
        try:
            c=r.json()
        except:
            print r.url,'bad_json'
            continue
        bad_mods = list(check_col(c))
        if bad_mods:
            print r.url,bad_mods
