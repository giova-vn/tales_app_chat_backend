from flask import Flask, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# import blueprints 


# MongoDB connection
app.config["MONGO_URI"] = "mongodb+srv://giovannipe204:qfc3XFy3QVfGr05G@chatappdb.dpfvwnv.mongodb.net/chat_app_db" 

mongodb_client = PyMongo(app)
db = mongodb_client.db 

@app.route('/')
def index():     
    return "Server is running."

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)