import csv
import os.path
import constants as c
import datetime
import urllib2, urllib

from command_line import get_args
from bs4 import BeautifulSoup

def fetch_rg():
    print('Fetch Rotogrinders')
    league = args.l.upper()
    urls = c.PROJECTED_URLS[league]
    
    with open(c.DIRPATHS['projections'] + 'rg_{}_projection.csv'.format(league), 'wb') as proj_file:
        proj_writer = csv.writer(proj_file)
        proj_writer.writerow(["playername", "points", "team"])

        for url in urls:
            reader = csv.reader(urllib2.urlopen(url))
            for row in reader:
                proj_writer.writerow([row[0], row[7], row[2]])


if __name__ == '__main__':
    print('Welcome to fetch!')
    args = get_args()

    fetch_rg()

    # url = "https://www.fangraphs.com/dailyprojections.aspx"
    # data = urllib.urlencode({'pos':'all', 'stats':'bat', 'type':'sabersim'})
    # req = urllib2.Request(url, data)
    # response = urllib2.urlopen(req)

    # with open(c.DIRPATHS['projections'] + 'test.csv', 'wb') as local_file:                
    #     rdr = csv.reader(response)
    #     wtr = csv.writer(local_file)
    #     wtr.writerow(["playername", "points"])
    #     for r in rdr:
    #         wtr.writerow([r[0], r[18]])
    


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
    


    

