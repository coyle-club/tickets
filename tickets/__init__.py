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
        "CREATE TABLE IF NOT EXISTS tickets (namespace text, pool text, value integer, timestamp integer, UNIQUE(namespace, pool))"
    )
    conn.commit()

app = Flask("tickets")
metrics = PrometheusMetrics(app)


@app.route("/pool")
def namespaces():
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT namespace FROM tickets ORDER BY namespace ASC")
        return jsonify([row[0] for row in cur.fetchall()])


@app.route("/pool/<namespace>")
def pools(namespace):
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT pool, value, timestamp FROM tickets WHERE namespace = ? ORDER BY pool ASC",
            (namespace,),
        )
        return jsonify(
            [
                dict(pool=row[0], value=row[1], timestamp=row[2])
                for row in cur.fetchall()
            ]
        )


@app.route("/pool/<namespace>", methods=["POST"])
def acquire(namespace):
    count = max(1, int(request.args.get("count", 1)))
    pool = request.args["pool"]
    timestamp = int(time() * 1000)
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tickets (namespace, pool, value, timestamp) VALUES (?, ?, ? + 1, ?) ON CONFLICT (namespace, pool) DO UPDATE SET value = value + excluded.value - 1, timestamp = excluded.timestamp RETURNING pool, value, timestamp",
            (namespace, pool, count, timestamp),
        )
        row = cur.fetchone()
        conn.commit()
    return jsonify(
        dict(pool=row[0], start=row[1] - count, count=count, timestamp=row[2])
    )
