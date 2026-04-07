# agents/nodes/async_doc_processing_node.py

import asyncio
from services.ocr_service import call_ocr
from services.classifier_service import classify

async def process_single_document(file, doc_id):
    loop = asyncio.get_event_loop()

    # Step 1: OCR (blocking → thread)
    ocr_result = await loop.run_in_executor(None, call_ocr, file)
    text = ocr_result.get("text", "")
    
    ocr_message = f"OCR DONE :: Document {doc_id} OCR completed. Extracted {len(text)} characters"
    print(ocr_message)

    # Step 2: Classification (depends on OCR → sequential per doc)
    classification = await loop.run_in_executor(None, classify, text)

    classification_message = f"CLASSIFICATION DONE :: Document {doc_id} classified as {classification.get('document_type', 'unknown')}"
    print(classification_message)

    return {
        "doc_id": doc_id,
        "text": text,
        "document_type": classification.get("document_type", "unknown"),
        "ocr_message": ocr_message,
        "classification_message": classification_message
    }


async def async_doc_processing_node(state):
    files = state["files"]

    # 🔥 Each document processed independently
    tasks = [
        process_single_document(file, f"doc_{i}")
        for i, file in enumerate(files)
    ]

    # ⚡ Run BOTH documents in parallel
    results = await asyncio.gather(*tasks)

    # Store clean structured output
    documents = {}
    processing_messages = []
    
    for result in results:
        doc_id = result["doc_id"]
        documents[doc_id] = {
            "text": result["text"],
            "document_type": result["document_type"]
        }
        processing_messages.append(result["ocr_message"])
        processing_messages.append(result["classification_message"])

    state["documents"] = documents
    state.setdefault("node_history", []).append({
        "node": "async_doc_processing",
        "status": "done",
        "documents": documents,
        "messages": processing_messages
    })
    return state