import requests, os
from dotenv import load_dotenv,find_dotenv


load_dotenv(find_dotenv())

URL = os.getenv("METRICS_SERVICE_URL")

def get_approved_documents() -> list:
    try:
        res = requests.get(f"{URL}/get-approved-docuement-types")
        res.raise_for_status()
        
        try:
            data = res.json().get("document_types", [])
            if isinstance(data, list):
                return data
            else:
                print(f"Unexpected response format: {data}")
                return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []

    except requests.RequestException as e:
        print(f"Error fetching approved document types: {e}")
        return []