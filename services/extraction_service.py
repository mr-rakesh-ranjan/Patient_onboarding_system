import requests, os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

URL = os.getenv("EXTRACTION_SERVICE_URL")

def extract(text, document_type, fields):
    try:
        res = requests.post(f"{URL}/extract-values", json={
            "text": text,
            "document_type": document_type,
            "fields": fields
        })
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error extracting values for {document_type}: {e}")
        return {"error": str(e)}
