#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Command-line script to download orphaned files from db
"""

import argparse
import os

import psycopg2

DEFAULT_PSYCOPG_CONNECTION_STRING = "dbname=cnxarchive user=cnxarchive " \
                                    "password=cnxarchive host=localhost " \
                                    "port=5432"


def get_orphan_fids(cursor):
    cursor.execute('select fileid from files f where not exists'
                   '   (select 1 from module_files mf'
                   '     where mf.fileid = f.fileid)'
                   ' and not exists'
                   '   (select 1 from collated_file_associations cfa'
                   '     where cfa.fileid = f.fileid)')
    results = cursor.fetchall()
    for result in results:
        yield result[0]


def get_file(cursor, fid):
    cursor.execute('select file from files where fileid=%s', [fid])
    res = cursor.fetchall()
    if res:
        return res[0][0]


def main(argv=None):
    parser = argparse.ArgumentParser(description='download orphan files')
    parser.add_argument('-d', '--db-conn-str',
                        default=DEFAULT_PSYCOPG_CONNECTION_STRING,
                        help='a psycopg2 db connection string')
    parser.add_argument('document_dir', metavar='doc', default='.',
                        help='directory to store orphan files in')
    args = parser.parse_args(argv)

    with psycopg2.connect(args.db_conn_str) as db_connection:
        with db_connection.cursor() as cursor:
            for fid in get_orphan_fids(cursor):
                path = os.path.join(args.document_dir, str(fid))
                f = get_file(cursor, fid)
                with open(path, 'w') as fp:
                    fp.write(str(f))


if __name__ == '__main__':
    main()
