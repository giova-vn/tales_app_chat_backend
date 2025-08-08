from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
import datetime

chats_bp = Blueprint("chats", __name__)
db = None

def set_db_connection(mongoDB):
    global db
    db = mongoDB

def json_response(data, status_code = 200):
    return jsonify(data), status_code

def parse_message_date_string(date_string):
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


@chats_bp.route("/message/send", methods=["POST"])
def send_message():
    if db is None:
        return json_response({"Error": "Error with database initialization"}, 500)
    
    chats_collection = db.chats

    data = request.get_json()
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    # validations 
    if (not sender_id or not receiver_id or not content):
        return json_response({"Error": "SenderID, ReceiverID and content are required"}, 400)

    try:
        sender_id = ObjectId(sender_id)
        receiver_id = ObjectId(receiver_id)
    except ValueError:
        return json_response({"Error": "Sender and receiver ID must be valid ObjectsID"}, 400)
    
    # finding a conversartion between these users
    conversation = chats_collection.find_one({
    "$or": [
        {"user_id1": sender_id, "user_id2": receiver_id},
        {"user_id1": receiver_id, "user_id2": sender_id} 
        ]
    })

    message_data = {
        "sender": sender_id,
        "message_date": str(datetime.datetime.now()), 
        "message_content": content,
    }

    if conversation:
        chats_collection.update_one(
            {"_id": conversation["_id"]},
            {"$push": {"messages": message_data}}
            )
        return json_response({"Successful": "Message sent"}, 201)
    
    else:
        new_conversation = {
            "user_id1": sender_id,
            "user_id2": receiver_id,
            "messages": [message_data]
        }
        chats_collection.insert_one(new_conversation)
        return json_response({"Successful": "Conversation created. Message sent"}, 201)

@chats_bp.route("/message/history", methods=["GET"])
def get_messages():
    if db is None:
        return json_response({"Error": "Error with database initialization"}, 500)
    
    chats_collection = db.chats

    user_id1_param = request.args.get("user_id1")
    user_id2_param = request.args.get("user_id2")

    if (not user_id1_param or not user_id2_param):
        return json_response({"Error": "user_id for both users are required"}, 400)

    try:
        user_id1 = ObjectId(user_id1_param)
        user_id2 = ObjectId(user_id2_param)
    except ValueError:
        return json_response({"Error": "user_id1 and user_id2 must be valid ObjectsID"}, 400)

    conversation = chats_collection.find_one({
        "$or": [
            {"user_id1": user_id1, "user_id2": user_id2},
            {"user_id1": user_id2, "user_id2": user_id1}
        ]
    })

    if not conversation:
        return json_response({"message": "No chat history found between these users."}, 200)

    chat_history_raw = conversation.get("messages", [])
    chat_history_raw.sort(key=lambda x: parse_message_date_string(x.get("message_date", "")) or datetime.datetime.min)

    chat_history_formatted = []
    for message in chat_history_raw:
        formatted_message = {
            "message_content": message.get("message_content"),
            "sender": str(message.get("sender")), 
            "message_date": message.get("message_date")
        }
        chat_history_formatted.append(formatted_message)

    return json_response({"successful": "chat history retrieved", "messages": chat_history_formatted}, 200)

@chats_bp.route("/chats", methods=["GET"])
def get_chats():
    if db is None:
        return json_response({"Error": "Error with database initialization"}, 500)
    
    chats_collection = db.chats
    users_collection = db.users
    user_id_param = request.args.get("user_id")

    if not user_id_param:
        return json_response({"Error": "user_id is required"}, 400)
    
    try:
        user_id = ObjectId(user_id_param)
    except ValueError:
        return json_response({"Error": "invalid user_id"}, 400)
    
    user_chats_available = chats_collection.find({
        "$or": [
            {"user_id1": user_id},
            {"user_id2": user_id}
        ]
    })

    chats_list = []

    for chat in user_chats_available:
        if chat["user_id1"] == user_id:
            other_user_id = chat["user_id2"]
        elif chat["user_id2"] == user_id:
            other_user_id = chat["user_id1"] 

        other_user = users_collection.find_one({"_id": other_user_id})
        last_message = chat["messages"][-1]

        chat_info = {
            "other_user_id": str(other_user_id),
            "other_username": other_user["username"],
            "last_message": last_message["message_content"]
        }

        chats_list.append(chat_info)

    return json_response(chats_list, 200)
