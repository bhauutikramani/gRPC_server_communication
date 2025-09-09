import grpc
from concurrent import futures #give thread pool
import threading #property of single thread
import networkx as nx #networkx is a graph library for graph operations
import graph_service_pb2
import graph_service_pb2_grpc

class GraphService(graph_service_pb2_grpc.GraphServiceServicer):
    def __init__(self):
        self.combined_graph = nx.Graph()
        self.client_graphs = {}  # Store individual client graphs
        self.lock = threading.RLock()  # For thread-safe operations
        self.combined_graph.clear()
        self.client_graphs.clear()
    
    def SubmitGraph(self, request, context):
            with self.lock:
                client_id = request.client_id
                print(f"Received graph from client: {client_id}")
                client_graph = nx.Graph() #dict<int, dict<int, dict>>
                
                for adj_list in request.adjacency_lists:
                    node = adj_list.node #node is the node number
                    neighbors = list(adj_list.neighbors) #neighbors is the list of neighbors
                    client_graph.add_node(node)
                    for neighbor in neighbors:
                        client_graph.add_edge(node, neighbor)
                self.client_graphs[client_id] = client_graph
                self._rebuild_combined_graph()
                
                print(f"Graph from {client_id} processed. Combined graph: "
                          f"{self.combined_graph.number_of_nodes()} nodes ,"
                          f"{self.combined_graph.number_of_edges()} edges")
                
                return graph_service_pb2.SubmissionResponse(success=True,message=f"Graph from {client_id} successfully processed")
    
    def HasIndependentSet(self, request, context):
            with self.lock:
                k = request.k
                print(f"Checking for independent set of size >= {k}")
                
                if self.combined_graph.number_of_nodes() == 0:
                    return graph_service_pb2.BooleanResponse(
                        result=(k<=0),
                        message="No graph data available"
                    )
                
                # Find maximum independent set
                max_independent_set = self._find_max_independent_set()
                result = len(max_independent_set) >= k
                
                print(f"Maximum independent set size: {len(max_independent_set)}, "
                          f"Required: {k}, Result: {result}")
                
                return graph_service_pb2.BooleanResponse(
                    result=result,
                    message=f"Maximum independent set size: {len(max_independent_set)}"
                )
    
    def HasMatching(self, request, context):
            with self.lock:
                k = request.k
                print(f"Checking for matching of size >= {k}")
                
                if self.combined_graph.number_of_nodes() == 0:
                    return graph_service_pb2.BooleanResponse(
                        result=(k<=0),
                        message="No graph data available"
                    )
                
                # Find maximum matching
                max_matching = nx.max_weight_matching(self.combined_graph)
                matching_size = len(max_matching)
                result = matching_size >= k
                
                print(f"Maximum matching size: {matching_size}, "
                          f"Required: {k}, Result: {result}")
                
                return graph_service_pb2.BooleanResponse(
                    result=result,
                    message=f"Maximum matching size: {matching_size}"
                )
    
    def GetGraphStatus(self, request, context):
            with self.lock:
                return graph_service_pb2.GraphStatus(
                    total_nodes=self.combined_graph.number_of_nodes(),
                    total_edges=self.combined_graph.number_of_edges(),
                    connected_clients=list(self.client_graphs.keys())
                )
    
    def _rebuild_combined_graph(self):
        self.combined_graph.clear()
        all_edges = set()
        all_nodes = set()
        
        for client_id, graph in self.client_graphs.items():
            all_nodes.update(graph.nodes())
            all_edges.update(graph.edges())
        
        self.combined_graph.add_nodes_from(all_nodes)
        self.combined_graph.add_edges_from(all_edges)
        
        print(f"Combined graph rebuilt with {self.combined_graph.number_of_nodes()} nodes "
                   f"and {self.combined_graph.number_of_edges()} edges")
    
    def _find_max_independent_set(self):
        if self.combined_graph.number_of_nodes() == 0:
            return set()
        
        
        if self.combined_graph.number_of_nodes() <= 20:
            return self._exact_max_independent_set()
        else:
            return self._greedy_independent_set()
    
    def _exact_max_independent_set(self):
        try:
            return nx.maximum_independent_set(self.combined_graph)
        except:
            return self._greedy_independent_set()
    
    # def _greedy_independent_set(self):
    #     """Greedy approximation for maximum independent set"""
    #     independent_set = set()
    #     remaining_nodes = set(self.combined_graph.nodes())
        
    #     while remaining_nodes:
    #         # Choose node with minimum degree among remaining nodes
    #         min_degree_node = min(remaining_nodes, 
    #                             key=lambda n: len(set(self.combined_graph.neighbors(n)) & remaining_nodes))
            
    #         # Add to independent set
    #         independent_set.add(min_degree_node)
            
    #         # Remove node and all its neighbors from remaining nodes
    #         neighbors_to_remove = set(self.combined_graph.neighbors(min_degree_node)) & remaining_nodes
    #         remaining_nodes -= neighbors_to_remove
    #         remaining_nodes.discard(min_degree_node)
        
    #     return independent_set

    def _greedy_independent_set(self):
        independent_set = set()
        remaining_nodes = set(self.combined_graph.nodes())

        while remaining_nodes:
            node_with_fewest_neighbors = None
            min_neighbor_count = float('inf')

            for node in remaining_nodes:
                
                current_neighbor_count = 0
                for neighbor in self.combined_graph.neighbors(node):
                    if neighbor in remaining_nodes:
                        current_neighbor_count += 1

                if current_neighbor_count < min_neighbor_count:
                    min_neighbor_count = current_neighbor_count
                    node_with_fewest_neighbors = node

            independent_set.add(node_with_fewest_neighbors)

            neighbors = set(self.combined_graph.neighbors(node_with_fewest_neighbors))
            neighbors_to_remove = neighbors & remaining_nodes  # Only remove neighbors that are still remaining
            remaining_nodes -= neighbors_to_remove
            remaining_nodes.discard(node_with_fewest_neighbors)  # Remove the node itself

        return independent_set


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    graph_service_pb2_grpc.add_GraphServiceServicer_to_server(GraphService(), server)
    
    listen_addr = '[::]:1025'
    server.add_insecure_port(listen_addr)
    
    print(f"Starting gRPC server on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()