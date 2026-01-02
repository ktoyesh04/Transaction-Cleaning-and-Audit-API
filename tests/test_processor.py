import pandas as pd
import tempfile
import os

from app.services.processor import validate_and_clean


def test_validate_and_clean_pipeline():
    df = pd.DataFrame([
        {"account_id": 1, "amount": "1.5L", "date": "01/01/2024", "customer_name": "Amit"},
        {"account_id": None, "amount": "500", "date": "01/01/2024", "customer_name": "Ravi"},
        {"account_id": 2, "amount": "-100", "date": "01/01/2024", "customer_name": "Neha"},
    ])

    with tempfile.TemporaryDirectory() as tmpdir:
        cleaned, flagged, rejected = validate_and_clean(df, tmpdir)

    assert len(cleaned) == 0
