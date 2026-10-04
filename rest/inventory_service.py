import os
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# Fake stock data (same data will be used in the gRPC version)
STOCK = {"apple": 10, "banana": 0, "laptop": 3}

# Temporary delay for the failure demo (default 0 = no delay)
DELAY = float(os.getenv("INVENTORY_DELAY_SECONDS", "0"))


@app.post("/inventory/check")
def check():
    # Simulates a slow service when INVENTORY_DELAY_SECONDS is set
    time.sleep(DELAY)

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    qty = data.get("quantity")

    # 400: bad input
    if not item_id or not isinstance(qty, int) or qty <= 0:
        return jsonify(error="item_id and a positive integer quantity are required"), 400

    # 404: unknown item
    if item_id not in STOCK:
        return jsonify(item_id=item_id, available=False, error="item not found"), 404

    # 409: item exists but not enough stock
    if STOCK[item_id] < qty:
        return jsonify(item_id=item_id, requested=qty, in_stock=STOCK[item_id],
                       available=False, error="insufficient stock"), 409

    # 200: available
    return jsonify(item_id=item_id, requested=qty, in_stock=STOCK[item_id],
                   available=True), 200


if __name__ == "__main__":
    app.run(port=5001)