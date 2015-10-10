import psycopg2, datetime, ppygis, pprint, urllib2, BeautifulSoup


# scrapeUCPD accesses an archive on the UCPD website,
# scrapes it starting from the given input date,
# and yields the data row by row
def scrapeUCPD(resource, start):
   url_stem = 'https://incidentreports.uchicago.edu/' + resource + '.php?startDate='
   response = urllib2.urlopen('url_stem' + stuff)
   html = response.read()
   for
   yield row

# updateTable puts a row into the given table in the database
def updateTable():
