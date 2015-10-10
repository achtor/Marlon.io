import psycopg2, datetime, ppygis, pprint, urllib2, BeautifulSoup, daterangeparser, re,numpy as np
from geopy.geocoders import Nominatim
from dateutil import parser

# scrapeUCPD accesses an archive on the UCPD website,
# scrapes it starting from the given input date,
# and yields the data row by row
    

# scrapes an individual page for a table
# converts the table into a list of lists
def pageScrape(start,report,offset):
    urlbase = 'https://incidentreports.uchicago.edu/'
    if report == 'incident':
        urlreport = 'incidentReportArchive.php'
        cols = 7
    elif report == 'traffic':
        urlreport = 'trafficStopsArchive.php'
        cols = 9
    elif report == 'interview':
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
        if('No field interviews' in str(td) or 'No traffic stops' in str(td)):
            count = cols
        if(count % cols == 0):
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
    if report == 'incident':
        urlreport = 'incidentReportArchive.php'
    elif report == 'traffic':
        urlreport = 'trafficStopsArchive.php'
    elif report == 'interview':
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

# updateTable puts an iterable of rows into the given table in the database
def updateTable(table, rows):
   geolocator = Nominatim()

   # open connection and get cursor
   conn_string = 'host=\'localhost\' dbname=\'ucpd_data\' user=\'postgres\' password=\'LynchTheGrinch\''
   try:
      conn = psycopg2.connect(conn_string)
   except:
      return
      # HANDLE EXCEPTION HERE
   cursor = conn.cursor()
   
   for row in rows: 
      # put together query string
      query_string = 'INSERT INTO ' + table + ' '
      if table == 'incidents':
         query_string = query_string + '(incident, reported, occurred, comments, disposition, \
                        ucpd_num, address, latlng) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
         incident = row[0]
         reported = parser.parse(row[2])
         occurred = row[3]  # occurred formatting is just too varied and hard to handle, so put it in a string 
         comments = row[4]
         disposition = row[5]
         ucpd_num = row[6]
         address = row[1]
         location = geolocator.geocode(address + ', Chicago, Illinois')
         try:
            latlng = ppygis.Point(location.latitude, location.longitude)
         except:
            latlng = None
         qtuple = (incident, reported, occurred, comments, disposition, ucpd_num, address, latlng)
      elif table == 'traffic_stops':
         query_string = query_string + '(time, address, latlng, race, gender, reason, idot, cit_viol, \
                        disposition, search) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
         time = parser.parse(row[0])
         address = row[1]
         location = geolocator.geocode(address + ', Chicago, Illinois')
         try:
            latlng = ppygis.Point(location.latitude, location.longitude)
         except:
            latlng = None
         race = row[2]
         gender = row[3]
         reason = row[5]
         idot = row[4]
         cit_viol = row[6]
         disposition = row[7]
         search = (row[8] != 'No')
         qtuple = (time, address, latlng, race, gender, reason, idot, cit_viol, disposition, search)
      elif table == 'field_interviews':
         query_string = query_string + '(time, address, latlng, init, race, gender, reason, \
                        disposition, search) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
         time = parser.parse(row[0])
         address = row[1]
         location = geolocator.geocode(address + ', Chicago, Illinois')
         try:
            latlng = ppygis.Point(location.latitude, location.longitude)
         except:
            latlng = None
         init = row[2]
         race = row[3]
         gender = row[4]
         reason = row[5]
         disposition = row[6]
         search = (row[7] != 'No')
         qtuple = (time, address, latlng, init, race, gender, reason, disposition, search)

   # make the query
   print query_string
   print qtuple
   cursor.execute(query_string, qtuple)

   # commit
   conn.commit()
  

'''
TESTS 
row = ['10/1/2015 9:42 PM', '5700 Hyde Park', 'Asian', 'Female', 'Traffic Sign/Signal', 'Ran stop sign', 'N/A', 'Verbal Warning' ,'No']
rows = [row]
updateTable('traffic_stops', rows)

row = ['Harassment by Electronic Means', 'Greenwood at 58th', '2/9/11 12:52 PM', '1/14/11 to 2/1/11 various', 'Ex-boyfriend has harassed complainant with numerous unwanted email and voice messages', 'Open', 'X0172']
rows = [row]
updateTable('incidents', rows)

row = ['10/8/2015 9:11 PM', '969 E 60th St', 'Citizen request for UCPD Response', 'Caucasian', 'Male', 'Suspicious person', 'Name checked; released; no further action', 'No']
rows = [row]
updateTable('field_interviews', rows)
'''
