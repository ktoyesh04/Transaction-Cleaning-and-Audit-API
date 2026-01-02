import logging
import pandas as pd

from app.rules.config import RULES
from app.rules.validators import (
	clean_account_id,
	clean_amount,
	clean_date,
	clean_name
)
from app.services.audit import write_audit_events


def validate_and_clean(df: pd.DataFrame, job_path=None):
	cleaned, flagged, rejected = [], [], []
	audit_events = []
	
	for row_num, row in df.iterrows():
		record = {}
		
		record["account_id"], audits = clean_account_id(row["account_id"], row_num)
		audit_events.extend(audits)
		if record["account_id"] is None:
			rejected.append(row.to_dict())
			continue
		
		record["amount"], audits = clean_amount(row["amount"], row_num)
		audit_events.extend(audits)
		if record["amount"] is None:
			rejected.append(row.to_dict())
			continue
			
		if record["amount"] > RULES["amount"]["high_value_threshold"]:
			record["flag_reason"] = "HIGH_AMOUNT"
			audit_events.append({
            "row_number": row_num,
            "status": "FLAG",
            "rule_code": "HIGH_AMOUNT",
            "field": "amount",
            "value": row["amount"],
            "message": "Flagged the high amount"
        })
			
		record["date"], audits = clean_date(row["date"], row_num)
		audit_events.extend(audits)
		if record["date"] is None:
			rejected.append(row.to_dict())
			continue
		
		record["name"] = clean_name(row["customer_name"], row_num)
		audit_events.extend(audits)
		if record["name"] is None:
			rejected.append(row.to_dict())
			continue
		
		if "flag_reason" in record:
			flagged.append(record)
		else:
			cleaned.append(record)
	
	if job_path:
		write_audit_events(job_path, audit_events)
	return (
		pd.DataFrame(cleaned),
		pd.DataFrame(flagged),
		pd.DataFrame(rejected),
	)
	