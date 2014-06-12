/^cn:/N
s/\(cn:.* \(.*\)\)\n\(objectClass: account\)/\1\nsn: \2\n\3/
s/objectClass: account/objectClass: person\
objectClass: organizationalPerson\
objectClass: inetOrgPerson/
s/ account/ inetOrgPerson/
