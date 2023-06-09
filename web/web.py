#!/usr/bin/python3
from flask import Flask, render_template, abort
import mysql.connector
import uuid
import schedule
import time
import threading


app = Flask(__name__)
conn = mysql.connector.connect(
        host="localhost",
        user="micoliser",
        password="****",
        database="bincomphptest")
curr = conn.cursor()


def keep_alive():
    """ Executes a lightweight query """
    curr.execute("SELECT 1")


@app.route("/web/polls", strict_slashes=False)
def polls():
    """ creates the route for the poll """

    curr.execute("SELECT uniqueid, polling_unit_name FROM polling_unit")
    poll_dict = [{"id": row[0], "name": row[1]} for row in curr.fetchall()]

    curr.execute("SELECT lga_id, lga_name FROM lga")
    lga_dict = [{"id": row[0], "name": row[1]} for row in curr.fetchall()]

    schedule.every(5).minutes.do(keep_alive)

    # Run the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    return render_template("polls.html",
                           poll_units=poll_dict,
                           lgas=lga_dict,
                           cache_id=uuid.uuid4())


if __name__ == "__main__":
    app.run(host="0.0.0.0")
