#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return ''

api = Api(app)
class Activities(Resource):
    def get(self):
        activities = [a.to_dict() for a in Activity.query.all()]
        return make_response(jsonify(activities), 200)
    
    # def post(self):
    #     data = request.get_json()
    #     activity = Activity(**data)
    #     db.session.add(activity)
    #     db.session.commit()
    #     return make_response(jsonify(activity.to_dict()), 201)

api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    def get(self, id):
        try:
            activity = Activity.query.get_or_404(id)
            return make_response(jsonify(activity.to_dict()), 200)
        except Exception as e:
            return make_response(jsonify({"error": "404: Activity not found"}), 404)
    
    def delete(self, id):
        activity = Activity.query.get_or_404(id)
        db.session.delete(activity)
        db.session.commit()
        return make_response(jsonify({}), 204)
    
api.add_resource(ActivityByID, '/activities/<int:id>')
class Campers(Resource):
    def get(self):
        campers = [c.to_dict(only=('id', 'name', 'age', 'signups')) for c in Camper.query.all()]
        return make_response(jsonify(campers), 200)
    
    def post(self):
        data = request.get_json()
        import ipdb; ipdb.set_trace()
        try:
            camper = Camper(**data)
            db.session.add(camper)
            db.session.commit()
            return make_response(jsonify(camper.to_dict()), 201)
        except (Exception, IntegrityError) as e:
            return make_response(jsonify({"error": str(e)}), 400)

api.add_resource(Campers, '/campers')
class CamperByID(Resource):
    def get(self, id):
        try:
            camper = Camper.query.get_or_404(id)
            return make_response(jsonify(camper.to_dict()), 200)
        except Exception as e:
            return make_response(jsonify({"error": "404: Camper not found"}), 404)
    
    # def patch(self, id):
    #     camper = Camper.query.get_or_404(id)
    #     data = request.get_json()
    #     for key, value in data.items():
    #         setattr(camper, key, value)
    #     db.session.commit()
    #     return make_response(jsonify(camper.to_dict()), 200)
    
    def delete(self, id):
        camper = Camper.query.get_or_404(id)
        db.session.delete(camper)
        db.session.commit()
        return make_response(jsonify({}), 204)

api.add_resource(CamperByID, '/campers/<int:id>')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
