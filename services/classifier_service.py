import requests, os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

from services.metrics_service import get_approved_documents

URL = os.getenv("CLASSIFIER_SERVICE_URL")

# helper function to call classifier service
approved_documents = get_approved_documents()

def classify(text):
    res = requests.post(f"{URL}/classify", json={"text": text, "hint_categories": approved_documents})
    res.raise_for_status()
    return res.json().get("classification", {})