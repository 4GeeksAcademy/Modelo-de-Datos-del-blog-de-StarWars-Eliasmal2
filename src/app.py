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
from models import Character, Planet, db, User
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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
def get_user():
    stmt=select(User)
    all_users = db.session.execute(stmt).scalars().all()
    all_users = list(map(lambda item: item.serialize(), all_users))

    return jsonify(all_users), 200

@app.route('/planets', methods=['GET'])
def get_planet():
    stmt=select(Planet)
    all_users = db.session.execute(stmt).scalars().all()
    all_users = list(map(lambda item: item.serialize(), all_users))

    return jsonify(all_users), 200

@app.route('/character', methods=['GET'])
def get_character():
    stmt=select(Character)
    all_users = db.session.execute(stmt).scalars().all()
    all_users = list(map(lambda item: item.serialize(), all_users))

    return jsonify(all_users), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorite(user_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404
    
    array_planet = []
    for planet in user.fav_planet:
        array_planet.append(planet.serialize())
    
    array_character = []
    for character in user.fav_character:
        array_character.append(character.serialize())


    return {'user_id': user_id, "favorites":{"planets": array_planet, 'character': array_character}}, 200

@app.route('/users/<int:user_id>/favorites', methods=['DELETE'])
def delete_favorite(user_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404
    
    data = request.get_json()
    planet_id = data.get('planet_id')
    character_id = data.get('character_id')

    if planet_id is not None:
        planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
        if planet is None:
            return { 'message': f"El planeta con el id {planet_id} no existe"},404
        user.fav_planet.remove(planet)
    
    if character_id is not None:
        character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
        if character is None:
            return { 'message': f"El personaje con el id {character_id} no existe"},404
        user.fav_character.remove(character)

    db.session.commit()

    return {'user_id': user_id, "favorites":{"planets": [], 'character': []}}, 200

@app.route('/users/<int:user_id>/favorites', methods=['PUT'])
def put_favorite(user_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404
    
    data = request.get_json()
    planet_id = data.get('planet_id')
    character_id = data.get('character_id')

    if planet_id is not None:
        planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
        if planet is None:
            return { 'message': f"El planeta con el id {planet_id} no existe"},404
        user.fav_planet.append(planet)
    
    if character_id is not None:
        character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
        if character is None:
            return { 'message': f"El personaje con el id {character_id} no existe"},404
        user.fav_character.append(character)

    db.session.commit()

    return {'user_id': user_id, "favorites":{"planets": [], 'character': []}}, 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return { 'message': f"El planeta con el id {planet_id} no existe"},404

    return jsonify(planet.serialize()), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character_by_id(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return { 'message': f"El personaje con el id {character_id} no existe"},404

    return jsonify(character.serialize()), 200

@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def post_planet(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return { 'message': f"El planeta con el id {planet_id} no existe"},404

    data = request.get_json()
    user_id = data.get('user_id')
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404

    user.fav_planet.append(planet)
    db.session.commit()

    return jsonify(user.serialize()), 200

@app.route('/favorites/character/<int:character_id>', methods=['POST'])
def post_character(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return { 'message': f"El personaje con el id {character_id} no existe"},404

    data = request.get_json()
    user_id = data.get('user_id')
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404

    user.fav_character.append(character)
    db.session.commit()

    return jsonify(user.serialize()), 200

@app.route('/planets/<planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return { 'message': f"El planeta con el id {planet_id} no existe"},404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({ 'message': f"El planeta con el id {planet_id} ha sido eliminado"}), 200

@app.route('/character/<character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return { 'message': f"El personaje con el id {character_id} no existe"},404

    db.session.delete(character)
    db.session.commit()

    return jsonify({ 'message': f"El personaje con el id {character_id} ha sido eliminado"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
