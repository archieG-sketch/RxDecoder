"""
Agent Testing Suite - Test each agent individually with sample inputs
Usage: python test_agents.py
"""

import asyncio
import json
from pathlib import Path
from app.config import settings
from app.utils.logger import logger

# Import all agents
from app.agents.vision_agent import vision_agent
from app.agents.phi_agent import phi_agent
from app.agents.parser_agent import parser_agent
from app.agents.med_info_agent import med_info_agent
from app.agents.safety_agent import safety_agent
from app.agents.explanation_agent import explanation_agent

# Sample test data
SAMPLE_RAW_TEXT = """
Dr. Smith Clinic
Date: 08/15/2024
Patient: Archana Yujeed, DOB: 01/01/1980

Rx:
1. Dolo 650mg - take 1 tablet every after food 8 hours as needed for pain, for 5 days
2. Metformin 500mg - Take 1 tablet twice daily with meals, for diabetes management
3. Atorvastatin 20mg - Take 1 tablet at bedtime, for 90 days
4. Aspirin 81mg - Take 1 tablet daily for heart health

Dr. Sarah Smith, MD
Signature: [Doctor signature]
"""

SAMPLE_SANITIZED_TEXT = """
Clinic
Date: 08/15/2024

Rx:
1. Dolo 650mg - take 1 tablet every after food 8 hours as needed for pain, for 5 days
2. Metformin 500mg - Take 1 tablet twice daily with meals, for diabetes management
3. Atorvastatin 20mg - Take 1 tablet at bedtime, for 90 days
4. Aspirin 81mg - Take 1 tablet daily for heart health
"""

async def test_vision_agent():
    """Test Vision Agent with a sample prescription image"""
    print("\n" + "="*60)
    print("TESTING: Vision Agent (OCR Extraction)")
    print("="*60)
    
    # Try to load a test image if available
    test_image_path = Path("tests/sample_prescription.png")
    if test_image_path.exists():
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()
        print(f"✓ Using test image: {test_image_path}")
        
        result = await vision_agent.extract_prescription_text(image_bytes, "image/png")
        print(f"\nVision Agent Output:")
        print(f"  Document Type: {result.get('document_type')}")
        print(f"  Legibility Score: {result.get('legibility_score')}")
        print(f"  Has Unclear: {result.get('has_unclear_handwriting')}")
        print(f"  Raw Text Preview: {result.get('raw_transcription', '')[:200]}...")
        print(f"  Medications Found: {len(result.get('extracted_sections', {}).get('medication_lines', []))}")
        return result.get('raw_transcription', '')
    else:
        print(f"✗ No test image found at {test_image_path}")
        print(f"  Using sample text instead for downstream testing")
        return SAMPLE_RAW_TEXT

async def test_phi_agent(raw_text: str):
    """Test PHI Agent sanitization"""
    print("\n" + "="*60)
    print("TESTING: PHI Agent (Sanitization)")
    print("="*60)
    
    print(f"Input text ({len(raw_text)} chars):")
    print(f"  {raw_text[:150]}...")
    
    sanitized_text, phi_report = await phi_agent.sanitize_prescription(raw_text)
    
    print(f"\nPHI Agent Output:")
    print(f"  Sanitized text ({len(sanitized_text)} chars):")
    print(f"    {sanitized_text[:150]}...")
    print(f"  PHI Report:")
    if phi_report:
        print(f"    Sanitized: {phi_report.sanitized}")
        print(f"    Masked Items: {phi_report.masked_items_count}")
        print(f"    Masked Types: {phi_report.masked_types}")
        print(f"    Summary: {phi_report.summary}")
    else:
        print(f"    (No PHI detected)")
    
    return sanitized_text

async def test_parser_agent(sanitized_text: str):
    """Test Parser Agent medication extraction"""
    print("\n" + "="*60)
    print("TESTING: Parser Agent (Medication Parsing)")
    print("="*60)
    
    print(f"Input text ({len(sanitized_text)} chars):")
    print(f"  {sanitized_text[:150]}...")
    
    medications, has_unclear, uncertainty = await parser_agent.parse_prescription(sanitized_text)
    
    print(f"\nParser Agent Output:")
    print(f"  Medications Found: {len(medications)}")
    for med in medications:
        print(f"    - {med.name} {med.strength} | {med.frequency} | Route: {med.route} | Confidence: {med.confidence}")
    print(f"  Has Unclear: {has_unclear}")
    if uncertainty:
        print(f"  Uncertainty: {uncertainty[:100]}")
    
    return medications

