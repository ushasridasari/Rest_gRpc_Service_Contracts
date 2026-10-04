import sys

import grpc
import inventory_pb2
import inventory_pb2_grpc

item_id = sys.argv[1] if len(sys.argv) > 1 else "apple"
quantity = int(sys.argv[2]) if len(sys.argv) > 2 else 2

with grpc.insecure_channel("localhost:50052") as channel:
    stub = inventory_pb2_grpc.InventoryServiceStub(channel)
    request = inventory_pb2.CheckInventoryRequest(item_id=item_id, quantity=quantity)

    print("REQUEST:")
    print(request)

    try:
        response = stub.CheckInventory(request, timeout=2)
        print("RESPONSE:")
        print(response)
        print("STATUS: OK")
    except grpc.RpcError as e:
        print(f"STATUS: {e.code().name}")
        print(f"DETAILS: {e.details()}")