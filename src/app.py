"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    serialized_planets = list(
        map(lambda p: {'id': p.id, 'name': p.name}, planets))
    return jsonify({"msg": "Completed", "planets": serialized_planets}), 200


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    serialized_people = list(
        map(lambda p: {'id': p.id, 'name': p.name}, people))
    return jsonify({"msg": "Completed", "people": serialized_people}), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    serialized_users = list(
        map(lambda u: {'id': u.id, 'email': u.email}, users))
    return jsonify({"msg": "Completed", "users": serialized_users}), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    serialized_favorites = list(
        map(lambda f: {'planet_id': f.planet_id, 'people_id': f.people_id}, favorites))
    return jsonify({"msg": "Completed", "favorites": serialized_favorites}), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    if person:
        serialized_person = {'id': person.id, 'name': person.name}
        return jsonify({"msg": "Completed", "person": serialized_person}), 200
    else:
        return jsonify({"error": "Persona no encontrada"}), 404


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        serialized_planet = {'id': planet.id, 'name': planet.name}
        return jsonify({"msg": "Completed", "planet": serialized_planet}), 200
    else:
        return jsonify({"error": "Planeta no encontrado"}), 404


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Planeta favorito agregado'})


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Personaje favorito agregado'})


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': 'Planeta eliminado con exito'})
    else:
        return jsonify({'error': 'Planeta no encontrado'}), 404


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1
    favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': 'Personaje borrado con exito'})
    else:
        return jsonify({'error': 'Personaje no se encontro'}), 404


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
