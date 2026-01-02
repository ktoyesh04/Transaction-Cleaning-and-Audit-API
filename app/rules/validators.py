
from dateutil import parser
from app.rules.config import RULES

def clean_account_id(value, row_number):
    audit_events = []
    original = value

    try:
        value = int(value)

        if value < RULES["account_id"]["min_value"]:
            audit_events.append({
                "row_number": row_number,
                "status": "REJECT",
                "rule_code": "ACCOUNT_ID_TOO_SMALL",
                "field": "account_id",
                "original_value": original,
                "new_value": None,
                "message": "Account ID below minimum value"
            })
            return None, audit_events

        return value, audit_events

    except (ValueError, TypeError):
        audit_events.append({
            "row_number": row_number,
            "status": "REJECT",
            "rule_code": "INVALID_ACCOUNT_ID",
            "field": "account_id",
            "original_value": original,
            "new_value": None,
            "message": "Account ID must be integer"
        })
        return None, audit_events
    

def clean_amount(value, row_number):
    original = value
    audit_events = []

    value = str(value).strip()

    if "₹" in value:
        value = value.replace("₹", "")
        audit_events.append({
            "row_number": row_number,
            "status": "FIXED",
            "rule_code": "REMOVE_CURRENCY_SYMBOL",
            "field": "amount",
            "original_value": original,
            "new_value": value,
            "message": "Removed currency symbol"
        })

    if "," in value:
        new_value = value.replace(",", "")
        audit_events.append({
            "row_number": row_number,
            "status": "FIXED",
            "rule_code": "REMOVE_COMMAS",
            "field": "amount",
            "original_value": value,
            "new_value": new_value,
            "message": "Removed thousand separators"
        })
        value = new_value

    try:
        if value.endswith("L"):
            amount = float(value[:-1]) * 100000
            audit_events.append({
                "row_number": row_number,
                "status": "FIXED",
                "rule_code": "AMOUNT_LAKH_CONVERSION",
                "field": "amount",
                "original_value": original,
                "new_value": amount,
                "message": "Converted lakh notation to number"
            })
        else:
            amount = float(value)

        if not RULES["amount"]["allow_negative"] and amount < 0:
            audit_events.append({
                "row_number": row_number,
                "status": "REJECT",
                "rule_code": "NEGATIVE_AMOUNT",
                "field": "amount",
                "original_value": original,
                "new_value": None,
                "message": "Negative amount not allowed"
            })
            return None, audit_events

        return amount, audit_events

    except ValueError:
        audit_events.append({
            "row_number": row_number,
            "status": "REJECT",
            "rule_code": "INVALID_AMOUNT",
            "field": "amount",
            "original_value": original,
            "new_value": None,
            "message": "Amount parsing failed"
        })
        return None, audit_events


def clean_date(value, row_number):
    try:
        return parser.parse(
            value,
            dayfirst=RULES["date"]["day_first"]
        ), []
    except (ValueError, TypeError):
        return None, {
            "row_number": row_number,
            "status": "REJECT",
            "rule_code": "INVALID_DATE",
            "field": "date",
            "original_value": value,
            "new_value": None,
            "message": "Date parsing failed"
        }
    
    
def clean_name(value, row_number):
    audit_events = []
    original = value

    if not isinstance(value, str):
        audit_events.append({
            "row_number": row_number,
            "status": "REJECT",
            "rule_code": "INVALID_NAME_TYPE",
            "field": "customer_name",
            "original_value": original,
            "new_value": None,
            "message": "Name must be a string"
        })
        return None, audit_events

    if not RULES["name"]["allow_digits"]:
        if any(char.isdigit() for char in value):
            audit_events.append({
                "row_number": row_number,
                "status": "REJECT",
                "rule_code": "DIGITS_IN_NAME",
                "field": "customer_name",
                "original_value": original,
                "new_value": None,
                "message": "Digits not allowed in name"
            })
            return None, audit_events

    cleaned = " ".join(value.split()).title()

    if cleaned != original:
        audit_events.append({
            "row_number": row_number,
            "status": "FIXED",
            "rule_code": "NORMALIZE_NAME",
            "field": "customer_name",
            "original_value": original,
            "new_value": cleaned,
            "message": "Normalized spacing and casing"
        })

    return cleaned, audit_events
