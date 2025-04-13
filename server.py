from flask import Flask, render_template, request, jsonify
from db_utils import save_player_name

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/tracks')  
def tracks():
    return render_template('tracks.html')

@app.route('/save_name', methods=['POST'])
def save_name():
    data = request.get_json()
    name = data.get('name')
    if name:
        player_id = save_player_name(name)
        return jsonify({'status': 'success', 'id': player_id})
    return jsonify({'status': 'error', 'message': 'No name provided'})

if __name__ == '__main__':
    app.run(debug=True)
