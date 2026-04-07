import requests, os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

URL = os.getenv("AZURE_OCR_SERVICE_URL")

def call_ocr(file):
    res = requests.post(f"{URL}/extract", files={"file": file})
    res.raise_for_status()
    return res.json()