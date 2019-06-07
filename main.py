#!/usr/bin/env python3

import time
import smtplib
import socket
import argparse

from psycopg2 import pool

try:
    from config import logfile, known_domains_db_path
    from config import db_host, db_port, db_user, db_db
except ModuleNotFoundError:
    print("Error - config.py not found")
    print("Please cp config_template.py to config.py")
    print("(and adjust the settings)")
    exit(-1)


def fetch_crt(tld):
    log(f"Querying database {db_db} on {db_host}:{db_port}")

    try:
        hbn = socket.gethostbyname(db_host)
    except Exception as e:
        print(f"Error:Can't resolve {db_host}")
        print(e)
        exit(-1)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((db_host, db_port))
    except Exception as e:
        print(f"Error:Can't connect to {db_host}:{db_port}")
        print(e)
        exit(-1)

    sql = f"""
        SELECT DISTINCT(ci.NAME_VALUE)
        FROM certificate_identity ci
        WHERE reverse(lower(ci.NAME_VALUE)) LIKE reverse(lower('{tld}'))
    """

    try:
        ppool = pool.SimpleConnectionPool(1, 20, user=db_user,
                                          host=db_host,
                                          port=db_port,
                                          database=db_db)
    except Exception as e:
        msg = "Error: Unable to connect to database server"
        print(e)
        log(msg)
        exit(-1)

    ps_connection = ppool.getconn()
    ps_connection.set_session(readonly=True, autocommit=True)
    ps_cursor = ps_connection.cursor()
    ps_cursor.execute(sql)
    records = ps_cursor.fetchall()
    log(f"Found {len(records)} records in db")

    tmp = []
    for record in records:
        tmp.append(record[0])
    records = tmp
    records.sort()

    return records


def log(msg):
    now = int(time.time())
    msg = f"{now}\t{msg}\n"
    with(open(logfile, "a")) as log:
        log.write(msg)

    if verbose is True:
        print(msg, end="")


def read_known_domains():
    log(f"Reading known domains file: {known_domains_db}")
    try:
        with(open(known_domains_db, "r")) as kd:
            known_domains = kd.read()
            return known_domains
    except FileNotFoundError:
        return []


def send_mail():
    log(f"Sending mail")

    message = f"""From: crt.sh script <{m_sender}>
To: To Person <{m_to}>
Subject: {m_subject}
               
{new_domains}
"""

    try:
        smtpObj = smtplib.SMTP(m_host)
        smtpObj.sendmail(m_sender, m_to, message)
        log("Successfully sent email")
    except SMTPException:
        log("Error: unable to send email")

if __name__ == "__main__":

    # Parse command line options

    p = argparse.ArgumentParser()
    p.add_argument("-t", "--tld", help="tld to query on crt.sh")
    p.add_argument("-m", "--mail", action="store_true", help="Mail new domains")
    p.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    args = p.parse_args()

    if args.tld is None:
        print("Please enter a tld to query on crt.sh")
        exit(-1)

    tld = args.tld
    tld = tld.strip()
    tld_wc = f"%.{tld}"
    tld_wc = tld_wc.replace("..", ".")

    verbose = bool(args.verbose)
    mail = bool(args.mail)

    known_domains_db = f"{known_domains_db_path}/db_{tld}"
    known_domains_db = known_domains_db.replace(".", "-")
    known_domains_db = f"{known_domains_db}.txt"

    log(f"Start for {tld}")

    new_domains = []
    known_domains = read_known_domains()
    records = fetch_crt(tld_wc)
    log(f"Found {len(records)} on crt.sh")

    for record in records:
        if record not in known_domains:
            new_domains.append(record)

    if len(new_domains) == 0:
        log("No new domains found on crt.sh.")
        exit(0)

    log(f"New Domains: {new_domains}")

    # Adding new domains to db

    log(f"Writing new domains to {known_domains_db}")
    with open(known_domains_db, "a+") as kd:
        for n in new_domains:
            kd.write(n+"\n")

    # Sending mail if requested
    if mail is False:
        exit(0)

    from config import m_host, m_sender, m_to, m_subject
    send_mail()


exit(0)
