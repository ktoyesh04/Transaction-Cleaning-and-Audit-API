
import json
import os.path
from datetime import datetime


def write_audit_events(path, events):
	with open(os.path.join(path, "audit.json"), "w+") as fp:
		for event in events:
			event["timestamp"] = datetime.utcnow().isoformat()
			fp.write(json.dumps(event) + "\n")


def write_master_audit(event):
	event["timestamp"] = datetime.utcnow().isoformat()
	with open(r"data\audit_master.jsonl", "a") as fp:
		fp.write(json.dumps(event) + "\n")
