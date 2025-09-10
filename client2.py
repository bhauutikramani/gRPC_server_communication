import grpc
import time
import graph_service_pb2
import graph_service_pb2_grpc

class GraphClient2:
    def __init__(self, server_address='localhost:1025'):
        self.server_address = server_address
        self.client_id = "client_2"
        self.graph = graph = graph = {
    20: [21, 25],
    21: [20, 22, 30],
    22: [21, 23],
    23: [22, 24, 35],
    24: [23, 25],
    25: [20, 24, 26],
    26: [25, 27],
    27: [26, 28, 40],
    28: [27, 29],
    29: [28, 30],
    30: [21, 29, 31],
    31: [30, 32, 45],
    32: [31, 33],
    33: [32, 34],
    34: [33, 35, 50],
    35: [23, 34, 36],
    36: [35, 37],
    37: [36, 38, 55],
    38: [37, 39],
    39: [38, 40],
    40: [27, 39, 41],
    41: [40, 42],
    42: [41, 43, 60],
    43: [42, 44],
    44: [43, 45],
    45: [31, 44, 46],
    46: [45, 47],
    47: [46, 48, 65],
    48: [47, 49],
    49: [48, 50],
    50: [34, 49, 51],
    51: [50, 52],
    52: [51, 53, 67],
    53: [52, 54],
    54: [53, 55],
    55: [37, 54, 56],
    56: [55, 57],
    57: [56, 58, 68],
    58: [57, 59],
    59: [58, 60],
    60: [42, 59, 61],
    61: [60, 62],
    62: [61, 63, 69],
    63: [62, 64],
    64: [63, 65],
    65: [47, 64, 66],
    66: [65, 67],
    67: [52, 66, 70],
    68: [57, 69],
    69: [62, 68, 70],
    70: [67, 69]
}


        
    def connect_and_submit(self):
            with grpc.insecure_channel(self.server_address) as channel:
                stub = graph_service_pb2_grpc.GraphServiceStub(channel)
                adjacency_lists = []
                for node, neighbors in self.graph.items():
                    adj_list = graph_service_pb2.AdjacencyList(
                        node=node,
                        neighbors=neighbors
                    )
                    adjacency_lists.append(adj_list)

                request = graph_service_pb2.GraphSubmission(
                    client_id=self.client_id,
                    adjacency_lists=adjacency_lists
                )
                response = stub.SubmitGraph(request)
                if response.success:
                    print(f"Graph submitted successfully: {response.message}")
                else:
                    print(f"Failed to submit graph: {response.message}")
                
                return response.success
    
    def query_independent_set(self, k):
            with grpc.insecure_channel(self.server_address) as channel:
                stub = graph_service_pb2_grpc.GraphServiceStub(channel)
                request = graph_service_pb2.ISQuery(k=k)
                response = stub.IndependentSetQuery(request)
                print(f"Independent set query (k={k}): {response.result} - {response.message}")
                return response.result
                
    
    def query_matching(self, k):
            with grpc.insecure_channel(self.server_address) as channel:
                stub = graph_service_pb2_grpc.GraphServiceStub(channel)
                request = graph_service_pb2.MQuery(k=k)
                response = stub.MatchingQuery(request)
                print(f"Matching query (k={k}): {response.result} - {response.message}")
                return response.result

    
    def get_graph_status(self):
            with grpc.insecure_channel(self.server_address) as channel:
                stub = graph_service_pb2_grpc.GraphServiceStub(channel)
                request = graph_service_pb2.Empty()
                response = stub.GetGraphStatus(request)
                print(f"Graph Status - Nodes: {response.total_nodes}, "f"Edges: {response.total_edges}, "f"Clients: {list(response.connected_clients)}")
                return response

def main():
    client = GraphClient2()
    print("Client 2 Graph:")
    for node, neighbors in client.graph.items():
        print(f"  Node {node}: {neighbors}")
    
    if client.connect_and_submit():
        print("Graph submission successful!")
        print("Enter k values for queries (enter -1 to disconnect and exit):")
        
        while True:
                k = int(input("Enter k value: "))
                if k == -1:
                    print("Disconnecting client and exiting...")
                    break
                print(f"Performing queries with k={k}...")
                client.query_independent_set(k)
                client.query_matching(k)
                
        print("Client execution completed.")
        client.get_graph_status()
    else:
        print("Failed to submit graph")

if __name__ == '__main__':
    main()