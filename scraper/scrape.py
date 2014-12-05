#!/usr/bin/env python3
from bs4 import BeautifulSoup
from redis import StrictRedis
from requests import get
from datetime import datetime

DATA_URL = 'http://146.6.85.131/?command=TableDisplay&table=Table1&records=24'

# Returns a dictionary of the values with the timestamp as the key
def download_data():
    # Load and parse HTML table
    html = get(DATA_URL).text
    doc = BeautifulSoup(html)

    row = doc.find_all('tr')[-1]
    cells = row.find_all('td')

    return {
        'date': cells[0].text,
        'gh': float(cells[2].text),
        'dh': float(cells[3].text),
        'dir': float(cells[4].text),
        'uv': float(cells[5].text),
    }

def main():
    r = StrictRedis()
    
    key = datetime.now().strftime('%Y.%m.%d.%H.%m')

    r.hmset('toaster.%s' % key, download_data())
    # Expire slightly over 24 hours, just in case
    r.expire('toaster.%s' % key, 60 * 60 * 25)

if __name__ == '__main__':
    main()
