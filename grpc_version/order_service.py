import grpc
from flask import Flask, jsonify, request

import inventory_pb2
import inventory_pb2_grpc

app = Flask(__name__)

channel = grpc.insecure_channel("localhost:50052")
stub = inventory_pb2_grpc.InventoryServiceStub(channel)

DEADLINE_SECONDS = 2

# Map gRPC status codes to HTTP codes for the caller
HTTP_FOR = {
    grpc.StatusCode.DEADLINE_EXCEEDED: 504,
    grpc.StatusCode.UNAVAILABLE: 503,
    grpc.StatusCode.NOT_FOUND: 404,
    grpc.StatusCode.FAILED_PRECONDITION: 409,
    grpc.StatusCode.INVALID_ARGUMENT: 400,
}


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}

    try:
        quantity = int(data.get("quantity") or 0)
    except (TypeError, ValueError):
        quantity = 0

    req = inventory_pb2.CheckInventoryRequest(
        item_id=str(data.get("item_id") or ""),
        quantity=quantity,
    )

    try:
        resp = stub.CheckInventory(req, timeout=DEADLINE_SECONDS)
    except grpc.RpcError as e:
        app.logger.error("gRPC call failed: %s - %s", e.code().name, e.details())
        return jsonify(
            order_status="failed",
            grpc_status=e.code().name,
            error=e.details(),
        ), HTTP_FOR.get(e.code(), 500)

    return jsonify(
        order_status="accepted",
        item_id=resp.item_id,
        requested=resp.requested,
        in_stock=resp.in_stock,
    ), 201


if __name__ == "__main__":
    app.run(port=5002)