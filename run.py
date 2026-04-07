import asyncio
from agents.graph import build_graph

async def run_agent(files, progress_callback=None):
    """
    Run the agent graph with optional progress callbacks
    
    Args:
        files: List of uploaded files
        progress_callback: Optional function to call with (node_name, status, data) after each node
    """
    print(f"Starting agent with {len(files)} files...")
    try:
        graph = build_graph()

        state = {
            "files": files,
            "documents": {},
            "template": None,
            "extracted_data": {},
            "validation_status": "",
            "validation_details": [],
            "manual_review_required": False,
            "errors": [],
            "doc_mapping": {},
            "node_history": []
        }

        # Use streaming to get updates as each node completes
        async for event in graph.astream(state):
            # Event contains the node name as key and state as value
            for node_name, node_state in event.items():
                # Update our state first
                state.update(node_state)
                
                if progress_callback:
                    # Call the callback with node information and full state
                    progress_callback(node_name, state)
        
        print("Graph execution completed successfully.")
        return state
    except Exception as e:
        print(f"Error in run_agent: {e}")
        raise
