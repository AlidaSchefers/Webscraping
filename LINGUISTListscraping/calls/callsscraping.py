# scrapes current Call for Papers postings on LINGUISTList

from bs4 import BeautifulSoup
import requests
import csv
import re #for regular expressions

#This program currently scrapes LINGUISTList's "browse current calls" webpage and the pages of individual conferences.

#this program writes a csv that...
    #contains each conference's title, website url, call deadline, location, start date, end date, Linguistic Field(s), Subject Language(s), and LINGUISTList url

#scraping from the website page:
source = requests.get('https://old.linguistlist.org/callconf/browse-current.cfm?type=Call').text
soup = BeautifulSoup(source, 'lxml')

#create a csv file
csv_file = open('calls_scrape.csv', 'w')
csv_writer = csv.writer(csv_file)

#write the top header in the csv file
csv_writer.writerow(['title', 'website_url', 'call_deadline', 'location', 'is_online_or_hybrid','start_date','end_date','linguistic_field(s)','subject_language(s)','LINGUISTList_url'])

#reducing the scraping code from the whole page to just the conferences listing
listing = soup.find('table', {'cellspacing': "10", "width": "100%"}).find_all('tr', recursive=False)[4:] #first conference is at index 4
listing = [item for item in listing if not (item.find('td', {'align':'left', 'valign':'top'}))] #removes tabbed session postings + browse-by-date line on top of page
listing = [item for item in listing if not (item.find('span', class_='important'))] #removes call for papers and date dividers
listing = [item for item in listing if not ('Session' in item.find('td').text)] #removes sessions that are only labeled as sessions in parentheses.

for posting in listing:
    #title
    title = posting.find('a').text[0:-1].replace('\n', ' ') #[0:-1] removes the \n at the end, and the replace('\n', ' ') makes the title and its shortened name in () stay on the same line

    #location, start_date, end_date, is_online_or_hybrid
    try:
        title_location_and_dates_text = posting.find('td').text 
            #e.g. 11th Conference of the International Gender and Language Association (IGALA11)&nbsp;[London (Online)] [22-Jun-2021 - 24-Jun-2021]
        location = re.findall('\[([^\]]*)\]', title_location_and_dates_text)[0] #regex finds bracketed text, but the parentheses in the regex makes it NOT return the brackets
        dates = re.findall('\[([^\]]*)\]', title_location_and_dates_text)[1]
        start_date = dates[0:11]
        end_date = dates[14:len(dates)]
        is_online_or_hybrid = bool(re.search('(online|virtual|zoom|hybrid|MS Teams)', str(location), flags=re.IGNORECASE))
    except Exception as e:
        location = None;
        start_date = None;
        end_date = None;
        is_online_or_hybrid = None;
    
    #linguistlist_url
    conference_id = posting.find('a')['href'][-6:]
    linguistlist_url = f'https://old.linguistlist.org/callconf/browse-conf-action.cfm?ConfID={conference_id}'

    #get info from the conference's specific LINGUISTList webpage
    conf_specific_source = requests.get(linguistlist_url).text
    conf_specific_soup = BeautifulSoup(conf_specific_source, 'lxml')
    conf_details = conf_specific_soup.find('div', class_='col-sm-8 text-left')

    #conf_website_url
    try:
        posting_str_ver = str(conf_details)
        if(len(re.findall('Web Site: <a href="([^"]*)"',posting_str_ver)) != 0):
            conf_website_url = re.findall('Web Site: <a href="([^"]*)"',posting_str_ver)[0]
        else:
            conf_website_url = re.findall('Meeting URL: <a href="([^"]*)"',posting_str_ver)[0]
    except Exception as e:
        conf_website_url = None

    #call_deadline
    try:
        call_deadline = re.findall('Call Deadline: (.*?) <br',posting_str_ver)[0]
    except Exception as e:
        call_deadline = None

    #ling_fields
    try:
        ling_fields = re.findall('Linguistic Field\(s\): (.*?)<br',posting_str_ver)[0]
    except Exception as e:
        ling_fields = None

    #subject_langs
    try:
        subject_langs = re.findall('Subject Language\(s\): (.*?)<br',posting_str_ver)[0]
    except Exception as e:
        subject_langs = None

    #write a row with the conference's details
    csv_writer.writerow([title, conf_website_url, call_deadline, location, is_online_or_hybrid, start_date, end_date, ling_fields, subject_langs, linguistlist_url])  