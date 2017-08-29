#!/usr/bin/env python

import argparse
import os


def de_dup(directories, dry_run=False):
    """Dedupliate files from multiple directories"""
    # Build a dictionary listing the dirs and ages for each file in that dir
    all_files = {}
    for dname in directories:
        for fname in os.listdir(dname):
            all_files.setdefault(fname, []).append((os.stat(os.path.join(dname, fname)).st_mtime, dname))

    # Find dir keys (filenames) that occur in more than one directory
    dupfiles = [fs for fs in all_files if len(fs) > 1]

    to_del = []
    for dup in dupfiles:
        dupdirs = all_files[dup]
        # Timestamp is first in tuple - sorts increasing
        dupdirs.sort()
        # Build paths to files, for all but last in each list, since it's the newest
        to_del.extend([os.path.join(d[1], dup) for d in dupdirs[:-1]])

    for d in to_del:
        print "deleting: %s" % (d,)
        if not dry_run:
            os.unlink(d)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Remove duplicate files in directories')
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Do not remove files but print out the files that are going to be deleted.')
    parser.add_argument(
        'directories', nargs='+',
        help='The directories that need duplicate files to be removed.')
    args = parser.parse_args(argv)
    de_dup(args.directories, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
