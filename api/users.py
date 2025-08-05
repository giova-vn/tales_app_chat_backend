from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import datetime

users_bp = Blueprint("users", __name__)
db = None
bcrypt = Bcrypt()

def set_db_connection(mongoDB):
    global db
    db = mongoDB

def json_response(data, status_code = 200):
    return jsonify(data), status_code


@users_bp.route("/register", methods=["POST"])
def register_user():
    if db is None:
        return json_response({"error": "Database not initialized"}, 500)
        
    users_collection = db.users

    data = request.get_json()
    username = data.get("username")
    raw_password = data.get("password")

    if not username or not raw_password:
        return json_response({"error": "username and password are required"}, 400)
    
    if users_collection.find_one({"username": username}):
        return json_response({"error": "username already exists"}, 409)
    
    hashed_password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    user_data = {
        "username": username,
        "password": hashed_password,   
        "created": datetime.datetime.now()
    } 
    users_collection.insert_one(user_data)
    
    return json_response({"successful": "User registered successfully"}, 201)

@users_bp.route("/login", methods=["POST"])
def login_user(): 
    if db is None:
        return json_response({"error": "Database not initialized"}, 500)
    
    user_collection = db.users

    data = request.get_json()
    username = data.get("username")
    raw_password = data.get("password")

    if not username or not raw_password:
        return json_response({"error": "username and password required"}, 400)
    
    user = user_collection.find_one({"username": username})

    if user and bcrypt.check_password_hash(user['password'], raw_password):
        return json_response({"successful": "user login successful", "username": username}, 200)
    else:
        return json_response({"error": "user not found"}, 401)