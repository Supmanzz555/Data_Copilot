# app/pii_masking.py
import re

def mask_email(email: str) -> str:
    """Mask email addresses: john.doe@example.com -> j***@example.com"""
    if not email or '@' not in email:
        return email
    local, domain = email.split('@', 1)
    masked_local = local[0] + '***' if len(local) > 1 else '***'
    return f"{masked_local}@{domain}"

def mask_name(name: str) -> str:
    """Mask names: John Doe -> J*** D***"""
    if not name:
        return name
    parts = name.split()
    masked_parts = [p[0] + '***' if len(p) > 1 else '***' for p in parts]
    return ' '.join(masked_parts)

def mask_pii_in_dict(data: dict) -> dict:
    """Recursively mask PII fields in a dictionary"""
    masked = {}
    for key, value in data.items():
        if key in ['email', 'customer_email']:
            masked[key] = mask_email(str(value)) if value else value
        elif key in ['name', 'customer_name']:
            masked[key] = mask_name(str(value)) if value else value
        elif isinstance(value, dict):
            masked[key] = mask_pii_in_dict(value)
        elif isinstance(value, list):
            masked[key] = [mask_pii_in_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            masked[key] = value
    return masked

def mask_pii_in_results(results: list) -> list:
    """Mask PII in a list of result dictionaries"""
    return [mask_pii_in_dict(row) for row in results]

