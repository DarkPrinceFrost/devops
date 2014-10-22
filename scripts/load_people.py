#!/usr/bin/python

import csv
import optparse
import sys
import psycopg2


def store_person(cursor, person, appid):
    """load a csv row into db"""

    # Row looks like:
    # ['row_number', 'username', 'password_digest', 'title', 'first_name', 'last_name', 'full_name', 'email_address']

    row_num, username, password_digest, title, first_name, last_name, full_name, email = person

    cursor.execute("""INSERT into people (created_at, updated_at) 
       VALUES (CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) RETURNING id""")
    personid = cursor.fetchall()[0][0]

    cursor.execute("""INSERT into users (username, person_id, is_temp,
                                       first_name, last_name, full_name, title,
                                       uuid,
                                       created_at, updated_at)
                               values (%s,%s,%s,
                                       %s,%s,%s,%s,
                                       uuid_generate_v4(),
                                       CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) RETURNING id""",\
                 (username, personid, False,\
                 first_name, last_name, full_name, title ))
    userid = cursor.fetchall()[0][0]

    cursor.execute("""INSERT into identities (user_id, password_digest, 
                                            password_expires_at, 
                                            created_at, updated_at)
                                    values (%s,%s,
                                            CURRENT_TIMESTAMP - '1 day'::interval ,
                                            CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) RETURNING id""",\
                 (userid, password_digest ))
    identid = cursor.fetchall()[0][0]

    cursor.execute("""INSERT into authentications (user_id, provider, uid,
                                            created_at, updated_at)
                                    values (%s,'identity', %s,
                                            CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) RETURNING id""",\
                 (userid, identid ))

    cursor.execute("""INSERT into contact_infos (type, value, verified, user_id,
                                                 created_at, updated_at)
                                    values ('EmailAddress', %s , True, %s,
                                            CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) RETURNING id""",\
                 (email, userid ))

    cursor.execute("""INSERT INTO application_users (application_id, user_id, created_at, updated_at)
                   VALUES (%s, %s, NOW(), NOW())""",\
                 (appid, userid ))


def load_people(conn, appname,csvfile):
    cursor = conn.cursor()
    cursor.execute("""SELECT id from oauth_applications where name ~ %s""", (appname,))
    appid = cursor.fetchall()[0][0]

    csvlines = csv.reader(csvfile)
    for num,person in enumerate(csvlines,1):
        store_person(cursor,person, appid)
        if not (num % 1000):
            conn.commit()
            print "Stored: ", num

    conn.commit()
    print "Stored: ", num


def main():
    usage = 'Usage: %prog db_conn_str appname csv_filename'
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()
    if len(args) != 3:
        parser.error('database connection string, application name, and csv_filename required\n')
    
    with psycopg2.connect(sys.argv[1]) as conn, open(sys.argv[3]) as csvfile:
        load_people(conn,sys.argv[2],csvfile)

if __name__ == '__main__':
    main()
