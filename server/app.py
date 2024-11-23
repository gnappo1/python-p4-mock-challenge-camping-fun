#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class CamperById(Resource):
    def patch(self, id):
        try:
            #! grab the camper by the id given
            camper = Camper.query.get_or_404(id)
            #! grab the data
            data = request.get_json()
            # TODO at some point set up app-level validations (Marshmallow, reqparse)
            #! we need to tell camper that some attrs are dated, and we need to reset them -> @validates will listen
            camper.name = data.get("name", camper.name)
            camper.age = data.get("age", camper.age)
            #! time to commit!
            db.session.commit()
            return camper.to_dict(), 202
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": "Camper not found"}

api.add_resource(CamperById, "/campers/<int:id>")


class Campers(Resource):
    def post(self):
        try:
            data = request.json
            #! instantiate a new object to then have the session track it and fire a INSERT INTO statement
            camper = Camper(name=data.get("name"), age=data.get("age"))
            # camper = Camper(**data)
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 201)
        except Exception as e:
            return {"error": str(e)}, 400

api.add_resource(Campers, "/campers")

class AllSignups(Resource):
    def post(self):
        try:
            data = request.json
            signup = Signup(**data)
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 201)
        except Exception as e:
            return {"error": str(e)}, 400

api.add_resource(AllSignups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
