#!/bin/bash
for d in cnx-archive cnx-authoring cnx-epub cnx-publishing \
         cnx-query-grammar openstax-accounts plpydbapi webview
  do (
    cd $d
    echo -n $d" "
     git describe --tags
   )
  done
