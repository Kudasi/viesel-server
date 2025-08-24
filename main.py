from flask import Flask, request, jsonify
from json import loads, dumps, dump
from random import randint


class Message:

    id : int = 0
    chat_id : int = 0
    sender: str = ""
    text: str = ""
    timestamp: int = 0

    def __init__(self, id: int, chat_id: int ,sender: str, text: str, timestamp: int):
        self.id = id
        self.chat_id = chat_id
        self.sender = sender
        self.text = text
        self.timestamp = timestamp


class Chat:

    id : int = 0
    recipients: list[int] = []

    def __init__(self, id: int, recipients: list[int]):
        self.id = id
        self.recipients = recipients

class User:

    name: str = ""
    password: str = ""
    about: str = ""
    chats: list[Chat]

    def __init__(self, name: str, password: str, about: str = ""):
        self.name = name
        self.password = password
        self.about = about
        self.chats = []

data = loads(open('server_data', 'r').read())
users = [User(**user) for user in data]

app = Flask(__name__)

def generate_token() -> str:
    token = ''.join([chr(randint(97, 122)) for _ in range(32)])
    if token in data["tokens"]:
        return generate_token()
    return token


@app.route('/login', methods=['GET'])
def login():
    user_data = loads(request.json)
    name = user_data["name"]
    password = user_data["password"]
    
    if not name or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    for user in data:
        if user['name'] == name and user['password'] == password:
            token = generate_token()
            data["tokens"][token] = name
            with open('server_data', 'w') as f:
                dump(data, f, indent=4)
            return jsonify({"token": token}), 200
        
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/register', methods=['POST'])
def register():
    new_user = loads(request.json)
    new_user["about"] = ""

    if not new_user or 'name' not in new_user or 'password' not in new_user:
        return jsonify({"error": "Login and password are required"}), 400

    # Check if user already exists
    for user in data:
        if user['name'] == new_user['name']:
            return jsonify({"error": "User already exists"}), 400

    data.append(new_user)
    token = generate_token()
    data["tokens"][token] = new_user['name']
    with open('server_data', 'w') as f:
        dump(data, f, indent=4)
    
    return jsonify({"token": token}), 200


@app.route('/get_chats', methods=['GET'])
def get_chats():
    data = loads(request.json)
    token =  data["token"]

    if token not in data["tokens"]:
        return jsonify({"error": "Invalid token"}), 401

    user_name = data["tokens"][token]
    
    return jsonify({
        "chats": data[user_name]["chats"]
    }), 200

@app.route('/get_chat_info', methods=['GET'])
def get_chat_info():
    data = loads(request.json)
    token = data["token"]

    if token not in data["tokens"]:
        return jsonify({"error": "Invalid token"}), 401
    

    chat_id = data["chat_id"]

    if chat_id not in data["users"][data["tokens"][token]]["chats"]:
        return jsonify({"error": "Chat not found"}), 404

    return jsonify({
        "chat": {}  # Placeholder for chat info
    }), 200

@app.route('/get_chat_messages', methods=['GET'])
def get_chat_messages():
    data = loads(request.json)
    token = data["token"]

    if token not in data["tokens"]:
        return jsonify({"error": "Invalid token"}), 401

    chat_id = data["chat_id"]

    if chat_id not in data["users"][data["tokens"][token]]["chats"]:
        return jsonify({"error": "Chat not found"}), 404

    messages = []
    for message in data["messages"]:
        if message["chat_id"] == chat_id:
            messages.append(message)

    return jsonify({
        "messages": messages  # Placeholder for chat messages
    }), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    data = loads(request.json)
    token = data["token"]

    if token not in data["tokens"]:
        return jsonify({"error": "Invalid token"}), 401

    chat_id = data["chat_id"]
    text = data["text"]

    if chat_id not in data["users"][data["tokens"][token]]["chats"]:
        return jsonify({"error": "Chat not found"}), 404

    if not text:
        return jsonify({"error": "Message text is required"}), 400

    message_id = randint(0, 4000000000)
    new_message = Message(message_id, chat_id, data["tokens"][token], text, 0)
    data["messages"].append(new_message)
    with open('server_data', 'w') as f:
        dump(data, f, indent=4)

@app.route("/create_chat", methods=['POST'])
def create_chat():
    data = loads(request.json)
    initiator = data["initiator"]
    recipients = data["recipients"]

    if not initiator or not recipients:
        return jsonify({"error": "Initiator and recipients are required"}), 400

    chat_id = randint(0, 4000000000)
    new_chat = Chat(chat_id, recipients)
    data['chats'].append(new_chat)
    with open('server_data', 'w') as f:
        dump(data, f, indent=4)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
