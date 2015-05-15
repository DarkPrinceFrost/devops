#!/bin/bash
for d in cnx-epub plpydbapi cnx-query-grammar rhaptos.cnxmlutils \
         cnx-archive cnx-authoring cnx-publishing \
         openstax-accounts
  do (
    cd $d
    python setup.py $1
   )
  done
