import asyncio
import pytest
from app.agents.phi_agent import phi_agent

def test_phi_rule_based_masking():
    raw_text = (
        "Patient: Robert Johnson, DOB: 04/15/1982\n"
        "Phone: 555-123-4567\n"
        "Email: robert.j@example.com\n"
        "Rx: Amoxicillin 500mg 1 cap PO TID"
    )
    sanitized, report = asyncio.run(phi_agent.sanitize_prescription(raw_text))
    
    assert "[PATIENT_NAME_MASKED]" in sanitized or "[PATIENT" in sanitized
    assert "[DOB_MASKED]" in sanitized or "[DATE" in sanitized
    assert "[PHONE_MASKED]" in sanitized
    assert "[EMAIL_MASKED]" in sanitized
    assert "Amoxicillin 500mg" in sanitized
    assert report.sanitized is True
    assert report.masked_items_count >= 3
