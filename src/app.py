import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
import re
import zipfile
from datetime import datetime, timedelta
from storage.mongodb.mongo_utility import *
from config import *
from storage.database import Database
import re

def return_limited_list(filtered_list,nrd_limit):
    if nrd_limit>0:
        return filtered_list[:nrd_limit] if len(filtered_list) >  nrd_limit else filtered_list
    else:
        return filtered_list

def website_filtering(url_list):
    # Keywords related to gambling and adult content
    gambling_keywords = ["casino", "bet", "poker", "gambling"]
    adult_keywords = ["adult", "sex", "porn", "xxx", "erotic", "nude", "dating", "romance", "romantic"]
    shipping_keywords = ["shipping", "cargo"]
    crypto_keywords = ["crypto", "bitcoin", "blockchain", "coin", "wallet"]

    # Compile regular expressions for keywords
    gamb_re = re.compile("|".join(gambling_keywords), re.IGNORECASE)
    adult_re = re.compile("|".join(adult_keywords), re.IGNORECASE)
    ship_re = re.compile("|".join(shipping_keywords), re.IGNORECASE)
    crypto_re = re.compile("|".join(crypto_keywords), re.IGNORECASE)

    filtered_list = []
    if url_list:
        for url in url_list:
            if not gamb_re.search(url) and not adult_re.search(url) and not ship_re.search(url) and not crypto_re.search(url):
                filtered_list.append(url)

    print(f"nrd urls filtered {len(filtered_list)}")
    return filtered_list

def get_whois_data():
    url = 'https://www.whoisds.com/newly-registered-domains'
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    flag, i, domain_list = False, 0, []
    while not flag and i < 5:
        i+= 1
        try:
            response = urllib.request.urlopen(req)
            soup = BeautifulSoup(response.read(), "html.parser")
            #print('______________________________\n\n\n\n\n', soup.select('table')[0])
            cell = soup.select('table')[0].select('a')[1]
            #print(cell)
            dl_link = cell.get('href')
            #dl_link = "https://www.whoisds.com//whois-database/newly-registered-domains/MjAyNC0wMy0wNS56aXA=/nrd"
            print(dl_link)
            d = soup.select('td')[0].text
            filename = 'domains' + re.search(r'-[0-9]+-[0-9]+', d)[0][1:]
            print(f"fname: {filename}")


            r = requests.get(dl_link, allow_redirects=True)
            print(r.status_code)
            outfile = "/tmp/tmp.zip"
            open(outfile, 'wb').write(r.content)

            # open the txt file
            archive = zipfile.ZipFile(outfile, 'r')
            links = archive.open('domain-names.txt')
            
            
            for l in links.readlines():
                # write to db
                domain_list.append(l.decode('utf-8'))
            flag = True
        except Exception as e:
            print(e)

    return domain_list



def get_shopify(today):

    url = f"https://www.merchantgenius.io/shop/date/{today}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    urls = [link.get('href') for link in links if link.get('href')]
    unq_urls = list(set(urls))

    shopify_list = []
    for url in unq_urls:
        if url.startswith('/shop/url/'):
            new_url = url.replace('/shop/url/', '')
            shopify_list.append(new_url)
    print(f"shopify urls fetched {len(shopify_list)}")
    return shopify_list

def main():
    mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource={mongo_db}"
    database = Database.instance()
    print(mongo_uri)
    database.create_connection(mongo_uri)

    #while True:
    yesterday= datetime.now() - timedelta(days=1)
    ystd = yesterday.strftime("%Y-%m-%d")
    print(f"date: {ystd}")
    final_list : list = []
    
    shopify_list = get_shopify(ystd)
    _shopify_list = return_limited_list(shopify_list,save_limit)
    final_list.extend(_shopify_list)
    nrd_list = get_whois_data()
    
    print(f"limit : {save_limit}")
    print(f"len(final_list) : {len(final_list)}")
    if save_limit == 0 : 
        selected_nrd = website_filtering(nrd_list)
        final_list.extend(selected_nrd)
    elif len(final_list) < save_limit:
        remained_limit = save_limit - len(final_list)
        selected_nrd = website_filtering(nrd_list)
        _selected_nrd = return_limited_list(selected_nrd,remained_limit)
        final_list.extend(_selected_nrd)
    unq_nrd = list(set(final_list))
    print(f"len(unq_nrd) : {len(unq_nrd)}")
    for item in unq_nrd:
        create_domain(item.strip(), _monitor=1, _crawl_freq=48)
    
    #if scheduler_time_interval>0:
    #    time.sleep(scheduler_time_interval)
    #else:
    #    break


if __name__ == '__main__':
    main()