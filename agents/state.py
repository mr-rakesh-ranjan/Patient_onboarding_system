from typing import TypedDict, Optional, Dict, Any, List

class AgentState(TypedDict):
    files: List[Any]
    documents: Dict
    template: Optional[Dict]
    extracted_data: Dict
    validation_status: str
    validation_details: List[Dict]
    errors: List[str]
    doc_mapping: Dict