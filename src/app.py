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
from models import db, User, Characters, Planets, starship

#Crea una API conectada a una base de datos e implemente los siguientes endpoints (muy similares a SWAPI.dev or SWAPI.tech):

#[GET] /people Listar todos los registros de people en la base de datos.
#[GET] /people/<int:people_id> Muestra la información de un solo personaje según su id.
#[GET] /planets Listar todos los registros de planets en la base de datos.
#[GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id.
#Adicionalmente, necesitamos crear los siguientes endpoints para que podamos tener usuarios y favoritos en nuestro blog:

#[GET] /users Listar todos los usuarios del blog. x
#[GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual. x
#[POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id.
#[POST] /favorite/people/<int:people_id> Añade un nuevo people favorito al usuario actual con el id = people_id.
#[DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id.
#[DELETE] /favorite/people/<int:people_id> Elimina un people favorito con el id = people_id.

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

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([users.serialize() for users in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"msg": "User id is requiered"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    favorites = {
        "people": [c.serialize() for c in user.favorites_people],
        "planets": [p.serialize() for p in user.favorites_planets],
        "starships": [s.serialize() for s in user.favorites_starships]
    }
    return jsonify(favorites), 200
    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


