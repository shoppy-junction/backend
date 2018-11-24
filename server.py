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
    df = pd.read_csv(StringIO(data))
    df.columns = ['beacon_id', 'rssi', 'userid', 'timestamp']
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
    """
    get endpoint
    params (optional): 
    - userid: userid to return results for
    """
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
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE proximity (timestamp int, userid int, beacon_id int, rssi int);")
    except:
        c.execute("DROP TABLE proximity;")
        c.execute("CREATE TABLE proximity (timestamp int, userid int, beacon_id int, rssi int);")
    conn.commit()
    conn.close()
    return "location table created"

@app.route('/createpurchasetable', methods=['GET'])
def create_purchase_table():
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE purchases (timestamp int, userid int, ean str, price str);")
    except:
        c.execute("DROP TABLE purchases;")
        c.execute("CREATE TABLE purchases (timestamp int, userid int, ean str, price str);")
    conn.commit()
    conn.close()
    return "purchases table created"


@app.route('/to_csv', methods=['GET'])
def write_to_csv():
    """
    endpoint to dump db to a csv
    params (optional): 
    - userid: userid to return results for
    - filename: file name to write to
    """
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    userid = request.args.get('userid')
    filename = request.args.get('filename')
    if userid is None:
        res = c.execute("SELECT * FROM proximity;").fetchall()
    else:
        res = c.execute("SELECT * FROM proximity WHERE userid = ?;", (userid,)).fetchall()
    conn.commit()
    conn.close()
    df = pd.DataFrame(res)
    df.columns = ['timestamp', 'userid', 'beacon_id', 'rssi']
    if filename is None:
        df.set_index('userid').to_csv('data/test_data.csv')
    else:
        df.to_csv(filename)
    return 'ok'


@app.route('/process', methods=['GET'])
def process_csv():
    filename = request.args.get('filename')
    if filename is None:
        filename = 'data/test_data.csv'
    from processing.process import process
    df = process(filename)
    df.to_csv(filename[:-4] + '_processed.csv')
    return 'ok'

@app.route('/purchase', methods=['POST'])
def post_purchase():
    data = request.get_data(as_text=True)
    df = pd.read_csv(StringIO(data))
    print(df)
    df.columns = ['timestamp', 'userid', 'ean', 'price']
    data = df
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    for i, row in data.iterrows():
        c.execute("INSERT into purchases VALUES (?,?,?,?);", (int(row.timestamp), int(row.userid), row.ean, row.price))
    conn.commit()
    conn.close()
    return str(data)

@app.route('/purchasedata', methods=['GET'])
def get_purchases():
    """
    get endpoint
    params (optional): 
    - userid: userid to return results for
    """
    conn = sqlite3.connect('beacon_data.db')
    c = conn.cursor()
    userid = request.args.get('userid')
    if userid is None:
        res = c.execute("SELECT * FROM purchases;").fetchall()
    else:
        res = c.execute("SELECT * FROM purchases WHERE userid = ?;", (userid,)).fetchall()
    conn.commit()
    conn.close()
    return str(res)


app.run(host='130.233.87.184')
