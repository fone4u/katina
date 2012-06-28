#!/usr/bin/python
'''
    katina.py
    Apple App Store reviews scraper with sentiment analysis

    by Athanasios "attheodo" Theodoridis - http://attheo.do

'''

import argparse
import requests
import re
import StringIO
import pprint
import elementtree.ElementTree as ET



# international store codes 
# ripped from http://blogs.oreilly.com/iphone/2008/08/scraping-appstore-reviews.html
appstorecodes = {
'Argentina':          143505,
'Australia':          143460,
'Belgium':            143446,
'Brazil':             143503,
'Canada':             143455,
'Chile':              143483,
'China':              143465,
'Colombia':           143501,
'Costa Rica':         143495,
'Croatia':            143494,
'Czech Republic':     143489,
'Denmark':            143458,
'Deutschland':        143443,
'El Salvador':        143506,
'Espana':             143454,
'Finland':            143447,
'France':             143442,
'Greece':             143448,
'Guatemala':          143504,
'Hong Kong':          143463,
'Hungary':            143482,
'India':              143467,
'Indonesia':          143476,
'Ireland':            143449,
'Israel':             143491,
'Italia':             143450,
'Korea':              143466,
'Kuwait':             143493,
'Lebanon':            143497,
'Luxembourg':         143451,
'Malaysia':           143473,
'Mexico':             143468,
'Nederland':          143452,
'New Zealand':        143461,
'Norway':             143457,
'Osterreich':         143445,
'Pakistan':           143477,
'Panama':             143485,
'Peru':               143507,
'Phillipines':        143474,
'Poland':             143478,
'Portugal':           143453,
'Qatar':              143498,
'Romania':            143487,
'Russia':             143469,
'Saudi Arabia':       143479,
'Schweiz/Suisse':     143459, 
'Singapore':          143464,
'Slovakia':           143496,
'Slovenia':           143499,
'South Africa':       143472,
'Sri Lanka':          143486,
'Sweden':             143456,
'Taiwan':             143470,
'Thailand':           143475,
'Turkey':             143480,
'United Arab Emirates'  :143481,
'United Kingdom':     143444,
'United States':      143441,
'Venezuela':          143502,
'Vietnam':            143471,
'Japan':              143462,
'Dominican Republic': 143508,
'Ecuador':            143509,
'Egypt':              143516,
'Estonia':            143518,
'Honduras':           143510,
'Jamaica':            143511,
'Kazakhstan':         143517,
'Latvia':             143519,
'Lithuania':          143520,
'Macau':              143515, 
'Malta':              143521,
'Moldova':            143523,  
'Nicaragua':          143512,
'Paraguay':           143513,
'Uruguay':            143514
}




def listCountriesWithAppStores():
    ''' Lists the country names that have an Apple App Store '''
    
    countries = appstorecodes.keys()
    countries.sort()

    print ('\n[+] Available AppStore countries:\n')
    for country in countries:
        print country

def get_reviews(app_id,country_id):
    ''' scrapes and downloads App Store reviews for all pages '''
    
    reviews = list()
    page_num = 0

    while 1:

        currentPageReviews = scrape_reviews(app_id,country_id,page_num)
        
        if len(currentPageReviews) == 0:
            break

        reviews = reviews + currentPageReviews
        page_num += 1

    print reviews


def scrape_reviews(app_id,country_id,page_num):
    ''' scrapes iTunes page of the app_id to grab reviews for page_num'''

    iTunesUserAgent = 'iTunes/9.2 (Macintosh; U; Mac OS X 10.6)'
    appleStoreFront = "%d-1" % country_id

    url = "http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%d&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (app_id, page_num)
    
    request = requests.get(url, headers={'X-Apple-Store-Front': appleStoreFront,'User-Agent': iTunesUserAgent})
    
    response = StringIO.StringIO(request.content)
    root = ET.parse(response).getroot()

    response.close()
    
    reviews= list()

    # heavily lifted coded
    for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/'):
        
        review_data = dict()

        review_node = node.find("{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle")
        if review_node is None:
            review_data["body"] = None
        else:
            review_data["body"] = review_node.text

        version_node = node.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL")
        if version_node is None:
            review_data["version"] = None
        else:
            review_data["version"] = re.search("Version [^\n^\ ]+", version_node.tail).group()
    
        user_node = node.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL/{http://www.apple.com/itms/}b")
        if user_node is None:
            review_data["username"] = None
        else:
            review_data["username"] = user_node.text.strip()

        rank_node = node.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView")
        try:
            alt = rank_node.attrib['alt']
            st = int(alt.strip(' stars'))
            review_data["rating"] = st
        except KeyError:
            review_data["rating"] = None

        topic_node = node.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b")
        if topic_node is None:
            review_data["topic"] = None
        else:
            review_data["topic"] = topic_node.text

        reviews.append(review_data)
        
    return reviews

if __name__ == '__main__':

    cmdparser = argparse.ArgumentParser(
        description='[~] katina.py - Apple App Store reviews scraper with sentiment analysis',
             epilog='[~] To find your app\'s id, check this gist:')

    # add integer argument for the id of the app the reviews we're scraping
    cmdparser.add_argument('-i','--id',
        default=0,
        metavar='app_id',
        type=int,
        help='Your app\'s App Store id number')

    # add boolean argument to check for sentiment analysis
    cmdparser.add_argument('-s','--sentiment',
        default=False,
        action='store_true',
        dest='should_analyze_sentiment',
        help='Perform sentiment analysis on each review body'
        )

  
    # add option to list countries
    cmdparser.add_argument('-l','--list',
        action='store_true',
        default=False,
        help='List all countries with Apple App Store')

    # add option for country name parsing
    cmdparser.add_argument('-c','--country',
        type=str,
        default='all',
        help='App Store country name.')

    arguments = cmdparser.parse_args()
    
    # logic
    if arguments.list:
    
        listCountriesWithAppStores()

    else:

        # no app id was set
        if arguments.id == 0:
            
            cmdparser.print_help()
            raise SystemExit

        else:
            
            country = arguments.country
            app_id = arguments.id

            # download reviews for all countries one by one
            if country == 'All':
                
                print 0
            
            # download reviews for preselected country
            else:
                
                country_name = arguments.country
                get_reviews(app_id,appstorecodes[country_name])


