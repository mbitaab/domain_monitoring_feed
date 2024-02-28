import requests
import os
import sys
import os
import urllib.request
import urllib
from bs4 import BeautifulSoup
import re
import zipfile
from datetime import date
import time

def save_to_db(domain):
    pass

def get_whois_data(outfile):
    url = 'https://www.whoisds.com/newly-registered-domains'
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )

    try:
        response = urllib.request.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        print('______________________________\n\n\n\n\n', soup.select('table')[0])
        cell = soup.select('table')[0].select('a')[0]
        print(cell)
        dl_link = cell.get('href')
        print(dl_link)
        d = soup.select('td')[0].text
        filename = 'domains' + re.search(r'-[0-9]+-[0-9]+', d)[0][1:]
        print(f"fname: {filename}")


        r = requests.get(dl_link, allow_redirects=True)
        print(r.status_code)
        open(outfile, 'wb').write(r.content)

        # open the txt file
        archive = zipfile.ZipFile(outfile, 'r')
        links = archive.open('domain-names.txt')
        # write to dB
        for l in links.readlines():
            save_to_db(l.decode('utf-8'))
    except Exception as e:
        print(e)

def main():

    while True:

        today = date.today()
        print(f"date: {today}")
        filename = f"/tmp/all_data_{today}.zip" 
        for i in range(5):
            if os.path.exists(filename):
                break
            get_whois_data(filename)
            
        time.sleep(86400)
        
if __name__ == '__main__':
    main()