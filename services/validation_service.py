import requests, os
from dotenv import load_dotenv,find_dotenv
from difflib import SequenceMatcher
import re
from datetime import datetime

load_dotenv(find_dotenv())


def clean_aadhaar_number(aadhaar_str):
    """Remove all non-digit characters from Aadhaar number"""
    if not aadhaar_str:
        return ""
    return re.sub(r'\D', '', str(aadhaar_str))


def normalize_date(date_str):
    """Convert any date format to DD/MM/YYYY"""
    if not date_str:
        return ""
    
    date_str = str(date_str).strip()
    
    # Common date formats to try
    date_formats = [
        '%d/%m/%Y',  # 22/08/1958
        '%d-%m-%Y',  # 22-08-1958
        '%m/%d/%Y',  # 08/22/1958
        '%Y-%m-%d',  # 1958-08-22
        '%d/%m/%y',  # 22/08/58
        '%d-%m-%y',  # 22-08-58
        '%m/%d/%y',  # 08/22/58
        '%d %b %Y',  # 22 Aug 1958
        '%d %B %Y',  # 22 August 1958
        '%Y/%m/%d',  # 1958/08/22
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime('%d/%m/%Y')
        except ValueError:
            continue
    
    # If no format matches, return original
    return date_str


def normalize_name(name_str):
    """Normalize name by removing extra spaces and converting to lowercase"""
    if not name_str:
        return ""
    # Remove extra spaces and convert to lowercase
    return ' '.join(str(name_str).strip().lower().split())


def calculate_character_match(str1, str2):
    """Calculate character-level match (all characters must be same, ignoring case and spaces)"""
    if not str1 or not str2:
        return 0.0
    
    # Normalize: lowercase, remove spaces
    normalized1 = ''.join(str1.lower().split())
    normalized2 = ''.join(str2.lower().split())
    
    # Check if they're exactly the same
    if normalized1 == normalized2:
        return 1.0
    else:
        # Return similarity ratio as fallback
        return SequenceMatcher(None, normalized1, normalized2).ratio()


def get_field_value(extracted_data, field_name):
    """Extract value from extracted_data response"""
    if not extracted_data or "extracted_values" not in extracted_data:
        return None
    
    for item in extracted_data["extracted_values"]:
        if item["field_name"].lower() == field_name.lower():
            return str(item.get("field_value", "")).strip().lower()
    return None

def calculate_similarity(str1, str2):
    """Calculate string similarity ratio (0.0 to 1.0)"""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1, str2).ratio()

def validate_extracted_data(extracted_data):
    """
    Validate that id_data and form_data match for required fields with per-field rules:
    - Name: Character-level exact match (ignoring case and spaces)
    - Date of Birth: Exact match after normalizing to DD/MM/YYYY format
    - Address: 80% similarity match
    - Aadhaar Number: Exact match after removing non-digit characters
    """
    id_data = extracted_data.get("id_data", {})
    form_data = extracted_data.get("form_data", {})

    validation_results = []
    all_match = True

    # Validate Name
    id_name = get_field_value(id_data, "name")
    form_name = get_field_value(form_data, "name")
    
    name_similarity = calculate_character_match(id_name, form_name)
    name_matches = name_similarity >= 1.0
    
    if not name_matches:
        all_match = False
    
    validation_results.append({
        "field": "Name",
        "id_value": id_name,
        "form_value": form_name,
        "similarity": round(name_similarity * 100, 2),
        "matches": name_matches,
        "threshold": 100.0
    })

    # Validate Date of Birth
    id_dob = get_field_value(id_data, "date_of_birth")
    form_dob = get_field_value(form_data, "date_of_birth")
    
    # Normalize both dates to DD/MM/YYYY
    normalized_id_dob = normalize_date(id_dob)
    normalized_form_dob = normalize_date(form_dob)
    
    dob_matches = normalized_id_dob == normalized_form_dob
    dob_similarity = 1.0 if dob_matches else 0.0
    
    if not dob_matches:
        all_match = False
    
    validation_results.append({
        "field": "Date of Birth",
        "id_value": f"{id_dob} → {normalized_id_dob}",
        "form_value": f"{form_dob} → {normalized_form_dob}",
        "similarity": round(dob_similarity * 100, 2),
        "matches": dob_matches,
        "threshold": 100.0
    })

    # Validate Address (80% match)
    id_address = get_field_value(id_data, "address")
    form_address = get_field_value(form_data, "address")
    
    address_similarity = calculate_similarity(id_address, form_address)
    address_matches = address_similarity >= 0.8
    
    if not address_matches:
        all_match = False
    
    validation_results.append({
        "field": "Address",
        "id_value": id_address,
        "form_value": form_address,
        "similarity": round(address_similarity * 100, 2),
        "matches": address_matches,
        "threshold": 80.0
    })

    # Validate Aadhaar Number (digits only, exact match)
    id_aadhaar = get_field_value(id_data, "aadhaar_number")
    form_aadhaar = get_field_value(form_data, "aadhaar_number")
    
    # Clean both Aadhaar numbers
    cleaned_id_aadhaar = clean_aadhaar_number(id_aadhaar)
    cleaned_form_aadhaar = clean_aadhaar_number(form_aadhaar)
    
    aadhaar_matches = cleaned_id_aadhaar == cleaned_form_aadhaar
    aadhaar_similarity = 1.0 if aadhaar_matches else 0.0
    
    if not aadhaar_matches:
        all_match = False
    
    validation_results.append({
        "field": "Aadhaar Number",
        "id_value": f"{id_aadhaar} → {cleaned_id_aadhaar}",
        "form_value": f"{form_aadhaar} → {cleaned_form_aadhaar}",
        "similarity": round(aadhaar_similarity * 100, 2),
        "matches": aadhaar_matches,
        "threshold": 100.0
    })

    return {
        "status": "passed" if all_match else "failed",
        "validation_details": validation_results,
        "summary": "All critical fields meet validation rules" if all_match else "Some fields did not meet validation rules"
    }
