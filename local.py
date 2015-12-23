import scrape, update, psycopg2, datetime, db_conn

# function should check last date for each table, then update with those rows
def updateMarlon(table):
   try:
      # retrieve last date for table
      conn_string = db_conn.conn_string
      conn = psycopg2.connect(conn_string)
      times = 'time'
      if table == 'incidents':
         times = 'reported'

      cursor = conn.cursor()
      query = 'SELECT MAX(' + times + ') FROM ' + table
      cursor.execute(query)
      result = cursor.fetchone()[0] + datetime.timedelta(days = 1)
      date = result.strftime('%m%%2F%d%%2F%Y')

      # get rows to put in
      rows = scrape.fullScrape(date, table)
      for item in rows:
         print item

      # update
      # update.updateTable(table, rows)
   except:
      # tell celery something went wrong
      raise Exception

"""
rows = scrape.fullScrape('09%2F01%2F2015', 'incidents')
update.updateTable('incidents', rows)

rows = scrape.fullScrape('09%2F01%2F2015', 'traffic_stops')
update.updateTable('traffic_stops', rows)

rows = scrape.fullScrape('09%2F01%2F2015', 'field_interviews')
update.updateTable('field_interviews', rows)
"""
