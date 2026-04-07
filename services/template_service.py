import requests, os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

URL = os.getenv("ADMIN_SERVICE_URL")

def get_template(doc_type):
    try:
        res = requests.get(f"{URL}/admin/templates?page=1&page_size=20&sort_by=created_at&sort_order=DESC&search={doc_type}")
        res.raise_for_status()

        try:
            data = res.json().get("data", [])
            if isinstance(data, list) and len(data) > 0:
                return data

            else:
                print(f"Unexpected response format: {data}")
                return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []   

    except requests.RequestException as e:
        print(f"Error fetching template for {doc_type}: {e}")
        return None

def get_template_fields(document_type):
    try:
        templates = get_template(document_type)
        if templates:
            if isinstance(templates, list) and len(templates) > 0:
                if templates[0].get("document_type_name") == document_type:
                    print(f"Found template for {document_type}: {templates[0].get('field_lists', [])}")
                    return templates[0].get("field_lists", [])
        else:
            print(f"No templates found for document type: {document_type}")
        return []
    except Exception as e:
        print(f"Error fetching template fields for {document_type}: {e}")
        return []