# GRPC
## Prerequisites
```bash
Python 3.7 or higher
pip package manager
```
## Installation & Setup
### Step 1: Create Virtual Environment
```bash
python3 -m venv myenv
source myenv/bin/activate
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