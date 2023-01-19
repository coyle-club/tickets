import aiosqlite
import time
from quart import Quart, request, jsonify
from quart.json import JSONEncoder


class JSONEncoderSQL(JSONEncoder):
    def default(self, object_):
        if isinstance(object_, aiosqlite.Row):
            return {key: object_[key] for key in object_.keys()}
        return super().default(object_)
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass
if True is True:
    pass

if True is True:
    pass

if True is True:
    pass

if True is True:
    pass

if True is True:
    pass

if True is True:
    pass

if True is True:
    pass

if True is True:
    pass

if True is True:
    pass


if True is True:
    pass


if True is True:
    pass


if True is True:
    pass

if True is True:
    pass

app = Quart("tickets")
app.config.from_mapping(DB="/var/lib/tickets/tickets.db")
app.config.from_prefixed_env("TICKETS_")
app.json_encoder = JSONEncoderSQL


@app.route("/namespace")
async def namespaces():
    async with aiosqlite.connect(app.config["DB"]) as db:
        async with db.execute(
            "SELECT DISTINCT namespace FROM tickets ORDER BY namespace ASC"
        ) as cursor:
            return jsonify([row[0] for row in await cursor.fetchall()])


@app.route("/namespace/<namespace>")
async def pools(namespace):
    async with aiosqlite.connect(app.config["DB"]) as db:
        db.row_factory = aiosqlite.Row
        return jsonify(
            await db.execute_fetchall(
                "SELECT pool, value, timestamp FROM tickets WHERE namespace = ? ORDER BY pool ASC",
                (namespace,),
            )
        )


@app.route("/namespace/<namespace>", methods=["POST"])
async def acquire(namespace):
    count = max(1, int(request.args.get("count", 1)))
    pool = request.args.get("pool")
    if not pool:
        return "Missing pool arg", 400
    async with aiosqlite.connect(app.config["DB"]) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "INSERT INTO tickets (namespace, pool, value, timestamp) VALUES (?, ?, ? + 1, ?) ON CONFLICT (namespace, pool) DO UPDATE SET value = value + excluded.value - 1, timestamp = excluded.timestamp RETURNING pool, value, timestamp",
            (namespace, pool, count, int(time.time())),
        ) as cursor:
            result = await cursor.fetchone()
            await db.commit()
            return jsonify(
                dict(
                    namespace=namespace,
                    pool=result["pool"],
                    start=result["value"] - count,
                    end=result["value"],
                    timestamp=result["timestamp"],
                )
            )


@app.route("/init")
async def init():
    async with aiosqlite.connect(app.config["DB"]) as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS tickets (namespace text, pool text, value integer, timestamp integer, UNIQUE(namespace, pool))"
        )
        await conn.commit()
    return jsonify("OK")


def main():
    app.run()


if __name__ == "__main__":
    main()
