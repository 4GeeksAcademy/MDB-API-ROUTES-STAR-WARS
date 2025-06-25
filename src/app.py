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
from models import db, User, Characters, Planets, Starship


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

#-----------------------------------Routes for Characters-----------------------------------
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characthers = Characters.query.all()
    return jsonify([characters.serialize() for characters in characthers])

#-----------------------------------Routes for Characters by ID-----------------------------------
@app.route('/characters/>int:character_id', methods=['GET'])
def get_character_by_id(character_id):
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(character.serialize()), 200

#-----------------------------------Routes for Planets-----------------------------------
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    return jsonify([planets.serialize() for planets in planets]), 200

#-----------------------------------Routes for Planets by ID-----------------------------------
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

#-----------------------------------Routes for Starships-----------------------------------
@app.route('/starships', methods=['GET'])
def get_all_starships():
    starships = Starship.query.all()
    return jsonify([starship.serialize() for starship in starships]), 200

#-----------------------------------Routes for Starships by ID-----------------------------------
@app.route('/starships/<int:starship_id>', methods=['GET'])
def get_starship_by_id(starship_id):
    starship = Starship.query.get(starship_id)
    if not starship:
        return jsonify({"msg": "Starship not found"}), 404
    return jsonify(starship.serialize()), 200

#-----------------------------------Routes for User-----------------------------------
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

#-----------------------------------Routes for User Favorites List-----------------------------------
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    favorites = {
    "characters": [c.serialize() for c in user.favorites_characters.all()],
    "planets": [p.serialize() for p in user.favorites_planets.all()],
    "starships": [s.serialize() for s in user.starships_favorites.all()]
}
    return jsonify(favorites), 200
#-----------------------------------Routes for Adding User-----------------------------------
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    required_fields = ('email', 'password', 'first_name', 'last_name')
    if not data or not all(field in data for field in required_fields):
        return jsonify({'msg': 'All fields are required'}), 400
    new_user = User(email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

#------------------------------------Routes for Adding Characters-----------------------------------------
@app.route('/characters', methods=['POST'])
def add_character():
    data = request.json
    required_fields = ('name','species' 'description', 'homeworld')
    if not data or not all(field in data for field in required_fields):
        return jsonify({'msg': 'All fields are required'}), 400
    new_character = Characters(name=data['name'],
                              species=data['species'],
                              description=data.get('description'),
                              homeworld=data.get('homeworld'))
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201
#------------------------------------Routes for Adding Planets-----------------------------------------
@app.route('/planets', methods=['POST'])
def add_planet():
    data = request.json
    required_fields = ('name', 'climate', 'terrain', 'population')
    if not data or not all(field in data for field in required_fields):
        return jsonify({'msg': 'All fields are required'}), 400
    new_planet = Planets(name=data['name'],
                        climate=data['climate'],
                        terrain=data['terrain'],
                        population=data['population'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201
#------------------------------------Routes for Adding Starships-----------------------------------------
@app.route('/starships', methods=['POST'])
def add_starship(): 
    data = request.json
    required_fields = ('name', 'model', 'starship_class')
    if not data or not all(field in data for field in required_fields):
        return jsonify({'msg': 'All fields are required'}), 400
    new_starship = Starship(name=data['name'],
                            model=data['model'],
                            starship_class=data['starship_class'])
    db.session.add(new_starship)
    db.session.commit()
    return jsonify(new_starship.serialize()), 201
#-----------------------------------Routes for Adding Favorites Planets-----------------------------------
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'msg': 'User id is required'}), 400
    
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)
    if not user or not planet:
        return jsonify({'msg': 'User or Planet not found'}), 404
    
    if planet in user.favorites_planets:
        return jsonify({'msg': 'Planet already in favorites'}), 400
    user.favorites_planets.append(planet)

    db.session.commit()
    return jsonify({'msg': 'Planet added to favorites'}), 201

#-----------------------------------Routes for Adding Favorites Characters-----------------------------------
@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_characther(character_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'msg': 'User id es required'}), 400
    
    user = User.query.get(user_id)
    character = Characters.query.get(character_id)
    if not user or not character:
        return jsonify({'msg': 'User or Character not found'}), 404
    
    if character in user.favorites_characters:
        return jsonify({'msg': 'Character already in favorites'}), 400
    user.favorites_characters.append(character)

    db.session.commit()
    return jsonify({'msg': 'Character added to favorites'}), 201

#-----------------------------------Routes for Adding Favorites Starships-----------------------------------
@app.route('/favorite/starship/<int:starship_id>', methods=['POST'])
def add_favorite_starship(starship_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'msg': 'User id is required'}), 400
    
    user = User.query.get(user_id)
    starship = Starship.query.get(starship_id)
    if not user or not starship:
        return jsonify({'msg': 'User or Starship nor found'}), 404
    
    if starship in user.starships_favorites:
        return jsonify({'msg': 'Starship already in favorites'}), 400
    user.starships_favorites.append(starship)

    db.session.commit()
    return jsonify({'msg': 'Starship added to favorites'}), 201

#-----------------------------------Routes for Deleting Favorites Planets-----------------------------------
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'msg': 'User id is required'}), 400
    
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)
    if not user or not planet:
        return jsonify({'msg': 'User or Planet not found'}), 404
    
    if planet not in user.favorites_planets:
        return jsonify({'msg': 'Planet not in favorites'}), 400
    user.favorites_planets.remove(planet)

    db.session.commit()
    return jsonify({'msg': 'Planet removed from favorites'}), 200

#-----------------------------------Routes for Deleting Favorites Characters-----------------------------------
@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'msg': 'User id is required'}), 400
    
    user = User.query.get(user_id)
    character = Characters.query.get(character_id)
    if not user or not character:
        return jsonify({'msg': 'User or Character not found'}), 404
    
    if character not in user.favorites_characters:
        return jsonify({'msg': 'Character not in favorites'}), 400
    user.favorites_characters.remove(character)

    db.session.commit()
    return jsonify({'msg': 'Character removed from favorites'}), 200

#-----------------------------------Routes for Deleting Favorites Starships-----------------------------------
@app.route('/favorite/starship/<int:starship_id>', methods=['DELETE'])
def delete_favorite_starship(starship_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'msg': 'User id is required'}), 400
    
    user = User.query.get(user_id)
    starship = Starship.query.get(starship_id)
    if not user or not starship:
        return jsonify({'msg': 'User or Starship not found'}), 404
    
    if starship not in user.starships_favorites:
        return jsonify({'msg': 'Starship not in favorites'}), 400
    user.starships_favorites.remove(starship)

    db.session.commit()
    return jsonify({'msg': 'Starship removed from favorites'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


