from flask import Flask, abort
from flask_restful import Resource, Api
import psycopg2, psycopg2.extras, ppygis
import db_conn
import json
from bson import json_util

app = Flask(__name__)
api = Api(app)

class UCPD(Resource):
   def get(self, dataset_name):
      conn_string = db_conn.conn_string
      try:
         conn = psycopg2.connect(conn_string)
      except:
         abort(500)
      cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
      query_string = 'SELECT * FROM ' + dataset_name

      cursor.execute(query_string)
      records = cursor.fetchall()
      json_rec = []
      for r in records:
         t = {}
         for key in r:
            if key == 'reported':
               t['reported'] = str(r['reported'])
            else:
               t[key] = r[key]
         json_rec.append(t)
      return json_rec

api.add_resource(UCPD, '/api/detail/<dataset_name>')

@app.route('/')
def root():
   return 'We out here'

if __name__ == '__main__':
    app.run(debug=True)
