from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS, cross_origin
from websocket import create_connection
import json
import requests
import datetime
import time
import calendar
# import MySQLdb

import pymysql.cursors

host = '198.245.75.250'
database = 'demoexch_exchange'
username = 'demoexch_abhi'
password = 'E,7{hb0[ggXs'
# end postgres

app = Flask(__name__)
CORS(app)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)


def sql_connect(query):
    db = pymysql.connect(host=host, user=username, passwd=password, db=database, cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()
    cursor.excecute(query)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows


@app.route('/config')
def config():
    results = {}

    results["supports_search"] = True
    results["supports_group_request"] = False
    results["supported_resolutions"] = ["1", "5", "15", "30", "60", "240", "1D"]
    results["supports_marks"] = False
    results["supports_time"] = True

    return jsonify(results)


@app.route('/symbols')
def symbols():
    symbol = request.args.get('symbol')

    base, quote = symbol.split('_')
    query = "select decimal_places from ci_apivalues where symbol = '" + base + quote + "';"
    rows = sql_connect(query)
    base_precision = 10 ** int(rows[0])

    results = {}
    results["name"] = symbol
    results["ticker"] = symbol
    results["description"] = base + "_" + quote
    results["type"] = ""
    results["session"] = "24x7"
    results["exchange"] = ""
    results["listed_exchange"] = ""
    results["timezone"] = "Asia/Kolkata"
    results["minmov"] = 1
    results["pricescale"] = base_precision
    results["minmove2"] = 0
    results["fractional"] = False
    results["has_intraday"] = True
    results["supported_resolutions"] = ["1", "5", "15", "30", "60", "240", "1D"]
    results["intraday_multipliers"] = ""
    results["has_seconds"] = False
    results["seconds_multipliers"] = ""
    results["has_daily"] = True
    results["has_weekly_and_monthly"] = False
    results["has_empty_bars"] = True
    results["force_session_rebuild"] = ""
    results["has_no_volume"] = False
    results["volume_precision"] = ""
    results["data_status"] = ""
    results["expired"] = ""
    results["expiration_date"] = ""
    results["sector"] = ""
    results["industry"] = ""
    results["currency_code"] = ""

    return jsonify(results)


@app.route('/search')
def search():
    query = request.args.get('query')
    type = request.args.get('type')
    exchange = request.args.get('exchange')
    limit = request.args.get('limit')

    final = []

    query = "SELECT distinct(symbol), baseAsset, quoteAsset FROM ci_apivalues WHERE symbol LIKE '%" + query + "%';"

    rows = sql_connect(query)

    for r in rows:
        results = {}
        # print w
        base = r[1]
        quote = r[2]

        results["symbol"] = base + "_" + quote

        results["full_name"] = r[0]
        results["description"] = r[0]
        results["exchange"] = "DemoExchange"
        results["ticker"] = base + "_" + quote
        results["type"] = ""
        final.append(results)

    return jsonify(final)


def get_data(symbol='XRPBTC'):
    res = requests.get('http://demoexchange.tk/api/getgraphdata/' + str(symbol))

    return json.loads(res.text)


@app.route('/history')
def history():
    symbol = request.args.get('symbol')
    from_ = request.args.get('from')
    to = request.args.get('to')
    resolution = request.args.get('resolution')

    left = datetime.datetime.fromtimestamp(int(from_)).strftime('%Y-%m-%d %H:%M:%S')
    right = datetime.datetime.fromtimestamp(int(to)).strftime('%Y-%m-%d %H:%M:%S')

    query = "SELECT close, open, high, low, volume, TimeStamp FROM ci_apivalues where symbol = '" + \
            str(symbol.replace('_')) + "' TimeStamp between '" + left + "' and '" + right + "';"

    rows = sql_connect(query)
    c = []
    o = []
    h = []
    l = []
    v = []
    t = []
    for r in rows:
        date = r[5]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        ts = calendar.timegm(date.utctimetuple())

        c.append(float(r[0]))
        o.append(float(r[1]))
        h.append(float(r[2]))
        l.append(float(r[3]))
        v.append(float(r[4]))
        t.append(ts)

    results = {}
    results["s"] = "ok"
    results["t"] = t
    results["c"] = c
    results["o"] = o
    results["h"] = h
    results["l"] = l
    results["v"] = v

    return jsonify(results)


@app.route('/time')
def time():
    date = datetime.datetime.now()

    # date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    return jsonify(str(calendar.timegm(date.utctimetuple())))

# print(time1())
