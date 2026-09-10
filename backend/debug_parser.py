"""
Debug Parser Agent - trace where medications are being lost
"""

import asyncio
from app.agents.parser_agent import parser_agent
from app.utils.logger import logger

SAMPLE_TEXT = """
Dr. Smith Clinic
Date: 08/15/2024
[PATIENT_NAME_MASKED], [DOB_MASKED]

Rx:
1. Dolo 650mg - take 1 tablet every after food 8 hours as needed for pain, for 5 days
2. Metformin 500mg - Take 1 tablet twice daily with meals, for diabetes management
3. Atorvastatin 20mg - Take 1 tablet at bedtime, for 90 days
4. Aspirin 81mg - Take 1 tablet daily for heart health
"""

async def debug_parser():
    print("\n" + "="*70)
    print("PARSER AGENT DEBUG")
    print("="*70)
    
    print(f"\nInput text ({len(SAMPLE_TEXT)} chars):")
    print(SAMPLE_TEXT)
    
    print("\n" + "="*70)
    print("EXPECTED MEDICATIONS:")
    print("="*70)
    expected = [
        ("Dolo", "650mg"),
        ("Metformin", "500mg"),
        ("Atorvastatin", "20mg"),
        ("Aspirin", "81mg"),
    ]
    for i, (name, strength) in enumerate(expected, 1):
        print(f"  {i}. {name} {strength}")
    
    print("\n" + "="*70)
    print("PARSING WITH PARSER AGENT:")
    print("="*70)
    
    medications, has_unclear, uncertainty = await parser_agent.parse_prescription(SAMPLE_TEXT)
    
    print(f"\nFOUND {len(medications)} MEDICATIONS:")
    for i, med in enumerate(medications, 1):
        print(f"\n  {i}. {med.name}")
        print(f"     Strength: {med.strength}")
        print(f"     Dosage: {med.dosage}")
        print(f"     Frequency: {med.frequency}")
        print(f"     Confidence: {med.confidence}")
    
    print("\n" + "="*70)
    print("MISSING MEDICATIONS:")
    print("="*70)
    found_names = {m.name.lower() for m in medications}
    for name, strength in expected:
        if not any(name.lower() in fn for fn in found_names):
            print(f"  ✗ {name} {strength} - NOT FOUND")
        else:
            print(f"  ✓ {name} {strength} - found")
    
    # Now test the clinical entity parser directly
    print("\n" + "="*70)
    print("DIRECT CLINICAL ENTITY PARSER TEST:")
    print("="*70)
    meds_direct, _, _ = parser_agent._clinical_entity_parse(SAMPLE_TEXT)
    print(f"\nDirect parser found {len(meds_direct)} medications:")
    for med in meds_direct:
        print(f"  - {med.name} {med.strength}")

if __name__ == "__main__":
    asyncio.run(debug_parser())
