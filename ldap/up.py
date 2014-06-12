import sys
import base64


for line in sys.stdin:
  if line.find('::') == -1:
    print line,
  else:
    field,value = line.split()
    print field,base64.decodestring(value)
