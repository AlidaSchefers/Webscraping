from bs4 import BeautifulSoup
import requests
import csv
import re #for regular expressions

#this program currently scrapes from the HTML file of LINGUISTList's "browse current conferences" page.

#the csv this program writes...
    #contains each conference's: title, location, dates, and LINGUISTList url
    #does not contain each conference's: Linguistic Field(s), Subject Language(s), website
#this version currently:
    #skips posts that are tabbed and labeled as "session"
    #skips calls for papers
    #skips mid-page date dividers

#using the HTML file:
with open('browse_current_conferences.html') as html_file:
    soup = BeautifulSoup(html_file, features="lxml")
    csv_file = open('conferences_scrape.csv', 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['title', 'location','start_date','end_date','LINGUISTList_url'])
    
    listing = soup.find('table', {'cellspacing': "10", "width": "100%"}).find_all('tr', recursive=False)[4:] #first conference is at index 4, session post at index 10.

    listing = [item for item in listing if not (item.find('td', {'align':'left', 'valign':'top'}))] #removes tabbed session postings + browse-by-date line on top of page
    listing = [item for item in listing if not (item.find('span', class_='important'))] #removes call for papers and date dividers
    #UNSUCCESSFUL: # listing_wo_para_sessions = [item for item in listing_wo_tabbed_sessions if not (item.find('a', class_='important'))] #removes sessions that are only written in parantheses. 

    for posting in listing[0:10]: #test with a few conferences (no session posts)
        title_location_and_dates_text = posting.find('td').text 
            #e.g. 11th Conference of the International Gender and Language Association (IGALA11)&nbsp;[London (Online)] [22-Jun-2021 - 24-Jun-2021]
        conference_id = posting.find('a')['href'][-6:]
        dates = re.findall('\[[^\]]*\]', title_location_and_dates_text)[1][1:-1] #[1:-1] removes the brackets
        
        title = posting.find('a').text[0:-1] #[0:-1] removes the \n at the end
        location = re.findall('\[[^\]]*\]', title_location_and_dates_text)[0][1:-1]
        start_date = dates[0:11]
        end_date = dates[14:len(dates)]
        linguistlist_url = f'https://old.linguistlist.org/callconf/browse-conf-action.cfm?ConfID={conference_id}'

        csv_writer.writerow([title, location, start_date, end_date, linguistlist_url])

csv_file.close()

#Things to skip:
    #DONE: the sessions indented. inside tr, then inside td use the align="left" valign="top attributes to find sessions
    #NOT YET: sessions described in parentheses: --> can't do yet. so we'll keep and have blank dates/etc and take the first link in href.
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

#using the website:
    # source = requests.get('https://old.linguistlist.org/callconf/browse-current.cfm?type=Conf').text
    # soup = BeautifulSoup(source, 'lxml')