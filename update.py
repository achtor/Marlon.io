import psycopg2, datetime, ppygis, pprint, daterangeparser, re
from geopy.geocoders import Nominatim
from dateutil import parser
import scrape

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

rows = scrape.fullScrape('09%2F01%2F2015', 'field_interviews')
for row in rows:
   print row
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
