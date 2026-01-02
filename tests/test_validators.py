import json

from app.rules.validators import clean_amount, clean_name


def test_amount_lakh_conversion():
    amount, audit = clean_amount("1.5L", row_number=1)
    assert amount == 150000
    assert audit is not None
    
    assert audit[0]["rule_code"] == "AMOUNT_LAKH_CONVERSION"


def test_negative_amount_rejected():
    amount, audit = clean_amount("-500", row_number=2)

    assert amount is None
    assert audit[0]["rule_code"] == "NEGATIVE_AMOUNT"


def test_name_with_digits_rejected():
    name, _ = clean_name("Rahul123", row_number=1)

    assert name is None


def test_name_normalisation():
    name, _ = clean_name("  rahul   kumar ", 1)

    assert name == "Rahul Kumar"
