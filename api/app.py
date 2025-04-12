# api/app.py
from flask import Flask, request, jsonify
from db.database import add_player, get_player_name

app = Flask(__name__)

@app.route('/save_name', methods=['POST'])
def save_name():
    name = request.json['name']
    add_player(name)
    return jsonify({'status': 'success'})

@app.route('/get_name', methods=['GET'])
def get_name():
    name = get_player_name()
    return jsonify({'name': name})

if __name__ == '__main__':
    app.run(debug=True)