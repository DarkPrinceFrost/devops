import requests
f=open('col_check_out.txt')
for l in f:
    ll = l.split()
    col=ll[0]
    links = eval(' '.join(ll[1:]))
    for id,v1,v2 in links:
        r=requests.get('http://archive.cnx.org/contents/%s@%s' % (id,v1))
        r2=requests.get('http://archive.cnx.org/contents/%s@%s' % (id,v2))
        if not r:
            print id,v1, r, v2, r2