async def test_med_info_agent(medications):
    """Test MedInfo Agent clinical enrichment"""
    print("\n" + "="*60)
    print("TESTING: MedInfo Agent (Clinical Enrichment)")
    print("="*60)
    
    print(f"Input: {len(medications)} medications")
    
    enriched = await med_info_agent.enrich_medications(medications)
    
    print(f"\nMedInfo Agent Output:")
    print(f"  Enriched Medications: {len(enriched)}")
    for med in enriched:
        print(f"    - {med.name}")
        if med.analysis:
            print(f"      Uses: {med.analysis.uses_summary[:80] if med.analysis.uses_summary else 'N/A'}...")
            print(f"      Mechanism: {med.analysis.mechanism_summary[:80] if med.analysis.mechanism_summary else 'N/A'}...")
            print(f"      Common Side Effects: {len(med.analysis.common_side_effects) if med.analysis.common_side_effects else 0} noted")
            print(f"      Important Warnings: {len(med.analysis.important_warnings) if med.analysis.important_warnings else 0} noted")
    
    return enriched

async def test_safety_agent(enriched_medications):
    """Test Safety Agent for drug interactions"""
    print("\n" + "="*60)
    print("TESTING: Safety Agent (Interaction Check)")
    print("="*60)
    
    print(f"Input: {len(enriched_medications)} medications")
    
    interaction_check, safety_unclear, warning = await safety_agent.evaluate_safety(
        enriched_medications, 
        has_unclear_handwriting=False
    )
    
    print(f"\nSafety Agent Output:")
    print(f"  Has Interactions: {interaction_check.has_potential_interactions}")
    print(f"  Summary: {interaction_check.summary}")
    print(f"  Interactions Found: {len(interaction_check.interactions)}")
    for interaction in interaction_check.interactions[:5]:
        print(f"    - {interaction.medications_involved}: {interaction.severity}")
        print(f"      {interaction.recommendation[:100]}...")
    print(f"  Verification Advice: {interaction_check.verification_advice[:100]}...")
    print(f"  Has Unclear: {safety_unclear}")
    if warning:
        print(f"  Warning: {warning[:100]}")
    
    return interaction_check

async def test_explanation_agent(enriched_medications):
    """Test Explanation Agent for patient-friendly output"""
    print("\n" + "="*60)
    print("TESTING: Explanation Agent (Patient Summary)")
    print("="*60)
    
    print(f"Input: {len(enriched_medications)} medications")
    
    simple_exp, detailed_exp, checklist, tts_script = await explanation_agent.generate_explanations_and_checklist(
        enriched_medications
    )
    
    print(f"\nExplanation Agent Output:")
    print(f"  Simple Explanation: {len(simple_exp)} chars")
    print(f"    {simple_exp[:150]}...")
    print(f"  Detailed Explanation: {len(detailed_exp)} chars")
    print(f"  Checklist Items: {len(checklist)}")
    for item in checklist[:3]:
        print(f"    - {item.medication_name} ({item.time_of_day}): {item.instructions[:60]}...")
        print(f"      Dosage: {item.dosage} | Food: {item.food_relation}")
    print(f"  TTS Script: {len(tts_script)} chars")
    print(f"    {tts_script[:150]}...")
    
    return simple_exp, detailed_exp, checklist

async def main():
    print("\n" + "="*60)
    print("ADK AGENT TEST SUITE")
    print("="*60)
    print(f"Testing all 6 agents individually")
    print(f"Gemini API Key: {'✓ Configured' if settings.gemini_api_key else '✗ Missing'}")
    
    try:
        # Stage 1: Vision
        raw_text = await test_vision_agent()
        
        # Stage 2: PHI
        sanitized_text = await test_phi_agent(raw_text)
        
        # Stage 3: Parser
        medications = await test_parser_agent(sanitized_text)
        
        # Stage 4: MedInfo
        enriched = await test_med_info_agent(medications)
        
        # Stage 5: Safety
        interactions = await test_safety_agent(enriched)
        
        # Stage 6: Explanation
        await test_explanation_agent(enriched)
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        logger.exception("Agent test failed")

if __name__ == "__main__":
    asyncio.run(main())
