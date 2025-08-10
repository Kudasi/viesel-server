from flask import Flask, request, jsonify
from json import loads, dumps, dump
from random import randint


class Message:

    sender: str = ""
    text: str = ""
    timestamp: int = 0

    def __init__(self, sender: str, text: str, timestamp: int):
        self.sender = sender
        self.text = text
        self.timestamp = timestamp


class Chat:

    id : int = 0
    recipients: list[str] = []
    messages: list[Message] = []

    def __init__(self, id: int, recipients: list[str]):
        self.id = id
        self.recipients = recipients
        self.messages = []


data = loads(open('server_data', 'r').read())

app = Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    user_data = loads(request.json)
    name = user_data["name"]
    password = user_data["password"]
    
    if not name or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    for user in data:
        if user['name'] == name and user['password'] == password:
            return jsonify({
                "message": "Login successful",
                "name": user['name'],
                "about": user['about']
            })
        
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
    with open('server_data', 'w') as f:
        dump(data, f, indent=4)
    
    return jsonify({"message": "User registered successfully"}), 201


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
