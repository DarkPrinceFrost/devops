#!/bin/bash
for d in cnx-archive cnx-authoring cnx-epub cnx-publishing \
         cnx-query-grammar openstax-accounts plpydbapi webview
  do (
    cd $d
    echo -n $d": "
     git fetch
     git diff master..origin/master | wc -l
   )
  done
