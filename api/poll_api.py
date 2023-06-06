#!/usr/bin/python3
from flask import Flask, jsonify, request, url_for, abort
from flask_cors import CORS
from datetime import datetime
import mysql.connector
import requests


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
conn = mysql.connector.connect(
        host="localhost",
        user="user",
        password="password",
        database="bincomphptest")
curr = conn.cursor()


@app.route("/parties", strict_slashes=False)
def parties():
    """ fetches all party names """

    curr.execute("SELECT partyname from party")
    party_names = [
            "LABO" if row[0] == "LABOUR" else row[0]
            for row in curr.fetchall()
    ]

    return jsonify(party_names)


@app.route("/results/pu/<pu_id>", strict_slashes=False)
def pu_result(pu_id):
    """ fetches the result for an individual polling unit """

    try:
        curr.execute("SELECT polling_unit_name FROM polling_unit WHERE uniqueid = {}".format(pu_id))
    except Exception:
        abort(404, "No unit with given Id")

    unit_name = curr.fetchone()[0]

    curr.execute("SELECT party_abbreviation, party_score FROM announced_pu_results where polling_unit_uniqueid = {}".format(pu_id))
    results = {row[0]: row[1] for row in curr.fetchall()}

    return jsonify({unit_name: results})


@app.route("/results/lga/<lga_id>", strict_slashes=False)
def lga_result(lga_id):
    """ fetches the result for an individual lga """

    # get all polling unit ids using the lga_id
    try:
        curr.execute("SELECT uniqueid FROM polling_unit WHERE lga_id = {}".format(lga_id))
    except Exception:
        abort(404, "No LGA with given Id")

    pu_ids = [row[0] for row in curr.fetchall()]

    # get the summed results using the pollling unit ids
    res = {}
    for id in pu_ids:
        response = requests.get(request.host_url.rstrip('/') + url_for('pu_result', pu_id=id))
        for name, result in response.json().items():
            res[name] = result

    total = {}
    for value in res.values():
        for name, count in value.items():
            if name in total:
                total[name] += count
            else:
                total[name] = count

    res["total"] = total

    return jsonify(res)


@app.route("/results/pu/", methods=["POST"], strict_slashes=False)
def post_pu_result():
    """ post a result to a new polling unit """

    try:
        post_data = request.get_json()
    except Exception:
        abort(404, "Not a JSON")

    time_now = datetime.now()
    ip_address = request.remote_addr
    name = post_data.get("username")
    pu_id = post_data.get("pu_id");

    del post_data["username"]
    del post_data["pu_id"]

    print(post_data)

    for party, score in post_data.items():
        query = "INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address) VALUES (%s, %s, %s, %s, %s, %s)"
        curr.execute(query, (pu_id, party, score, name, time_now, ip_address))

    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
