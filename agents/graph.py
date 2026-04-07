from langgraph.graph import StateGraph, END
from agents.state import AgentState

from agents.nodes.async_doc_processing_node import async_doc_processing_node
from agents.nodes.llm_decision_node import llm_decision_node
from agents.nodes.template_node import template_node
from agents.nodes.extraction_node import extraction_node
from agents.nodes.validation_node import validation_node
from agents.nodes.decision_node import template_decision, validation_decision
from services.memory_service import save_case

def memory_node(state):
    # Create case_id from name and timestamp
    id_data = state.get("extracted_data", {}).get("id_data", {})
    name = "unknown"
    for item in id_data.get("extracted_values", []):
        if item.get("field_name", "").lower() == "name":
            name = item.get("field_value", "unknown") or "unknown"
            break

    from datetime import datetime
    case_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    messages = [f"[memory_node] Saving case {case_id}"]
    print(messages[0])

    try:
        save_case(case_id, state)
        state["case_id"] = case_id
        state["memory_saved"] = True
        success_msg = f"[memory_node] Case saved: {case_id}"
        messages.append(f"Successfully saved case {case_id} to memory.")
        messages.append(success_msg)
        print(messages[-2])
        print(messages[-1])
    except Exception as e:
        state["memory_saved"] = False
        error_msg = f"Memory save failed: {e}"
        state["errors"].append(error_msg)
        messages.append(f"[memory_node] Error saving case: {e}")
        print(messages[-1])

    state["memory_messages"] = messages
    return state


def manual_review_node(state):
    state["errors"].append("Manual review required")
    return state

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("process_docs", async_doc_processing_node)
    graph.add_node("llm_decision", llm_decision_node)
    graph.add_node("template", template_node)
    graph.add_node("extract", extraction_node)
    graph.add_node("validate", validation_node)
    graph.add_node("memory", memory_node)
    graph.add_node("manual_review", manual_review_node)
    graph.add_node("END", lambda x: x)  # Add END as a node

    graph.set_entry_point("process_docs")

    graph.add_edge("process_docs", "llm_decision")
    graph.add_edge("llm_decision", "template")

    graph.add_conditional_edges(
        "template",
        template_decision,
        {
            "extract": "extract",
            "manual_review": "manual_review"
        }
    )

    graph.add_edge("extract", "validate")
    graph.add_conditional_edges(
        "validate",
        validation_decision,
        {
            "memory": "memory",
            "manual_review": "manual_review"
        }
    )
    graph.add_edge("memory", "END")
    graph.add_edge("manual_review", "memory")

    return graph.compile()