import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://localhost:5001/inventory/check")
TIMEOUT_SECONDS = 2


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    payload = {"item_id": data.get("item_id"), "quantity": data.get("quantity")}

    try:
        r = requests.post(INVENTORY_URL, json=payload, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        app.logger.error("Inventory timed out after %s seconds", TIMEOUT_SECONDS)
        return jsonify(order_status="failed", error="inventory service timed out"), 504
    except requests.exceptions.ConnectionError:
        app.logger.error("Inventory service unreachable")
        return jsonify(order_status="failed", error="inventory service unreachable"), 503

    if r.status_code == 200:
        return jsonify(order_status="accepted", inventory=r.json()), 201

    return jsonify(order_status="rejected", reason=r.json()), r.status_code


if __name__ == "__main__":
    app.run(port=5003)