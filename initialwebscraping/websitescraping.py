#using BeautifulSoup library and request library
from bs4 import BeautifulSoup
import requests
import csv

source = requests.get('https://coreyms.com/').text
soup = BeautifulSoup(source, 'lxml') #using lxml parser

csv_file = open('cms_scrape.csv', 'w') #'w' for 'write' this file

#use the writer method of csv module
csv_writer = csv.writer(csv_file)

#write the headers of the csv
csv_writer.writerow(['headline','summary','video_link', 'video keywords']) 

for article in soup.find_all('article'):

    headline = article.header.h2.a.text
    # print(headline)

    summary = article.find('div', class_='entry-content').p.text
    # print(summary)

    try:
        video_source = article.find('iframe', class_='youtube-player')['src']
        video_id = video_source.split('/')[4]
        video_id = video_id.split('?')[0]
        youtube_link = f'https://youtube.com/watch?v={video_id}'

        #get youtube video's views count as well
        youtube_source = requests.get(youtube_link).text
        youtube_soup = BeautifulSoup(youtube_source, 'lxml') #using lxml parser
        youtube_keywords = youtube_soup.find('meta', {'name': 'keywords'})['content']
    except Exception as e:
        youtube_link = None
        youtube_keywords = None

    # print(youtube_link)
    # print(youtube_keywords)
    # print()
    
    csv_writer.writerow([headline, summary, youtube_link, youtube_keywords])

csv_file.close()