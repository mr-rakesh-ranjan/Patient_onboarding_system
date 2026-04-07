from agents.llm import get_llm
import json, re

llm = get_llm()

def llm_decision_node(state):
    documents = state["documents"]

    docs_summary = [
        f"{doc_id}: {doc['document_type']}"
        for doc_id, doc in documents.items()
    ]

    prompt = f"""
You are a strict JSON generator.

Documents:
{docs_summary}

Return ONLY JSON:
{{
  "id_proof": "doc_x",
  "patient_form": "doc_y"
}}
"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    try:
        decision = json.loads(content)
    except:
        # Handle markdown code blocks (```json {...}```)
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            decision = json.loads(match.group())
        else:
            raise ValueError(f"Could not extract JSON from LLM response: {content}")

    state["doc_mapping"] = decision
    state.setdefault("node_history", []).append({
        "node": "llm_decision",
        "status": "done",
        "doc_mapping": decision
    })
    return state