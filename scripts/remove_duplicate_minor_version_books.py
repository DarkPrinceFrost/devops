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
    cursor.execute("""\
SELECT ident_hash(uuid,major_version,minor_version),
   max(module_ident), array_agg(module_ident), max(portal_type)
 FROM modules
    WHERE portal_type IN
        ('Collection', 'SubCollection', 'CompositeModule')
 GROUP BY ident_hash(uuid,major_version,minor_version)
 HAVING count(*) > 1
""")
    results = cursor.fetchall()
    for result in results:
        ident, keep, to_del, portal_type = result
        to_del.remove(keep)
        yield ident, keep, to_del, portal_type

    cursor.execute("""\
SELECT ident_hash(uuid, major_version, minor_version), 0,
       array_agg(module_ident), max(portal_type)
FROM modules m
WHERE portal_type IN ('SubCollection', 'CompositeModule')
  AND NOT EXISTS (
          SELECT 1 FROM trees t WHERE t.documentid = m.module_ident)
GROUP BY ident_hash(uuid, major_version, minor_version)
""")
    results = cursor.fetchall()
    for result in results:
        ident, keep, to_del, portal_type = result
        yield ident, keep, to_del, portal_type


def merge_trees(cursor, dry_run, ident, keep, merge):
    """Merge tree updates into one tree.

    Args:
        cursor: psycopg2 database cursor
        dry_run (bool): If set to true, the SQL statements are printed out and
            the database is not modified.
        ident (str): The ident hash of the collection.
        keep (int): The module_ident of the collection to keep.
        merge (list): List of module_idents of the collections to merge into
            the `keep` tree.
    """
    stmt = """\
WITH RECURSIVE tree1 (nodeid, parentid, path, documentid)
AS (
    SELECT tr.nodeid, tr.parent_id, ARRAY[tr.nodeid], tr.documentid
        FROM trees tr
        WHERE tr.documentid = %s AND tr.is_collated = FALSE
    UNION ALL
    SELECT t.nodeid, t.parent_id, path || ARRAY[t.nodeid], t.documentid
        FROM trees t JOIN tree1 ON t.parent_id = tree1.nodeid
        WHERE t.nodeid != ANY(path)
), tree2 (nodeid, parentid, path, documentid)
AS (
    SELECT tr.nodeid, tr.parent_id, ARRAY[tr.nodeid], tr.documentid
        FROM trees tr
        WHERE tr.documentid IN %s AND tr.is_collated = FALSE
    UNION ALL
    SELECT t.nodeid, t.parent_id, path || ARRAY[t.nodeid], t.documentid
        FROM trees t JOIN tree2 ON t.parent_id = tree2.nodeid
        WHERE t.nodeid != ANY(path)
)
SELECT nodeid, documentid, m.uuid,
       ident_hash(m.uuid, m.major_version, m.minor_version)
    FROM tree1 JOIN modules m ON tree1.documentid = m.module_ident
    WHERE tree1.documentid IS NOT NULL
UNION ALL
SELECT nodeid, documentid, m.uuid,
       ident_hash(m.uuid, m.major_version, m.minor_version)
    FROM tree2 JOIN modules m ON tree2.documentid = m.module_ident
    WHERE NOT EXISTS (
        SELECT 1
            FROM tree1
            WHERE tree1.documentid = tree2.documentid
    ) AND tree2.documentid IS NOT NULL
"""
    cursor.execute(stmt, (keep, tuple(merge)))
    original_tree = False
    # for original tree, uuid -> (nodeid, documentid)
    uuid_to_nodeid = {}
    # for all trees, uuid -> [documentid, ...]
    uuid_to_documentids = {}
    # for all trees, documentid -> ident_hash
    documentid_to_ident_hash = {}

    for nodeid, documentid, uuid_, ident_hash in cursor.fetchall():
        if ident_hash == ident:
            # the original tree is the first one that gets returned
            original_tree = not uuid_to_nodeid
            continue
        if original_tree:
            uuid_to_nodeid[uuid_] = (nodeid, documentid)
        uuid_to_documentids.setdefault(uuid_, [])
        uuid_to_documentids[uuid_].append(documentid)
        documentid_to_ident_hash[documentid] = ident_hash

    for uuid_, (nodeid, documentid) in uuid_to_nodeid.iteritems():
        documentids = sorted(uuid_to_documentids[uuid_], reverse=True)
        new_documentid = documentids[0]
        if documentid != new_documentid:
            print('Update tree nodeid {} from {} (documentid={}) '
                  'to {} (documentid={})'
                  .format(nodeid, documentid_to_ident_hash[documentid],
                          documentid,
                          documentid_to_ident_hash[new_documentid],
                          new_documentid))
            stmt = ('UPDATE trees SET documentid = %s '
                    'WHERE nodeid = %s', (new_documentid, nodeid))
            if dry_run:
                print(stmt[0] % stmt[1])
            else:
                cursor.execute(*stmt)


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
            for ident, keep, to_del, portal_type in get_dup_idents(cursor):
                print('\nProcessing {} ({}):'
                      ' keeping {},'
                      ' deleting {}'
                      .format(ident, portal_type, keep, str(to_del)))
                if portal_type == 'Collection':
                    merge_trees(cursor, args.dry_run, ident, keep, to_del)
                if portal_type == 'CompositeModule':
                    stmt = ('DELETE FROM collated_file_associations'
                            ' WHERE item IN %s', (tuple(to_del),))
                    if args.dry_run:
                        print(stmt[0] % stmt[1])
                    else:
                        cursor.execute(*stmt)
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

                if portal_type == 'Collection':
                    print('Triggering baking for {}'.format(keep))
                    stmt = ('UPDATE modules set stateid=5'
                            ' where module_ident = %s', (keep,))
                    if args.dry_run:
                        print(stmt[0] % stmt[1])
                    else:
                        cursor.execute(*stmt)


if __name__ == '__main__':
    main()
