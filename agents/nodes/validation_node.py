from services.validation_service import validate_extracted_data

def validation_node(state):
    result = validate_extracted_data(state["extracted_data"])
    state["validation_status"] = result.get("status", "failed")
    state["validation_details"] = result.get("validation_details", [])

    state.setdefault("node_history", []).append({
        "node": "validation",
        "status": state["validation_status"],
        "validation_details": state["validation_details"]
    })

    return state