# ./bin/zopectl run extract_users_to_csv.py csv_filename

import csv
import optparse
import sys

def extract_users(plone_site):
    pm = plone_site.portal_membership
    user_passwords = plone_site.acl_users.source_users._user_passwords
    for username in user_passwords:
        member = pm.getMemberById(username)
        password_digest = user_passwords[username]
        yield {
                'username': username,
                'fullname': member.getProperty('fullname'),
                'email_address': member.getProperty('email'),
                'password_digest': password_digest,
                'title': member.getProperty('title'),
                'first_name': '',
                'last_name': '',
                }

def to_csv(users, csv_filename):
    headers = ['row_number', 'username', 'password_digest', 'title',
            'first_name', 'last_name', 'full_name', 'email_address']
    outfile = open(csv_filename, 'wb')
    writer = csv.writer(outfile)
    writer.writerow(headers)
    for i, user in enumerate(users):
        writer.writerow([
            i + 1,
            user['username'],
            user['password_digest'],
            user['title'],
            user['first_name'],
            user['last_name'],
            user['fullname'],
            user['email_address']
            ])
        if (i + 1) % 10 == 0:
            print 'Extracted %s users...' % (i + 1)
            outfile.flush()
    outfile.close()
    return i + 1

def extract_users_to_csv(plone_site, csv_filename):
    users = extract_users(plone_site)
    number_of_users = to_csv(users, csv_filename)
    print 'Extracted %s users to %s' % (number_of_users, csv_filename)

def main():
    usage = 'Usage: ./bin/zopectl run %prog csv_filename'
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('csv_filename required\n')
    if 'app' not in dir():
        parser.error('This script needs to be run with zopectl.')
    extract_users_to_csv(app.objectValues('Plone Site')[0], sys.argv[1])

if __name__ == '__main__':
    main()
