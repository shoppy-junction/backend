import flask
from flask import request
import pandas as pd
import sqlite3
import csv
from io import StringIO

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET"])
def home():
    return "<h1>Bluetooth location API</h1>"

@app.route('/locationdata', methods=['POST'])
def post_location():
    data = request.get_data(as_text=True)
    print(type(data))
    df = pd.read_csv(StringIO(data))
    df.columns = ['beacon_id', 'rssi', 'timestamp', 'userid']
    data = df

    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    for i, row in data.iterrows():
        c.execute("INSERT into proximity VALUES (?,?,?,?);", (int(row.timestamp), int(row.userid), int(row.beacon_id), int(row.rssi)))
    conn.commit()
    conn.close()
    return str(data)

@app.route('/locationdata', methods=['GET'])
def get_location():
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    userid = request.args.get('userid')
    if userid is None:
        res = c.execute("SELECT * FROM proximity;").fetchall()
    else:
        res = c.execute("SELECT * FROM proximity WHERE userid = ?;", (userid,)).fetchall()
    conn.commit()
    conn.close()
    return str(res)

@app.route('/createloctable', methods=['GET'])
def create_location_table():
    """
    get endpoint
    params (optional): 
    - userid: userid to return results for
    """
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE proximity (timestamp int, userid int, beacon_id int, rssi int);")
    except:
        c.execute("DROP TABLE proximity;")
        c.execute("CREATE TABLE proximity (timestamp int, userid int, beacon_id int, rssi int);")
    conn.commit()
    conn.close()
    return "table created"

app.run(host='130.233.87.184')
