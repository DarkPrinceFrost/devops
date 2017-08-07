#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2017, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Command-line script to delete minor-version duplicates of books
"""
from __future__ import print_function

import argparse

import psycopg2

DEFAULT_PSYCOPG_CONNECTION_STRING = "dbname=cnxarchive user=cnxarchive " \
                                    "password=cnxarchive host=localhost " \
                                    "port=5432"


def get_dup_idents(cursor):
    cursor.execute("SELECT ident_hash(uuid,major_version,minor_version),"
                   "   max(module_ident), array_agg(module_ident)"
                   " FROM modules"
                   "    WHERE portal_type = 'Collection'"
                   " GROUP BY ident_hash(uuid,major_version,minor_version)"
                   " HAVING count(*) > 1"
                   )
    results = cursor.fetchall()
    for result in results:
        ident, keep, to_del = result
        to_del.remove(keep)
        yield ident, keep, to_del


def main(argv=None):
    parser = argparse.ArgumentParser(description='delete duplicate'
                                                 ' minor versions')
    parser.add_argument('-d', '--db-conn-str',
                        default=DEFAULT_PSYCOPG_CONNECTION_STRING,
                        help='a psycopg2 db connection string')
    parser.add_argument('--dry-run', action='store_true',
                        help='Prints SQL statements but does not modify db')
    args = parser.parse_args(argv)

    with psycopg2.connect(args.db_conn_str) as db_connection:
        with db_connection.cursor() as cursor:
            for ident, keep, to_del in get_dup_idents(cursor):
                print('\nProcessing {}:'
                      ' keeping {},'
                      ' deleting {}'.format(ident, keep, str(to_del)))
                for table in ('document_baking_result_associations',
                              'moduletags',
                              'module_files',
                              'modules'):
                    stmt = ('DELETE FROM {}'
                            ' WHERE module_ident'
                            ' in %s'.format(table), (tuple(to_del),))
                    if args.dry_run:
                        print(stmt[0] % stmt[1])
                    else:
                        cursor.execute(*stmt)

                print('Triggering baking for {}'.format(keep))
                stmt = ('UPDATE modules set stateid=5'
                        ' where module_ident = %s', (keep,))
                if args.dry_run:
                    print(stmt[0] % stmt[1])
                else:
                    cursor.execute(*stmt)


if __name__ == '__main__':
    main()
