#!/bin/bash
for d in cnx-archive cnx-authoring cnx-epub cnx-publishing \
         cnx-query-grammar openstax-accounts plpydbapi\
         rhaptos.cnxmlutils webview
  do (
    cd $d
     branchname=$(git symbolic-ref --short -q HEAD)
    echo -n $d": "
     git fetch -q
  echo -n $(git rev-list ^master origin/master| wc -l)
  if [ $branchname != "master" ]
  then
    echo " ($branchname) "$(git rev-list origin/master ^$branchname| wc -l)
  else
    echo
  fi
if [ "$1" = '-v' ]
then
  git log ^master origin/master 
  git log master ^$branchname
fi
   )
  done
