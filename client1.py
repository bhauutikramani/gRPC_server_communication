import grpc
import time
import graph_service_pb2
import graph_service_pb2_grpc

class GraphClient1:
    def __init__(self, server_address='localhost:1025'):
        self.server_address = server_address
        self.client_id = "client_1"
        self.graph = {
 1: [44],
 2: [13, 40, 6, 30],
 3: [],
 4: [27, 39, 48, 10],
 5: [10, 41, 24, 44],
 6: [14, 28, 2],
 7: [],
 8: [46, 24, 42, 40, 19],
 9: [47, 43],
 10: [5, 11, 14, 4, 13],
 11: [14, 41, 10, 46, 33],
 12: [15, 29],
 13: [20, 2, 37, 40, 10],
 14: [11, 6, 10],
 15: [17, 12, 25, 37],
 16: [22],
 17: [21, 15, 32, 34],
 18: [38, 34],
 19: [27, 29, 32, 8, 22],
 20: [13, 34, 46],
 21: [34, 17, 23, 44],
 22: [16, 39, 19],
 23: [46, 21, 32],
 24: [8, 5],
 25: [46, 15],
 26: [33, 38],
 27: [47, 4, 37, 19],
 28: [38, 47, 6, 37],
 29: [47, 19, 12],
 30: [36, 40, 2],
 31: [],
 32: [17, 19, 23],
 33: [26, 11],
 34: [21, 18, 20, 17, 50],
 35: [],
 36: [30, 47],
 37: [27, 45, 13, 15, 28],
 38: [18, 26, 28],
 39: [4, 22],
 40: [30, 8, 2, 13],
 41: [11, 48, 5],
 42: [8],
 43: [9],
 44: [1, 21, 5],
 45: [37],
 46: [8, 23, 25, 20, 11],
 47: [27, 29, 9, 36, 28],
 48: [4, 41],
 49: [],
 50: [34]
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
    client = GraphClient1()
    print("Client 1 Graph:")
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