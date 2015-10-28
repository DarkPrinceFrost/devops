#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Command-line script to take files on the commandline, store them in archive
and link them to documents based on uuids. Default is to take uuid from directory
name, and filename from the file itself, mimetype from magic
"""

import argparse
import os
import sys
import subprocess
import hashlib

import psycopg2
from psycopg2 import Binary

DEFAULT_PSYCOPG_CONNECTION_STRING = "dbname=cnxarchive user=cnxarchive " \
                                    "password=cnxarchive host=localhost " \
                                    "port=5432"

def get_idents(cursor, uuid):
    cursor.execute('select module_ident from modules where uuid = %s', [uuid])
    results =  cursor.fetchall()
    for result in results:
        yield result

def get_fileid(cursor,fpath):
    with open(fpath) as fp:
        bits = fp.read()
    sha1 = hashlib.new('sha1',bits).hexdigest()
    cursor.execute('select fileid from files where sha1=%s', [sha1])
    res=cursor.fetchall()
    if res:
        return res[0]
    else:
        cursor.execute('insert into files (file) values (%s) returning fileid',[Binary(bits)])
        res=cursor.fetchall()
        return res[0]

def get_abstractid(cursor,fpath):
    with open(fpath) as fp:
        bits = fp.read()
    sha1 = hashlib.new('sha1',bits).hexdigest()
    cursor.execute('select abstractid from abstracts where sha1(abstract)=%s', [sha1])
    res=cursor.fetchall()
    if res:
        return res[0]
    else:
        cursor.execute('insert into abstracts (abstract) values (%s) returning abstractid',[Binary(bits)])
        res=cursor.fetchall()
        return res[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description='upload files to archive '
            'linking them to documents via uuid from the directory name')
    parser.add_argument('-d', '--db-conn-str',
                        default=DEFAULT_PSYCOPG_CONNECTION_STRING,
                        help='a psycopg2 db connection string')
    parser.add_argument('document_dirs', metavar='doc', nargs='+',
                        help='document directory named via uuid')
    args = parser.parse_args(argv)

    with psycopg2.connect(args.db_conn_str) as db_connection:
        with db_connection.cursor() as cursor:
            for docdir in args.document_dirs:
                uuid = os.path.basename(docdir)
                print 'Processing doc "{}"'.format(uuid)
                files = os.listdir(docdir)
                for fname in files:
                    print "     {}".format(fname)
                    fpath = os.path.join(docdir,fname)
                    fid = get_fileid(cursor,fpath)
                    ident = None
                    mimeType = subprocess.check_output(['file', '--mime-type', '-Lb', fpath]).strip()
                    if filename == 'abstract.cnxml':
                        for ident in get_idents(cursor, uuid):
                            print "     (abstract)",ident, fid, fname
                            try:
                                cursor.execute('SAVEPOINT here')
                                abid = get_abstractid(cursor, fpath)
                                cursor.execute(
                                'update modules set abstractid = %s where module_ident = %s', [abid,ident])
                                print "abstract updated"
                            except psycopg2.IntegrityError:
                                cursor.execute('ROLLBACK TO SAVEPOINT here')
                                print "abstract skipped - something wrong"
                            else:
                                cursor.execute('RELEASE SAVEPOINT here')
                    else:
                        for ident in get_idents(cursor, uuid):
                            print "     ",ident, fid, fname, mimeType,
                            try:
                                cursor.execute('SAVEPOINT here')
                                cursor.execute(
                                    'insert into module_files (module_ident,fileid,filename,mimetype) values (%s,%s,%s,%s)',
                                    [ident, fid, fname, mimeType])
                                print "stored"
                            except psycopg2.IntegrityError:
                                cursor.execute('ROLLBACK TO SAVEPOINT here')
                                cursor.execute(
                                    'update module_files set fileid = %s, mimetype= %s where module_ident = %s and filename = %s',
                                    [fid, mimeType, ident, fname])
                                print "updated"
                            else:
                                cursor.execute('RELEASE SAVEPOINT here')
                    if not ident:
                        print "doc not in archive"
                db_connection.commit()

if __name__ == '__main__':
    main()
