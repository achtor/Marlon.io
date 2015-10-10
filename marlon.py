from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class UCPD(Resource):
    def get(self):
        return {'ucpd': 'data'}

api.add_resource(UCPD, '/')

if __name__ == '__main__':
    app.run(debug=True)
