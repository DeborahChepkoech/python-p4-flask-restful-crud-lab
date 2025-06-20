#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):
    def get(self):
        plants = [plant.to_dict(rules=('-id',)) for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        try:
            data = request.get_json()

            new_plant = Plant(
                name=data.get('name'),
                image=data.get('image'),
                price=data.get('price'),
                is_in_stock=data.get('is_in_stock', True) 
            )

            db.session.add(new_plant)
            db.session.commit()

            return make_response(new_plant.to_dict(), 201)
        except (ValueError, KeyError) as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = db.session.get(Plant, id)

        if plant:
            return make_response(jsonify(plant.to_dict()), 200)
        
        return make_response(jsonify({"error": f"Plant with id {id} not found"}), 404)

    def patch(self, id):
        plant = db.session.get(Plant, id)

        if not plant:
            return make_response(jsonify({"error": f"Plant with id {id} not found"}), 404)

        try:
            data = request.get_json()
            for key, value in data.items():
                setattr(plant, key, value)
            
            db.session.commit()
            return make_response(jsonify(plant.to_dict()), 200)
        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)


    def delete(self, id):
        plant = db.session.get(Plant, id)

        if plant:
            db.session.delete(plant)
            db.session.commit()
            return make_response('', 204)
        return make_response(jsonify({"error": f"Plant with id {id} not found"}), 404)


api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
