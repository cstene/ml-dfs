import csv
import os.path
import constants as c
import datetime
import urllib2

from command_line import get_args
from bs4 import BeautifulSoup

def fetch_rg():
    print('Fetch Rotogrinders')
    urls = ['https://rotogrinders.com/projected-stats/mlb-hitter.csv?site=draftkings',
            'https://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=draftkings']
    
    with open(c.DIRPATHS['projections'] + 'rg_MLB_projection.csv', 'wb') as proj_file:
        proj_writer = csv.writer(proj_file)
        proj_writer.writerow(["playername", "points"])

        for url in urls:
            reader = csv.reader(urllib2.urlopen(url))
            for row in reader:
                proj_writer.writerow([row[0], row[7]])


if __name__ == '__main__':
    print('Welcome to fetch!')
    args = get_args()

    fetch_rg()

    print('Complete')

    # page_url = 'https://rotogrinders.com/projected-stats/mlb-pitch.csv?site=draftkings'
    # page = urllib2.urlopen(page_url)



    # with open(c.DIRPATHS['projections'] + 'test.csv', 'wb') as local_file:                
    #     rdr = csv.reader(page)
    #     wtr = csv.writer(local_file)
    #     wtr.writerow(["playername", "points"])
    #     for r in rdr:
    #         wtr.writerow([r[0], r[7]])
        



    #soup = BeautifulSoup(page.content, 'lxml')
    #for d in soup.select('div.player-popup'):
    #   print d.text
    


    

