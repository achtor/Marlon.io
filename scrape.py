import urllib2
from bs4 import BeautifulSoup

# scrapes an individual page for a table
# converts the table into a list of lists
def pageScrape(start,report,offset):
    urlbase = 'https://incidentreports.uchicago.edu/'
    if report == 'incidents':
        urlreport = 'incidentReportArchive.php'
        cols = 7
    elif report == 'traffic_stops':
        urlreport = 'trafficStopsArchive.php'
        cols = 9
    elif report == 'field_interviews':
        urlreport = 'fieldInterviewsArchive.php'
        cols = 8
    url = urlbase + urlreport + '?startDate=' + start + '&endDate=10000000000&offset=' + str(offset)
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    # get table text
    for tr in soup.find_all('tbody'):
        tds = tr.find_all('td')
    # get list of lists
    count = 0
    row = list()
    lol = list()
    for td in tds:
        row.append(td)
        count += 1
        if('No field interviews' in str(td) or 'No traffic stops' in str(td) 
        or 'No Incident Reports' in str(td)):
            count = 0
            row = list()
        elif(count % cols == 0):
            lol.append(row)
            row = list()
    # remove tags
    for lst in lol:
        row2 = list()
        for item in lst:
            a = str(item)
            a = a.replace('<td colspan="9">','')
            a = a.replace('<td colspan="8">','')
            a = a.replace('<td>','')
            a = a.replace('</td>','')
            row2.append(a)
        yield(row2)

#given a startdate, figure out how many offsets needed for all pages
def getOffset(start,report):
    urlbase = 'https://incidentreports.uchicago.edu/'
    if report == 'incidents':
        urlreport = 'incidentReportArchive.php'
    elif report == 'traffic_stops':
        urlreport = 'trafficStopsArchive.php'
    elif report == 'field_interviews':
        urlreport = 'fieldInterviewsArchive.php'
    url = urlbase + urlreport + '?startDate=' + start + '&endDate=10000000000'
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    st = soup.find_all('span')[9]
    st = str(st)
    st = st.replace('<span style="width:50px; border:none; color:#800;">1 /','')
    st = st.replace(' </span>','')
    st = int(st)
    return(st*5)

#scrape all, given a start date
def fullScrape(start,report):
    offset = getOffset(start,report)
    for i in range(0,offset,5):
        iterable = pageScrape(start, report, i)
        for page in iterable:
            yield page
