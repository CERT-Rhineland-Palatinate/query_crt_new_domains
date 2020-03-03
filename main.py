#!/usr/bin/env python3

import time
import smtplib
import socket
import argparse

import requests
import feedparser

try:
    from config import logfile, known_domains_db_path
except ModuleNotFoundError:
    print("Error - config.py not found")
    print("Please cp config_template.py to config.py")
    print("(and adjust the settings)")
    exit(-1)

def fetch_atom(tld):
    url = f"https://crt.sh/atom?identity={tld}"
    log(f"Fetching {url}")
    result = requests.get(url)
    log(f"Return Code: {result.status_code}")
    if result.status_code == 200:
        return(result)
    else:
        log(f"Error - Exit")
        exit(0)

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
    except SMTPException as e:
        print(e)
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

    records = []
    new_domains = []
    known_domains = read_known_domains()
    
    page = fetch_atom(tld_wc)
    domains = feedparser.parse(page.text)
    for d in domains['entries']:
        value = d['summary_detail']['value']
        value = value.split("<br>")
        value = value[0]
        value = value.split("\n")
        for v in value:
            records.append(v)

    records = list(set(records))
    records.sort()

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
        log("No Mail")
        exit(0)

    from config import m_host, m_sender, m_to, m_subject
    send_mail()


exit(0)
