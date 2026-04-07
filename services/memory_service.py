import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "patient_memory.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {MEMORY_FILE}, starting fresh.")
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def save_case(case_id, state):
    # Create a serializable copy of the state, excluding non-serializable objects like UploadedFile
    serializable_state = {}
    for k, v in state.items():
        if k == "files":
            # Store only file names instead of UploadedFile objects
            serializable_state[k] = [f.name if hasattr(f, 'name') else str(f) for f in v]
        else:
            serializable_state[k] = v
    
    try:
        memory = load_memory()
        memory[case_id] = {
            "state": serializable_state,
            "timestamp": datetime.now().isoformat()
        }
        save_memory(memory)
        print(f"Successfully saved case {case_id} to memory.")
    except Exception as e:
        print(f"Error saving to memory: {e}")

def query_case(case_id):
    memory = load_memory()
    return memory.get(case_id)