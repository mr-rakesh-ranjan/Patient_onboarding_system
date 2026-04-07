from services.extraction_service import extract

def extraction_node(state):
    id_doc = state["doc_mapping"]["id_proof"]
    form_doc = state["doc_mapping"]["patient_form"]

    text = (
        state["documents"][id_doc]["text"] +
        "\n" +
        state["documents"][form_doc]["text"]
    )

    document_type = state["documents"][id_doc]["document_type"]

    fields = [
        {
            "field_name": f["field_name"],
            "normalized_name": f["field_name"],
            "confidence": 1.0,
            "is_mandatory": f.get("is_mandatory", True),
            "field_type": f.get("field_type", "text"),
            "reason": "",
            "location": "body",
            "indicators": []
        }
        for f in state["template"].get("field_lists", []) if not f.get("is_deleted", False)
    ]

    id_text = state["documents"][id_doc]["text"]
    form_text = state["documents"][form_doc]["text"]

    id_data = extract(id_text, document_type, fields)
    form_data = extract(form_text, document_type, fields)

    state["extracted_data"] = {
        "id_data": id_data,
        "form_data": form_data
    }
    state.setdefault("node_history", []).append({
        "node": "extraction",
        "status": "done",
        "id_data": id_data,
        "form_data": form_data
    })
    return state