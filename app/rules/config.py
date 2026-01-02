import json
from pathlib import Path


CONFIG_PATH = Path(__file__).parent.parent / "config"/"rules.json"

with open(CONFIG_PATH) as fp:
	RULES = json.load(fp)
	# print(RULES)
