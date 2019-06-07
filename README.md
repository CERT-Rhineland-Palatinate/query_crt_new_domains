# Discover new subdomains with crt.sh-scanner
## find new webservices of your constituency

Queries crt.sh database and searches for added subdomains.

https://www.certificate-transparency.org/what-is-ct

## Idea

Very often new webservices in our constituency are setup without telling us.

Hopefully new webservices are using https. 

This script searches for domains who requested a certificate and reports newly found domains.

As certificates are requested while setting up new services, we will know about new services before they are launched. :-)

## Installation

Linux:

```sh
git clone https://github.com/CERT-Rhineland-Palatinate/query_crt_new_domains.git
cd crtsh-scanner
python3 -m venv .
source bin/activate
pip install -r requirements.txt
cp config_template.py config.py
```

## Usage

The first time the script is run, it will report all domains, found on crt.sh

Searching for new .tld.com domains on crt.sh

```./main.py -t .tld.com```

Turning on verbose output and mail the result

```./main.py -v -m -t .tld.com```
