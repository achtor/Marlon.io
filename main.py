import psycopg2
import datetime
import ppygis
import pprint


def main():
   #Define our connection string
   conn_string = 'host=\'localhost\' dbname=\'ucpd_data\' user=\'postgres\' password=\'LynchTheGrinch\''
   
   # print the connection string we will use to connect
   print 'Connecting to database\n	->%s' % (conn_string)
   
   # get a connection, if a connect cannot be made an exception will be raised here
   conn = psycopg2.connect(conn_string)
   
   # conn.cursor will return a cursor object, you can use this cursor to perform queries
   cursor = conn.cursor()
   print 'Connected!\n'
   
   cursor.execute('INSERT INTO incidents (incident, reported, occurred, comments, disposition, \
                   ucpd_num, address, latlng) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                  ('Theft', datetime.datetime(2015,6,10,6,0), 'This happened at the witching hour.', 'This was the evil action of a very bad person.',
                   'Open', '3#HE63', '5600 S Ellis Ave', ppygis.Point(34,-116))
                 ) 
   print 'Inserted!\n'
    
   cursor.execute('SELECT * FROM incidents')
   records = cursor.fetchall()
   pprint.pprint(records)
   
   conn.commit()
 
if __name__ == '__main__':
   main()
