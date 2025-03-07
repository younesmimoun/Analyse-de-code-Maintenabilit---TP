from flask import Flask, jsonify
import json
import datetime
import tempfile
import os

app = Flask(__name__)

def read_water():
    # Auto-create water.json if it doesn't exist
    if not os.path.exists('water.json'):
        with open('water.json', 'w') as f:
            json.dump({"water": 0}, f)

    with open('water.json', 'r') as f:
        return json.load(f)

def read_water_by_user(userId):
    filename = f'water{userId}.json'
    # Auto-create water<userId>.json if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({"water": 0}, f)

    with open(filename, 'r') as f:
        return json.load(f)

def save_water(water):
    with open('water.json', 'w') as f:
        json.dump(water, f)

def save_water_by_user(water, userId):
    with open(f'water{userId}.json', 'w') as f:
        json.dump(water, f)

@app.route('/add_water', methods=['GET'])
def add_water():
    water_data = read_water()
    water_data["water"] += 10

    if "adding" not in water_data:
        water_data["adding"] = []

    water_data["adding"].append({
        'added_at': str(datetime.datetime.now()),
        'quantity': 10
    })

    save_water(water_data)
    return jsonify(water_data)

@app.route('/water', methods=['GET'])
def water():
    # Just for logging
    filename = tempfile.mktemp()
    with open(filename, 'a') as logfile:
        logfile.write(f'getting water at {datetime.datetime.now()}\n')

    water_data = read_water()
    return jsonify(water_data)

@app.route('/add_water/<user_id>', methods=['GET'])
def add_water_user(user_id):
    water_data = read_water_by_user(userId=user_id)
    water_data["water"] += 10
    save_water_by_user(water_data, user_id)
    return jsonify(water_data)

@app.route('/add_alert/<user_id>', methods=['GET'])
def check_alert(user_id):
    water_data = read_water_by_user(userId=user_id)
    if water_data["water"] < 10:
        return 'alert missing water'
    else:
        return 'everything is ok'

# Exclude from coverage because tests won't call app.run()
if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True)
