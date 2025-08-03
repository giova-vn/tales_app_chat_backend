from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo

# import blueprints 
from api.chats import chats_bp, set_db_connection


# initizalication 
app = Flask(__name__)
CORS(app)

# mongoDB connection
app.config["MONGO_URI"] = "mongodb+srv://giovannipe204:qfc3XFy3QVfGr05G@chatappdb.dpfvwnv.mongodb.net/chat_app_db" 
mongodb_client = PyMongo(app)
db = mongodb_client.db 

set_db_connection(db)
# register bp 
app.register_blueprint(chats_bp)


# route 
@app.route('/')
def index():     
    return "Server is running."

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)