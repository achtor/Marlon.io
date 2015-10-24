import psycopg2, datetime, ppygis, pprint, daterangeparser, re, geocoder
from dateutil import parser
import scrape
import db_conn

# updateTable puts an iterable of rows into the given table in the database
def updateTable(table, rows):

   # open connection and get cursor
   conn_string = db_conn.conn_string
   try:
      conn = psycopg2.connect(conn_string)
   except:
      return
      # HANDLE EXCEPTION HERE
   cursor = conn.cursor()
   
   for row in rows: 
      if row[0] == 'Void':
         continue
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
         location = geocoder.google(address + ', Chicago, Illinois').latlng
         try:
            latlng = ppygis.Point(location[0], location[1])
         except:
            latlng = None
         qtuple = (incident, reported, occurred, comments, disposition, ucpd_num, address, latlng)
      elif table == 'traffic_stops':
         query_string = query_string + '(time, address, latlng, race, gender, reason, idot, cit_viol, \
                        disposition, search) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
         time = parser.parse(row[0])
         address = row[1]
         location = geocoder.google(address + ', Chicago, Illinois').latlng
         try:
            latlng = ppygis.Point(location[0], location[1])
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
         location = geocoder.google(address + ', Chicago, Illinois').latlng
         try:
            latlng = ppygis.Point(location[0], location[1])
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

