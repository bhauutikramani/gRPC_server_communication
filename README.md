# GRPC
## Prerequisites
```bash
Python 3.7 or higher
pip package manager
```
## Installation & Setup
### Step 1: Create Virtual Environment
```bash
python3 -m venv myven
source myven/bin/activate
```
### Step 2: Install Required Dependencies
```bash
pip install grpcio grpcio-tools networkx
```

### Step 3: Generate gRPC Code
```bash
create .ptoto file
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. graph_service.proto
```

This generates the required Protocol Buffer files:
- `graph_service_pb2.py` - Message definitions
- `graph_service_pb2_grpc.py` - Service stubs and skeletons

---

## Compilation & Execution

### Project Structure
```
distributed_graph_system/
├── graph_service.proto           
├── generate_grpc.py            
├── server.py                   
├── client1.py                  
├── client2.py     
├── graph_service.proto                  
└── README.md                   
```

### Execution Options

### Local Execution 

1. **Start the Server** (Terminal 1):
```bash
python3 server.py
```
Server will start on the port specified in file.

2. **Run First Client** (Terminal 2):
```bash
python3 client1.py
```

3. **Run Second Client** (Terminal 3 - can start anytime):
```bash
python3 client2.py
```

### For HPC
1. **Allocate resource on server** (Terminal 1):
```bash
module load python/
salloc --nodes=1 --ntasks=3 --cpus-per-task=2
```

2. **Run server file** (Terminal 1):
```bash
srun --ntasks=1 --cpus-per-task=2 python3 -u server.py
```

3. **Run first client** (Terminal 2):
```bash
module load python/
srun --ntasks=1 --cpus-per-task=1 python3 -u client1.py
```
4. **Run second client** (Terminal 3):
```bash
module load python/
srun --ntasks=1 --cpus-per-task=1 python3 -u client2.py
```

Client1 loads its graph from graph1.json, and Client2 loads its graph from graph2.json. Both clients then submit their respective graphs to the server using the SubmitGraph method. The server merges both graphs to form a combined graph.

After this, both clients can query the server simultaneously — for example, Client1 may ask for an independent set query while Client2 asks for a matching number query. These queries can run in parallel since they are read-only operations.

At any time, either client can upload new nodes or edges to the server again. When this happens, the server updates the combined graph (using a write lock). During this update, queries are temporarily paused. Once the update is finished, queries can again run in parallel without issues.