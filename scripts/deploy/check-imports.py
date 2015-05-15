#!/usr/bin/env python
import importlib

PACKAGES = ('cnxarchive', 'cnxauthoring', 'cnxepub', 'cnxpublishing', 'cnxquerygrammar', 
            'openstax_accounts', 'rhaptos.cnxmlutils')

for p in PACKAGES:
    lib = importlib.import_module(p)
    print p,lib.__file__
