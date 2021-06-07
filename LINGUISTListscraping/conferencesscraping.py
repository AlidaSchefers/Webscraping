from bs4 import BeautifulSoup
import requests
import csv
import re #for regular expressions

#This program currently scrapes LINGUISTList's "browse current conferences" webpage and the pages of individual conferences.

#this program writes a csv that...
    #contains each conference's title, website url, location, start date, end date, Linguistic Field(s), Subject Language(s), and LINGUISTList url
#this version currently skips:
    #posts that are tabbed and labeled as "session"
    #posts that are labeled as "session" in the conference title parentheses.
    #calls for papers
    #mid-page date dividers

#scraping from the website page:
source = requests.get('https://old.linguistlist.org/callconf/browse-current.cfm?type=Conf').text
soup = BeautifulSoup(source, 'lxml')

#create a csv file
csv_file = open('conferences_scrape.csv', 'w')
csv_writer = csv.writer(csv_file)

#write the top header in the csv file
csv_writer.writerow(['title', 'website_url', 'location','start_date','end_date','linguistic_field(s)','subject_language(s)','LINGUISTList_url'])

#reducing the scraping code from the whole page to just the conferences listing
listing = soup.find('table', {'cellspacing': "10", "width": "100%"}).find_all('tr', recursive=False)[4:] #first conference is at index 4
listing = [item for item in listing if not (item.find('td', {'align':'left', 'valign':'top'}))] #removes tabbed session postings + browse-by-date line on top of page
listing = [item for item in listing if not (item.find('span', class_='important'))] #removes call for papers and date dividers
listing = [item for item in listing if not ('Session' in item.find('td').text)] #removes sessions that are only labeled as sessions in parentheses.

for posting in listing: #currently scraping 11 conference postings
    #title
    title = posting.find('a').text[0:-1].replace('\n', ' ') #[0:-1] removes the \n at the end, and the replace('\n', ' ') makes the title and its shortened name in () stay on the same line

    #location, start_date, end_date
    try:
        title_location_and_dates_text = posting.find('td').text 
            #e.g. 11th Conference of the International Gender and Language Association (IGALA11)&nbsp;[London (Online)] [22-Jun-2021 - 24-Jun-2021]
        location = re.findall('\[[^\]]*\]', title_location_and_dates_text)[0][1:-1]
        dates = re.findall('\[[^\]]*\]', title_location_and_dates_text)[1][1:-1] #[1:-1] removes the brackets      
        start_date = dates[0:11]
        end_date = dates[14:len(dates)]
    except Exception as e:
        location = None;
        start_date = None;
        end_date = None;
    
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

    #ling_fields
    try:
        ling_fields = re.findall('Linguistic Field\(s\): (.*?)<br',posting_str_ver)[0]
    except Exception as e:
        ling_fields = None
    
    #subject_langs
    try:
        subject_langs = re.findall('Subject Language\(s\): (.*?)<br',posting_str_ver)[0]
        #the conference at index 11 has subject languages.
    except Exception as e:
        subject_langs = None

    # print("Title: "+title+".\n\t"+"URL: "+str(conf_website_url)+"\n\tLing fields: "+str(ling_fields)+"\n\tSubject langs: "+str(subject_langs))

    #write a row with the conference's details
    csv_writer.writerow([title, conf_website_url, location, start_date, end_date, ling_fields, subject_langs, linguistlist_url])

# Initial notes -------------------------------
    #Things to skip:
    #DONE: the sessions indented. inside tr, then inside td use the align="left" valign="top attributes to find sessions
    #DONE: sessions described in parentheses: --> can't do yet. so we'll keep and have blank dates/etc and take the first link in href.
        # <tr>
        # <td colspan="2" align="left"><a href="/callconf/browse-conf-action.cfm?ConfID=426236">Accountability of Discursive Action and the Private-Public Interface
        # </a>
        # (Session of <a href="/callconf/browse-conf-action.cfm?ConfID=419116">17th International Pragmatics Conference</a>)
        # <br /></td>
        # </tr>
    #DONE: the month-year headers on the page
    #DONE: calls for papers
        # <tr>
        # <td colspan="2"><a href="../callconf/browse-conf-action.cfm?ConfID=443036">2nd International Linguistics Colloquium in Bolivia
        # <span>(ILCB)</span>
        # <span class="important">- Call for papers</span>
        # </a>
        # &nbsp;[Online] [17-Jul-2021 - 18-Jul-2021]<br /></td>
        # </tr>