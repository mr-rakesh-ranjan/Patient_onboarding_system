from services.template_service import get_template

def template_node(state):
    id_doc = state["doc_mapping"]["id_proof"]
    form_doc = state["doc_mapping"]["patient_form"]

    # Get document types for both documents
    id_doc_type = state["documents"][id_doc]["document_type"]
    form_doc_type = state["documents"][form_doc]["document_type"]

    # Get templates for both documents
    id_templates = get_template(id_doc_type)
    form_templates = get_template(form_doc_type)
    
    # Store primary template (ID proof template) for extraction
    state["template"] = id_templates[0] if id_templates else None
    
    # Store both templates for UI display
    state["templates"] = {
        "id_template": id_templates[0] if id_templates else None,
        "form_template": form_templates[0] if form_templates else None
    }
    
    state.setdefault("node_history", []).append({
        "node": "template",
        "status": "done",
        "template": state["template"],
        "templates": state["templates"]
    })
    return state