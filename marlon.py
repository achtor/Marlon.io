from flask import Flask, abort, render_template
from flask_restful import Resource, Api, reqparse
import psycopg2, psycopg2.extras, ppygis
import db_conn
import json, datetime, time
from bson import json_util

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('address', type=str, help='Search address string of location occurred')
parser.add_argument('disposition', type=str, help='Look up records with a certain disposition')
parser.add_argument('comments', type=str, help='Search comments of incident report')
parser.add_argument('incident', type=str, help='Search incident description string')
parser.add_argument('ucpd_num', type=str, help='Look up a specific case number')
parser.add_argument('race', type=str, help='Look up records involving individuals of a certain race')
parser.add_argument('gender', type=str, help='Look up records involving individuals of a certain gender')
parser.add_argument('reason', type=str, help='Search text of reason provided')
parser.add_argument('init', type=str, help='Search text of reason for initiation of field interview')
parser.add_argument('search', type=int, help='Restrict to field interviews with/without searches (1/0)')
parser.add_argument('cit_viol', type=str, help='Search text of citations/violations given for traffic stop')
parser.add_argument('idot', type=str, help='Search text of IDOT classification of traffic stop')

parser.add_argument('time1', type=str, help='Beginning of time (of day) range to query (inclusive). HHMMSS format. For incidents, this is time reported.')
parser.add_argument('time2', type=str, help='End of time (of day) range to query (exclusive). HHMMSS format. For incidents, this is time reported.')
parser.add_argument('date1', type=str, help='Beginning of date range to query (inclusive). YYYYMMDD format. For incidents, this is date reported.')
parser.add_argument('date2', type=str, help='End of date range to query (exclusive). YYYYMMDD format. For incidents, this is date reported.')

parser.add_argument('geom', type=str, help='Geometric boundaries to find the location in.')

class UCPD(Resource):
   def get(self, dataset_name):
      if not dataset_name in ['field_interviews','traffic_stops','incidents']:
         return {'error': 'invalid dataset'}

      args = parser.parse_args()

      conn_string = db_conn.conn_string
      try:
         conn = psycopg2.connect(conn_string)
      except:
         abort(500)
      cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
      query_string = 'SELECT *, ST_X(latlng), ST_Y(latlng) FROM ' + dataset_name
      
      where_args = []
      args = parser.parse_args()
      if args['address']:
         where_args = where_args + [cursor.mogrify( 'address ILIKE %s',('%' + args['address'] + '%',))] 
      if args['disposition']:
         where_args = where_args + [cursor.mogrify( 'LOWER(disposition) =  LOWER(%s)',(args['disposition'],))]
      if args['geom']:
         where_args = where_args + [cursor.mogrify( 'ST_CONTAINS(%s, latlng)', (ppygis.Polygon(args['geom'],)))]
      if dataset_name == 'incidents':
         if args['comments']:
            where_args = where_args + [cursor.mogrify( 'comments ILIKE %s',('%' + args['comments'] + '%',))]
         if args['incident']:
            where_args = where_args + [cursor.mogrify( 'incident ILIKE %s',('%' + args['incident'] + '%',))]
         if args['ucpd_num']:
            where_args = where_args + [cursor.mogrify( 'ucpd_num = %s', (args['ucpd_num'],))]
         if args['time1'] and args['time2']:
            time1 = time.strftime('%H:%M:%S', time.strptime(args['time1'], '%H%M%S')) 
            time2 = time.strftime('%H:%M:%S', time.strptime(args['time2'], '%H%M%S'))
            where_args = where_args + [cursor.mogrify( 'reported::time >= %s AND reported::time < %s', (time1, time2))]
         if args['date1'] and args['date2']:
            date1 = time.strftime('%Y-%m-%d', time.strptime(args['date1'], '%Y%m%d')) 
            date2 = time.strftime('%Y-%m-%d', time.strptime(args['date2'], '%Y%m%d'))
            where_args = where_args + [cursor.mogrify( 'reported::date >= %s AND reported::date < %s', (date1, date2))]
      else:
         if args['race']:
            where_args = where_args + [cursor.mogrify( 'LOWER(race) =  LOWER(%s)',(args['race'],))]
         if args['gender']:
            where_args = where_args + [cursor.mogrify( 'LOWER(gender) =  LOWER(%s)',(args['gender'],))]
         if args['reason']:
            where_args = where_args + [cursor.mogrify( 'reason ILIKE %s',('%' + args['reason'] + '%',))]
         if args['time1'] and args['time2']:
            time1 = time.strftime('%H:%M:%S', time.strptime(args['time1'], '%H%M%S')) 
            time2 = time.strftime('%H:%M:%S', time.strptime(args['time2'], '%H%M%S'))
            where_args = where_args + [cursor.mogrify( 'time::time >= %s AND time::time < %s', (time1, time2))]
         if args['date1'] and args['date2']:
            date1 = time.strftime('%Y-%m-%d', time.strptime(args['date1'], '%Y%m%d')) 
            date2 = time.strftime('%Y-%m-%d', time.strptime(args['date2'], '%Y%m%d'))
            where_args = where_args + [cursor.mogrify( 'time::date >= %s AND time::date < %s', (date1, date2))] 
         if dataset_name == 'field_interviews':
            if args['init']:
               where_args = where_args + [cursor.mogrify( 'init ILIKE %s',('%' + args['init'] + '%',))]
            if args['search'] == 1:
               where_args = where_args + ['search']
            if args['search'] == 0:
               where_args = where_args + ['NOT search']      
         elif dataset_name == 'traffic_stops':
            if args['cit_viol']:
               where_args = where_args + [cursor.mogrify( 'cit_viol ILIKE %s',('%' + args['cit_viol'] + '%',))]   
            if args['idot']:
               where_args = where_args + [cursor.mogrify( 'idot ILIKE %s',('%' + args['idot'] + '%',))]
      num_args = len(where_args)
      if num_args > 0:
         query_string = query_string + ' WHERE ' + ' AND '.join(where_args)

      cursor.execute(query_string)
      records = cursor.fetchall()
      for r in records:
         for key in r:
            if type(r[key]) is datetime.datetime:
               r[key] = r[key].strftime("%m/%d/%y %I:%M %p")
         r['lat'] = r['st_x']
         r['lng'] = r['st_y']
         r.pop('st_x', None)
         r.pop('st_y', None)
         r.pop('latlng', None)
      return records

api.add_resource(UCPD, '/api/detail/<dataset_name>')

@app.route('/')
def root():
   return render_template('index.html')

@app.route('/api')
def api():
   return render_template('api.html')
@app.route('/explore')
def explore():
   return render_template('explore.html')

if __name__ == '__main__':
    app.run(debug=True)
