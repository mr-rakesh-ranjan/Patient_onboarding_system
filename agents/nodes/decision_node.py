def template_decision(state):
    if state["template"] is None:
        return "manual_review"
    return "extract"


def validation_decision(state):
    if state.get("validation_status") == "passed":
        return "memory"
    return "manual_review"