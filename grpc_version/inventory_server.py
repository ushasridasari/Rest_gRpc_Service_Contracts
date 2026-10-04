import os
import time
from concurrent import futures

import grpc
import inventory_pb2
import inventory_pb2_grpc

# Same fake stock as the REST version
STOCK = {"apple": 10, "banana": 0, "laptop": 3}

# Temporary delay for the failure demo (default 0 = no delay)
DELAY = float(os.getenv("INVENTORY_DELAY_SECONDS", "0"))


class InventoryServicer(inventory_pb2_grpc.InventoryServiceServicer):
    def CheckInventory(self, request, context):
        # Simulates a slow service when INVENTORY_DELAY_SECONDS is set
        time.sleep(DELAY)

        # INVALID_ARGUMENT (REST 400)
        if not request.item_id or request.quantity <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                          "item_id and a positive quantity are required")

        # NOT_FOUND (REST 404)
        if request.item_id not in STOCK:
            context.abort(grpc.StatusCode.NOT_FOUND, "item not found")

        # FAILED_PRECONDITION (REST 409)
        if STOCK[request.item_id] < request.quantity:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "insufficient stock")

        # OK (REST 200)
        return inventory_pb2.CheckInventoryResponse(
            item_id=request.item_id,
            requested=request.quantity,
            in_stock=STOCK[request.item_id],
            available=True,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryServicer(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("gRPC Inventory Service running on port 50052", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()