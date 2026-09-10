"""
Sample Prescriptions Service
Provides realistic, high-fidelity sample prescriptions for demonstration, testing, and exploration.
"""

from typing import Dict, Any, List
from app.models.schemas import (
    PrescriptionDecodeResponse, MedicationItem, MedicationAnalysis,
    InteractionCheck, InteractionItem, MedicationChecklistItem, PHISanitizationReport
)

SAMPLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "sample_handwritten_amoxicillin": {
        "id": "sample_handwritten_amoxicillin",
        "title": "Messy Handwritten Rx (Amoxicillin & Ibuprofen)",
        "category": "Handwritten",
        "description": "Doctor's handwritten script for acute sinus infection with antibiotic and pain reliever.",
        "image_url": "/samples/handwritten_rx_1.png",
        "raw_text": "Metro Family Clinic\nDr. Marcus Vance, MD (Lic #984210)\nPt: Robert Miller, Age: 42\nDate: 10/14/2026\n\nRx:\n1. Amoxicillin 500mg\n   Sig: 1 cap PO TID PC x 10d\n   Disp: #30\n\n2. Ibuprofen 400mg\n   Sig: 1 tab PO Q6H PRN pain\n   Disp: #20\n\nRefills: 0\nSig: M. Vance, MD",
        "decoded_response": PrescriptionDecodeResponse(
            session_id="sample_session_1",
            original_file_name="sample_handwritten_amoxicillin.png",
            file_type="image",
            phi_report=PHISanitizationReport(
                sanitized=True,
                masked_items_count=4,
                masked_types=["Patient Name", "Age", "Doctor License Number", "Date"],
                sanitized_text_preview="Metro Family Clinic\nDr. Marcus Vance, MD [DOCTOR_ID_MASKED]\nPt: [PATIENT_NAME_MASKED], Age: [AGE_MASKED]\nDate: [DATE_MASKED]\n\nRx:\n1. Amoxicillin 500mg...",
                summary="Protected Health Information (PHI) masked 4 sensitive identifiers prior to clinical AI processing."
            ),
            raw_ocr_summary="Handwritten clinical prescription transcribed with high legibility on medication sig.",
            medications=[
                MedicationItem(
                    id="med_sample_1",
                    name="Amoxicillin",
                    generic_name="Amoxicillin",
                    brand_name="Amoxil",
                    strength="500 mg",
                    dosage="1 capsule",
                    frequency="Three times a day (every 8 hours)",
                    route="Oral",
                    duration="10 days",
                    timing_instructions="Morning, Afternoon, and Night (every 8 hours)",
                    food_instructions="Take after eating meals with a full glass of water",
                    additional_notes="Take all 10 days of medication until finished, even if you feel completely cured.",
                    confidence="high",
                    analysis=MedicationAnalysis(
                        uses_summary="Amoxicillin is a penicillin-based antibiotic commonly prescribed to treat bacterial infections of the sinuses, throat, lungs, or ears.",
                        how_to_take_plain="Take 1 capsule by mouth three times each day (for example: at 8 AM, 4 PM, and midnight). Always take it right after eating food.",
                        common_side_effects=["Mild stomach ache or cramping", "Loose stools or mild diarrhea", "Nausea", "Mild headache"],
                        important_warnings=[
                            "Complete the entire 10-day course. Stopping early can allow surviving bacteria to become resistant.",
                            "Do not share this antibiotic with anyone else.",
                            "Drink plenty of water throughout the day."
                        ],
                        serious_symptoms=[
                            "Hives, intense itching, or severe skin rash",
                            "Swelling of the lips, face, throat, or tongue",
                            "Difficulty breathing or swallowing",
                            "Severe, watery diarrhea occurring during or after treatment"
                        ],
                        substance_allergy_warnings=["Do NOT take if you are allergic to penicillin or cephalosporin antibiotics."],
                        mechanism_summary="Broad-spectrum penicillin that destroys bacteria by inhibiting cell wall synthesis."
                    )
                ),
                MedicationItem(
                    id="med_sample_2",
                    name="Ibuprofen",
                    generic_name="Ibuprofen",
                    brand_name="Advil / Motrin",
                    strength="400 mg",
                    dosage="1 tablet",
                    frequency="Every 6 hours as needed for pain or fever",
                    route="Oral",
                    duration="As needed for pain (up to 5-7 days)",
                    timing_instructions="Only take when experiencing pain or fever, waiting at least 6 hours between doses",
                    food_instructions="Always take with meals, a snack, or a glass of milk",
                    additional_notes="Do not take on an empty stomach. Do not exceed 1200 mg in 24 hours.",
                    confidence="high",
                    analysis=MedicationAnalysis(
                        uses_summary="Ibuprofen is an anti-inflammatory pain reliever that reduces swelling, headache, body aches, sinus pain, and fever.",
                        how_to_take_plain="Take 1 tablet by mouth when you have pain. Wait at least 6 hours before taking another. Always eat something first.",
                        common_side_effects=["Heartburn or indigestion", "Mild upset stomach", "Dizziness", "Mild drowsiness"],
                        important_warnings=[
                            "Never take on an empty stomach — always take with food or milk to safeguard your stomach lining.",
                            "Do not take other NSAID pain relievers (like Naproxen or Aspirin) at the same time.",
                            "Avoid alcohol while taking this medicine to lower the risk of stomach bleeding."
                        ],
                        serious_symptoms=[
                            "Black, tarry stools or vomiting material that looks like coffee grounds",
                            "Severe, sharp stomach pain",
                            "Sudden chest pain or shortness of breath",
                            "Swelling of ankles or sudden weight gain"
                        ],
                        substance_allergy_warnings=["Avoid if you have a known allergy to aspirin or other NSAIDs, or active stomach ulcers."],
                        mechanism_summary="Nonsteroidal anti-inflammatory drug (NSAID) that inhibits COX-1 and COX-2 enzymes to reduce inflammation."
                    )
                )
            ],
            interactions=InteractionCheck(
                has_potential_interactions=False,
                summary="No severe direct contraindications between Amoxicillin and Ibuprofen. They are frequently prescribed together for sinus infections.",
                interactions=[
                    InteractionItem(
                        severity="caution",
                        medications_involved=["Amoxicillin", "Ibuprofen"],
                        description="Both medicines can cause mild stomach irritation if taken without food.",
                        recommendation="Take both medications with food or after a substantial meal."
                    )
                ],
                verification_advice="Always inform your pharmacist if you take daily supplements or other prescription medicines."
            ),
            checklist=[
                MedicationChecklistItem(
                    id="chk_s1_1",
                    time_of_day="Morning",
                    medication_name="Amoxicillin 500mg",
                    dosage="1 capsule",
                    instructions="Take dose 1 of 3",
                    food_relation="After breakfast with water",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s1_2",
                    time_of_day="Afternoon",
                    medication_name="Amoxicillin 500mg",
                    dosage="1 capsule",
                    instructions="Take dose 2 of 3 (approx. 8 hours after morning dose)",
                    food_relation="After lunch or afternoon snack",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s1_3",
                    time_of_day="Evening",
                    medication_name="Amoxicillin 500mg",
                    dosage="1 capsule",
                    instructions="Take dose 3 of 3",
                    food_relation="After dinner",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s1_4",
                    time_of_day="As Needed",
                    medication_name="Ibuprofen 400mg",
                    dosage="1 tablet",
                    instructions="Only if feeling pain or fever (max 3 times/day, 6 hrs apart)",
                    food_relation="With food or milk",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s1_5",
                    time_of_day="Morning",
                    medication_name="Daily Antibiotic Reminder",
                    dosage="Course Completion",
                    instructions="Remember to finish all 10 days of Amoxicillin even when feeling better.",
                    food_relation="All day",
                    completed=False
                )
            ],
            simple_explanation=(
                "You have been prescribed two common medications to help clear your infection and relieve discomfort:\n\n"
                "1. **Amoxicillin 500 mg** is an antibiotic that fights the bacteria causing your infection. Take 1 capsule three times a day after meals for the full 10 days. It is very important to finish all pills even if you feel completely cured early.\n\n"
                "2. **Ibuprofen 400 mg** is a pain reliever. Take 1 tablet only when you feel pain or fever, always after eating. Make sure to wait at least 6 hours between doses."
            ),
            detailed_explanation=(
                "**Prescription Regimen Summary**:\n"
                "• **Amoxicillin 500 mg cap PO TID PC x 10d**: Therapeutic antimicrobial course targeting susceptible respiratory/sinus flora. Peptidoglycan cell wall synthesis inhibitor.\n"
                "• **Ibuprofen 400 mg tab PO Q6H PRN**: Analgesic and antipyretic therapy via reversible COX-1/COX-2 inhibition. Administer with food to mitigate gastric mucosal irritation."
            ),
            has_uncertain_handwriting=False,
            uncertainty_warning=None,
            tts_narration_script=(
                "Hello. Welcome to your RxDecoder prescription guide. "
                "You have two medicines. "
                "First, Amoxicillin 500 milligrams: take one capsule three times a day after eating, and finish all ten days. "
                "Second, Ibuprofen 400 milligrams: take one tablet every six hours as needed for pain, always with food. "
                "If you experience any rash or difficulty breathing, contact your doctor immediately."
            ),
            processing_time_ms=842.0
        )
    },
    "sample_complex_multi_drug": {
        "id": "sample_complex_multi_drug",
        "title": "Multi-Med Chronic Care (Metformin, Lisinopril, Atorvastatin)",
        "category": "Printed / Chronic Care",
        "description": "Standard printed multi-medication regimen for Type 2 Diabetes, Blood Pressure, and Cholesterol.",
        "image_url": "/samples/printed_rx_chronic.png",
        "raw_text": "Valley Internal Medicine\nDr. Elena Rostova, MD\nPt: Eleanor Davies, DOB: 03/22/1954\n\n1. Metformin 850mg tab - 1 tab PO BID with meals (#60)\n2. Lisinopril 20mg tab - 1 tab PO QAM (#30)\n3. Atorvastatin 40mg tab - 1 tab PO QHS (#30)",
        "decoded_response": PrescriptionDecodeResponse(
            session_id="sample_session_2",
            original_file_name="sample_complex_multi_drug.png",
            file_type="image",
            phi_report=PHISanitizationReport(
                sanitized=True,
                masked_items_count=3,
                masked_types=["Patient Name", "Date of Birth", "Clinic ID"],
                sanitized_text_preview="Valley Internal Medicine\nDr. Elena Rostova, MD\nPt: [PATIENT_NAME_MASKED], DOB: [DOB_MASKED]\n\n1. Metformin 850mg tab...",
                summary="Protected Health Information masked 3 patient identifiers before AI evaluation."
            ),
            raw_ocr_summary="Printed multi-medication prescription transcribed with 100% legibility.",
            medications=[
                MedicationItem(
                    id="med_sample_2_1",
                    name="Metformin",
                    generic_name="Metformin HCl",
                    brand_name="Glucophage",
                    strength="850 mg",
                    dosage="1 tablet",
                    frequency="Twice daily (morning and evening)",
                    route="Oral",
                    duration="30 days (Ongoing)",
                    timing_instructions="Take 1 tablet with breakfast and 1 tablet with dinner",
                    food_instructions="Always take with meals to reduce stomach discomfort",
                    additional_notes="Avoid excessive alcohol consumption.",
                    confidence="high",
                    analysis=MedicationAnalysis(
                        uses_summary="Metformin helps lower blood sugar levels in people with Type 2 diabetes by improving how your body responds to insulin.",
                        how_to_take_plain="Take 1 tablet by mouth twice a day with meals (breakfast and dinner). Swallow whole with water.",
                        common_side_effects=["Mild nausea or metallic taste", "Stomach upset or gas", "Soft stools during initial weeks"],
                        important_warnings=[
                            "Always take with meals to minimize stomach upset.",
                            "Avoid heavy alcohol drinking while on Metformin.",
                            "Inform your doctor if you are scheduled for medical imaging with contrast dye."
                        ],
                        serious_symptoms=[
                            "Unusual extreme tiredness, severe muscle pain, or trouble breathing (rare signs of lactic acidosis)",
                            "Severe, persistent vomiting or stomach pain"
                        ],
                        substance_allergy_warnings=["Inform your doctor if you have severe kidney impairment."],
                        mechanism_summary="Biguanide antidiabetic agent that decreases hepatic glucose production and increases peripheral insulin sensitivity."
                    )
                ),
                MedicationItem(
                    id="med_sample_2_2",
                    name="Lisinopril",
                    generic_name="Lisinopril",
                    brand_name="Prinivil / Zestril",
                    strength="20 mg",
                    dosage="1 tablet",
                    frequency="Once daily in the morning",
                    route="Oral",
                    duration="30 days (Ongoing)",
                    timing_instructions="Take every morning around the same time",
                    food_instructions="Can be taken with or without food",
                    additional_notes="Stand up slowly when getting out of bed to prevent dizziness.",
                    confidence="high",
                    analysis=MedicationAnalysis(
                        uses_summary="Lisinopril is an ACE inhibitor used to lower high blood pressure and protect your heart and kidneys.",
                        how_to_take_plain="Take 1 tablet by mouth every morning with a glass of water. Try to take it at the same time each day.",
                        common_side_effects=["Mild dizziness or lightheadedness", "Persistent dry cough", "Mild headache"],
                        important_warnings=[
                            "Do not use potassium supplements or salt substitutes without asking your doctor.",
                            "Get up slowly from sitting or lying down to prevent feeling faint.",
                            "Do NOT take if pregnant."
                        ],
                        serious_symptoms=[
                            "Swelling of the face, lips, tongue, or throat (angioedema)",
                            "Fainting or severe dizziness",
                            "Yellowing of skin or eyes"
                        ],
                        substance_allergy_warnings=["Avoid if you have ever had a swelling reaction (angioedema) to an ACE inhibitor."],
                        mechanism_summary="Angiotensin-converting enzyme (ACE) inhibitor that reduces vasoconstriction and aldosterone secretion."
                    )
                ),
                MedicationItem(
                    id="med_sample_2_3",
                    name="Atorvastatin",
                    generic_name="Atorvastatin Calcium",
                    brand_name="Lipitor",
                    strength="40 mg",
                    dosage="1 tablet",
                    frequency="Once daily at bedtime",
                    route="Oral",
                    duration="30 days (Ongoing)",
                    timing_instructions="Take every night at bedtime",
                    food_instructions="Can be taken with or without food",
                    additional_notes="Avoid drinking large amounts of grapefruit juice.",
                    confidence="high",
                    analysis=MedicationAnalysis(
                        uses_summary="Atorvastatin is a statin medication that lowers 'bad' LDL cholesterol and triglycerides in your blood to protect against heart attack and stroke.",
                        how_to_take_plain="Take 1 tablet by mouth every evening or bedtime with water.",
                        common_side_effects=["Mild joint or muscle aches", "Mild headache", "Diarrhea or constipation"],
                        important_warnings=[
                            "Avoid drinking large amounts of grapefruit juice (more than 1 quart a day) as it interacts with this medicine.",
                            "Inform your doctor if you experience unexplained muscle soreness."
                        ],
                        serious_symptoms=[
                            "Unexplained muscle pain, tenderness, or weakness, especially with fever or dark tea-colored urine (rhabdomyolysis)",
                            "Upper stomach pain or severe yellowing of eyes"
                        ],
                        substance_allergy_warnings=["Avoid if you have active liver disease."],
                        mechanism_summary="HMG-CoA reductase inhibitor that reduces hepatic cholesterol synthesis."
                    )
                )
            ],
            interactions=InteractionCheck(
                has_potential_interactions=True,
                summary="Standard cardiovascular & metabolic regimen. Moderate precaution regarding blood pressure and potassium levels.",
                interactions=[
                    InteractionItem(
                        severity="caution",
                        medications_involved=["Lisinopril", "Metformin"],
                        description="Ensure proper hydration, especially in warm weather, as both medications rely on healthy kidney function.",
                        recommendation="Drink regular water and schedule routine periodic kidney blood tests with your doctor."
                    )
                ],
                verification_advice="Always carry an updated medication card showing all three daily medications."
            ),
            checklist=[
                MedicationChecklistItem(
                    id="chk_s2_1",
                    time_of_day="Morning",
                    medication_name="Lisinopril 20mg",
                    dosage="1 tablet",
                    instructions="Take 1 tablet with a glass of water",
                    food_relation="With or without breakfast",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s2_2",
                    time_of_day="Morning",
                    medication_name="Metformin 850mg",
                    dosage="1 tablet",
                    instructions="Take morning dose",
                    food_relation="During or right after breakfast",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s2_3",
                    time_of_day="Evening",
                    medication_name="Metformin 850mg",
                    dosage="1 tablet",
                    instructions="Take evening dose",
                    food_relation="During or right after dinner",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s2_4",
                    time_of_day="Bedtime",
                    medication_name="Atorvastatin 40mg",
                    dosage="1 tablet",
                    instructions="Take at night before sleeping",
                    food_relation="With water (avoid grapefruit juice)",
                    completed=False
                )
            ],
            simple_explanation=(
                "Your doctor has prescribed three daily medications to help manage your health:\n\n"
                "• **Morning (Breakfast)**: Take your **Lisinopril 20 mg** (for blood pressure) and your first **Metformin 850 mg** (with your meal for blood sugar).\n"
                "• **Evening (Dinner)**: Take your second **Metformin 850 mg** with your dinner.\n"
                "• **Bedtime**: Take your **Atorvastatin 40 mg** (for cholesterol) right before going to bed."
            ),
            detailed_explanation=(
                "**Comprehensive Chronic Care Regimen**:\n"
                "1. **Metformin HCl 850 mg tab PO BID WF**: Biguanide glycemic control agent.\n"
                "2. **Lisinopril 20 mg tab PO QAM**: ACE-inhibitor antihypertensive agent.\n"
                "3. **Atorvastatin 40 mg tab PO QHS**: HMG-CoA reductase inhibitor lipid-lowering agent."
            ),
            has_uncertain_handwriting=False,
            uncertainty_warning=None,
            tts_narration_script=(
                "Here is your daily medication plan. In the morning with breakfast, take Lisinopril twenty milligrams and Metformin eight hundred and fifty milligrams. "
                "With dinner in the evening, take your second Metformin tablet. "
                "At bedtime, take Atorvastatin forty milligrams. "
                "Always take your Metformin with food to protect your stomach."
            ),
            processing_time_ms=790.0
        )
    },
    "sample_ambiguous_handwriting": {
        "id": "sample_ambiguous_handwriting",
        "title": "Unclear / Ambiguous Handwriting Rx",
        "category": "Unclear / Ambiguous",
        "description": "Prescription with blurred cursive and ambiguous dosage demonstrating safety verification flagging.",
        "image_url": "/samples/ambiguous_handwriting.png",
        "raw_text": "City Urgent Care\nPt: Unreadable\nRx:\n1. [Unclear Cursive: Lev...? / Lor...?] 50mcg - 1 tab PO QAM\n2. Omeprazole 20mg - 1 cap PO QAM AC",
        "decoded_response": PrescriptionDecodeResponse(
            session_id="sample_session_3",
            original_file_name="sample_ambiguous_handwriting.png",
            file_type="image",
            phi_report=PHISanitizationReport(
                sanitized=True,
                masked_items_count=2,
                masked_types=["Patient Name", "Clinic Date"],
                sanitized_text_preview="City Urgent Care\nPt: [PATIENT_NAME_MASKED]\nRx:\n1. [UNCLEAR HANDWRITING]...\n2. Omeprazole 20mg...",
                summary="Protected Health Information masked before AI parsing."
            ),
            raw_ocr_summary="OCR identified low-legibility handwriting on line 1 with potential multiple drug matches.",
            medications=[
                MedicationItem(
                    id="med_sample_3_1",
                    name="Levothyroxine (UNCLEAR - PLEASE VERIFY)",
                    generic_name="Levothyroxine Sodium (Uncertain)",
                    brand_name="Synthroid (Uncertain)",
                    strength="50 mcg (Uncertain)",
                    dosage="1 tablet",
                    frequency="Once daily in the morning",
                    route="Oral",
                    duration="Please verify with pharmacist",
                    timing_instructions="In the morning 30-60 minutes before breakfast",
                    food_instructions="On an empty stomach with plain water only",
                    additional_notes="Handwriting is heavily stylized. Could resemble Levothyroxine 50mcg or Lorazepam.",
                    confidence="unclear",
                    confidence_reason="Medication name could not be identified with sufficient confidence. Please verify this with your pharmacist or doctor.",
                    analysis=MedicationAnalysis(
                        uses_summary="Potential match: Thyroid hormone replacement (Levothyroxine) if verified by pharmacist.",
                        how_to_take_plain="DO NOT TAKE UNTIL CONFIRMED: Show this prescription to your pharmacist for verification.",
                        common_side_effects=["Depends on exact verified medication"],
                        important_warnings=[
                            "CRITICAL SAFETY NOTICE: Do not take this medication until your pharmacist or prescribing doctor confirms the exact name and dosage."
                        ],
                        serious_symptoms=["Contact your doctor if you experience rapid heart rate, confusion, or severe chest pain."],
                        substance_allergy_warnings=["Inform pharmacist of all allergies before filling."],
                        mechanism_summary="Unverified medication entry pending clinical confirmation."
                    )
                ),
                MedicationItem(
                    id="med_sample_3_2",
                    name="Omeprazole",
                    generic_name="Omeprazole",
                    brand_name="Prilosec",
                    strength="20 mg",
                    dosage="1 capsule",
                    frequency="Once daily in the morning",
                    route="Oral",
                    duration="14 to 30 days",
                    timing_instructions="Take 30 to 60 minutes before your first meal of the day",
                    food_instructions="Take on an empty stomach before breakfast",
                    additional_notes="Swallow capsule whole. Do not crush or chew.",
                    confidence="high",
                    analysis=MedicationAnalysis(
                        uses_summary="Omeprazole is a proton pump inhibitor (PPI) that reduces the amount of acid produced in your stomach, treating acid reflux and heartburn.",
                        how_to_take_plain="Take 1 capsule by mouth every morning 30 to 60 minutes before breakfast with a glass of water.",
                        common_side_effects=["Mild headache", "Stomach pain", "Mild nausea or diarrhea"],
                        important_warnings=[
                            "Take before your first meal of the day for maximum effectiveness.",
                            "Do not crush or chew the capsules; swallow whole."
                        ],
                        serious_symptoms=["Severe stomach cramps with watery diarrhea", "Joint pain with skin rash on cheeks or arms"],
                        substance_allergy_warnings=["Avoid if allergic to omeprazole or other PPI medications."],
                        mechanism_summary="Proton pump inhibitor (PPI) that irreversibly inhibits the H+/K+ ATPase pump in gastric parietal cells."
                    )
                )
            ],
            interactions=InteractionCheck(
                has_potential_interactions=True,
                summary="Safety flag: One medication has uncertain handwriting. Interaction check will be complete once the pharmacist confirms the first item.",
                interactions=[
                    InteractionItem(
                        severity="high",
                        medications_involved=["Unverified Item 1", "Omeprazole"],
                        description="If Item 1 is Levothyroxine, Omeprazole reduces stomach acid which can decrease Levothyroxine absorption.",
                        recommendation="Space Levothyroxine and acid reducers at least 4 hours apart after pharmacist confirmation."
                    )
                ],
                verification_advice="Take the physical prescription to your pharmacy for immediate clarification."
            ),
            checklist=[
                MedicationChecklistItem(
                    id="chk_s3_1",
                    time_of_day="Morning",
                    medication_name="⚠️ Unclear Medication Name",
                    dosage="50 mcg (Uncertain)",
                    instructions="DO NOT TAKE YET: Have your pharmacist verify the doctor's handwriting.",
                    food_relation="Requires Verification",
                    requires_verification=True,
                    verification_reason="Handwriting could not be deciphered with high confidence.",
                    completed=False
                ),
                MedicationChecklistItem(
                    id="chk_s3_2",
                    time_of_day="Morning",
                    medication_name="Omeprazole 20mg",
                    dosage="1 capsule",
                    instructions="Take 30 minutes before breakfast",
                    food_relation="On an empty stomach before food",
                    completed=False
                )
            ],
            simple_explanation=(
                "⚠️ **Important Notice**: One of the medications on this prescription could not be identified with certainty due to ambiguous handwriting.\n\n"
                "• **Item 1 is UNCONFIRMED**: Please show this prescription directly to your pharmacist before taking it.\n"
                "• **Omeprazole 20 mg** was clearly identified. It is an acid reducer taken once a day, 30 minutes before breakfast."
            ),
            detailed_explanation=(
                "**Prescription Legibility Review**:\n"
                "• **Line 1 (Uncertain Confidence)**: Inconclusive signature resembling 50 mcg dosing. Verification mandatory.\n"
                "• **Line 2 (High Confidence)**: Omeprazole 20 mg cap PO QAM AC. Proton pump inhibitor."
            ),
            has_uncertain_handwriting=True,
            uncertainty_warning=(
                "Some information in this prescription could not be read with sufficient confidence. "
                "Please confirm the medication and dosage with your doctor or pharmacist before taking it."
            ),
            tts_narration_script=(
                "Please note: some handwriting on this prescription is unclear. "
                "Item one requires verification with your pharmacist before taking. "
                "Item two is Omeprazole twenty milligrams: take one capsule in the morning on an empty stomach before eating."
            ),
            processing_time_ms=620.0
        )
    }
}

def get_sample_list() -> List[Dict[str, Any]]:
    return [
        {
            "id": v["id"],
            "title": v["title"],
            "category": v["category"],
            "description": v["description"],
            "image_url": v["image_url"]
        }
        for v in SAMPLE_PRESETS.values()
    ]

def get_sample_response(sample_id: str) -> PrescriptionDecodeResponse:
    if sample_id in SAMPLE_PRESETS:
        return SAMPLE_PRESETS[sample_id]["decoded_response"]
    return SAMPLE_PRESETS["sample_handwritten_amoxicillin"]["decoded_response"]
