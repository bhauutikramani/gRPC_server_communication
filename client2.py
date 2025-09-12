import grpc
import time
import json
import graph_service_pb2
import graph_service_pb2_grpc

class GraphClient2:
    def __init__(self, server_address='localhost:1025'):
        self.server_address = server_address
        self.client_id = "client_2"
        self.graph = {}
        
    def load_graph_from_json(self):
        try:
            with open('graph2.json', 'r') as file:
                data = json.load(file)
                # Convert string keys to integers if needed
                self.graph = {int(k): v for k, v in data.items()}
            print("Graph loaded successfully from graph.json")
            return True
        except FileNotFoundError:
            print("Error: graph.json file not found in current directory")
            return False
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in graph.json")
            return False
        except Exception as e:
            print(f"Error loading graph: {e}")
            return False

    def connect_and_submit(self):
        try:
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
        except grpc.RpcError as e:
            print(f"gRPC error: fail to connect to server at {self.server_address}: {e}")
            return False    
        
    def query_independent_set(self, k):
        try:
            with grpc.insecure_channel(self.server_address) as channel:
                stub = graph_service_pb2_grpc.GraphServiceStub(channel)
                request = graph_service_pb2.ISQuery(k=k)
                response = stub.IndependentSetQuery(request)
                print(f"Independent set query (k={k}): {response.result} - {response.message}")
                return response.result
        except grpc.RpcError as e:
            print(f"gRPC error during independent set query:fail to connect to server: {e}")
            return None
                
    def query_matching(self, k):
        try:
            with grpc.insecure_channel(self.server_address) as channel:
                stub = graph_service_pb2_grpc.GraphServiceStub(channel)
                request = graph_service_pb2.MQuery(k=k)
                response = stub.MatchingQuery(request)
                print(f"Matching query (k={k}): {response.result} - {response.message}")
                return response.result
        except grpc.RpcError as e:
            print(f"gRPC error during matching query: fail to connect to server: {e}")
            return None
        
    def get_graph_status(self):
        with grpc.insecure_channel(self.server_address) as channel:
            stub = graph_service_pb2_grpc.GraphServiceStub(channel)
            request = graph_service_pb2.Empty()
            response = stub.GetGraphStatus(request)
            print(f"Graph Status - Nodes: {response.total_nodes}, "f"Edges: {response.total_edges}, "f"Clients: {list(response.connected_clients)}")
            return response

def main():
    client = GraphClient2()
    
    while True:
        print("\nEnter choice:")
        print("1) Insert graph")
        print("2) Insert k")
        print("3) Exit")
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                print("Loading graph from graph.json...")
                if client.load_graph_from_json():
                    
                    if client.connect_and_submit():
                        print("Graph submission successful!")
                    else:
                        print("Failed to submit graph")
                        
            elif choice == '2':
                if not client.graph:
                    print("Please insert graph first (option 1)")
                    continue
                    
                print("Enter k values for queries (enter -1 to return to menu):")
                while True:
                    try:
                        k = int(input("Enter k value: "))
                        if k == -1:
                            print("Returning to main menu...")
                            break
                        print(f"Performing queries with k={k}...")
                        client.query_independent_set(k)
                        client.query_matching(k)
                    except ValueError:
                        print("Please enter a valid integer")
                    except KeyboardInterrupt:
                        print("\nReturning to main menu...")
                        break
                        
            elif choice == '3':
                print("Exiting program...")
                if client.graph:
                    try:
                        client.get_graph_status()
                    except Exception as e:
                        print(f"Error retrieving graph status: {e}")
                break
                
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\nExiting program...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()