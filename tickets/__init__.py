from flask import Flask, request, jsonify
import click
import sqlite3
from time import time
import json
import os
from prometheus_flask_exporter import PrometheusMetrics

DB_FILENAME = os.environ.get("DB_FILENAME", "/var/lib/tickets/tickets.db")

with sqlite3.connect(DB_FILENAME) as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tickets (pool text, value integer, timestamp integer, UNIQUE(pool))"
    )
    conn.commit()

app = Flask("tickets")
metrics = PrometheusMetrics(app)


@app.route("/pool")
def pools():
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT pool, value, timestamp FROM tickets")
        results = cur.fetchall()
        return jsonify(
            [
                dict(pool=result[0], value=result[1], timestamp=result[2])
                for result in results
            ]
        )


@app.route("/pool", methods=["POST"])
def acquire():
    count = max(1, int(request.args.get("count", 1)))
    pool = request.args["pool"]
    timestamp = int(time() * 1000)
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tickets (pool, value, timestamp) VALUES (?, ? + 1, ?) ON CONFLICT (pool) DO UPDATE SET value = value + excluded.value - 1, timestamp = excluded.timestamp RETURNING *",
            (pool, count, timestamp),
        )
        result = cur.fetchone()
        conn.commit()
    return jsonify(
        dict(pool=result[0], start=result[1] - count, count=count, timestamp=result[2])
    )
