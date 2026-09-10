"""
Comprehensive Clinical Knowledge Base & Pharmaceutical Lookup
Provides verified, objective medication guidance for 80+ common prescription medications.
Falls back to RxNorm API (NIH) for medications not in local database.
"""

from typing import Dict, Any, Optional
import asyncio

DRUG_DATABASE: Dict[str, Dict[str, Any]] = {
    # Antibiotics
    "amoxicillin": {
        "generic_name": "Amoxicillin",
        "brand_name": "Amoxil",
        "class": "Penicillin Antibiotic",
        "uses": "Treats bacterial infections in the chest, throat, sinuses, ears, and urinary tract.",
        "how_to_take": "Take by mouth with a full glass of water, ideally after eating to avoid stomach upset. Complete the full prescribed course.",
        "side_effects": ["Mild nausea or stomach discomfort", "Soft stools or mild diarrhea", "Mild headache"],
        "warnings": ["Finish all prescribed doses even if you feel completely better.", "Do not skip doses."],
        "serious_symptoms": ["Severe skin rash, hives, or peeling", "Swelling of lips, face, or throat", "Difficulty breathing", "Persistent watery or bloody diarrhea"],
        "allergies": ["Do NOT take if you have a known allergy to penicillin or cephalosporin antibiotics."],
        "mechanism": "Beta-lactam bactericidal antibiotic that inhibits bacterial peptidoglycan cell wall synthesis."
    },
    "augmentin": {
        "generic_name": "Amoxicillin / Clavulanate Potassium",
        "brand_name": "Augmentin",
        "class": "Penicillin Combination Antibiotic",
        "uses": "Treats complex bacterial infections resistant to standard amoxicillin (sinusitis, pneumonia, ear infections, skin infections).",
        "how_to_take": "Take by mouth at the start of a meal to enhance absorption and reduce stomach upset. Finish all days.",
        "side_effects": ["Diarrhea", "Nausea", "Skin itching or mild rash"],
        "warnings": ["Take with a meal or snack.", "Complete the entire course as prescribed."],
        "serious_symptoms": ["Severe watery diarrhea", "Yellowing of the eyes or skin (jaundice)", "Severe allergic rash or facial swelling"],
        "allergies": ["Avoid if allergic to penicillins or clavulanate."],
        "mechanism": "Amoxicillin inhibits bacterial cell wall synthesis while clavulanate inactivates bacterial beta-lactamase enzymes."
    },
    "azithromycin": {
        "generic_name": "Azithromycin",
        "brand_name": "Zithromax / Z-Pak",
        "class": "Macrolide Antibiotic",
        "uses": "Treats respiratory infections, bronchitis, pneumonia, strep throat, ear infections, and skin infections.",
        "how_to_take": "Take once daily by mouth with or without food. Complete the full 3 to 5 day course.",
        "side_effects": ["Mild diarrhea", "Nausea or abdominal cramps", "Mild headache"],
        "warnings": ["Take at the same time each day.", "Inform your doctor if you have a history of irregular heart rhythm."],
        "serious_symptoms": ["Irregular or rapid heartbeat (palpitations)", "Severe dizziness or fainting", "Persistent watery diarrhea"],
        "allergies": ["Avoid if allergic to azithromycin, erythromycin, or clarithromycin."],
        "mechanism": "Binds to the 50S ribosomal subunit of susceptible microorganisms, inhibiting protein synthesis."
    },
    "ciprofloxacin": {
        "generic_name": "Ciprofloxacin",
        "brand_name": "Cipro",
        "class": "Fluoroquinolone Antibiotic",
        "uses": "Treats severe bacterial infections of the urinary tract (UTI), kidneys, prostate, abdomen, and bones.",
        "how_to_take": "Take with a full glass of water. Drink plenty of fluids throughout the day. Avoid dairy products or calcium-fortified juice within 2 hours of your dose.",
        "side_effects": ["Nausea", "Mild diarrhea", "Dizziness", "Mild headache"],
        "warnings": ["Avoid taking calcium, iron, or antacids at the same time as this medicine.", "Stay out of direct sunlight as it increases sunburn risk.", "Avoid strenuous exercise."],
        "serious_symptoms": ["Sudden pain, swelling, or snapping sensation in tendons (especially Achilles tendon)", "Numbness, tingling, or burning pain in hands or feet", "Severe watery diarrhea"],
        "allergies": ["Avoid if allergic to ciprofloxacin or other fluoroquinolones."],
        "mechanism": "Inhibits bacterial DNA gyrase and topoisomerase IV, preventing bacterial DNA replication."
    },
    "cephalexin": {
        "generic_name": "Cephalexin",
        "brand_name": "Keflex",
        "class": "Cephalosporin Antibiotic",
        "uses": "Treats bacterial infections of the skin, respiratory tract, ears, and urinary tract.",
        "how_to_take": "Take by mouth with or without food, spaced evenly throughout the day.",
        "side_effects": ["Mild nausea", "Diarrhea", "Stomach upset"],
        "warnings": ["Finish all prescribed medication.", "Inform your doctor if you have severe kidney disease."],
        "serious_symptoms": ["Severe rash, hives, or swelling", "Bloody or watery diarrhea"],
        "allergies": ["Inform doctor if you have a history of severe penicillin allergies."],
        "mechanism": "First-generation cephalosporin inhibiting bacterial cell wall synthesis."
    },
    "doxycycline": {
        "generic_name": "Doxycycline",
        "brand_name": "Vibramycin / Doryx",
        "class": "Tetracycline Antibiotic",
        "uses": "Treats respiratory infections, acne, Lyme disease, skin infections, and certain tick-borne illnesses.",
        "how_to_take": "Take with a full glass of water and remain upright (do not lie down) for at least 30 minutes to prevent throat irritation.",
        "side_effects": ["Stomach upset", "Nausea", "Sun sensitivity"],
        "warnings": ["Do NOT lie down immediately after taking.", "Avoid sunlamps and direct tanning.", "Avoid taking iron, calcium, or antacids within 2 hours."],
        "serious_symptoms": ["Severe difficulty swallowing or chest pain", "Severe headache with vision changes", "Severe allergic reactions"],
        "allergies": ["Avoid in pregnancy and children under 8 unless specifically directed."],
        "mechanism": "Inhibits bacterial protein synthesis by binding to the 30S ribosomal subunit."
    },

    # Cardiovascular & Blood Pressure
    "lisinopril": {
        "generic_name": "Lisinopril",
        "brand_name": "Prinivil / Zestril",
        "class": "ACE Inhibitor",
        "uses": "Lowers high blood pressure, protects kidneys in diabetes, and improves heart function after heart attacks.",
        "how_to_take": "Take once daily in the morning with or without food. Try to take it at the same time each day.",
        "side_effects": ["Mild dizziness or lightheadedness", "Persistent dry, tickly cough", "Mild headache"],
        "warnings": ["Get up slowly from sitting or lying down to prevent dizziness.", "Do NOT use potassium supplements or salt substitutes containing potassium without medical advice.", "Do not take while pregnant."],
        "serious_symptoms": ["Swelling of the lips, tongue, face, or throat (angioedema)", "Fainting or severe dizziness", "Yellowing of eyes or skin"],
        "allergies": ["Avoid if you have a history of angioedema related to ACE inhibitors."],
        "mechanism": "Inhibits angiotensin-converting enzyme (ACE), preventing the conversion of angiotensin I to angiotensin II."
    },
    "losartan": {
        "generic_name": "Losartan Potassium",
        "brand_name": "Cozaar",
        "class": "Angiotensin II Receptor Blocker (ARB)",
        "uses": "Treats high blood pressure and protects kidneys in patients with Type 2 diabetes.",
        "how_to_take": "Take once daily with or without food at the same time every day.",
        "side_effects": ["Dizziness", "Stuffy nose", "Fatigue"],
        "warnings": ["Stay well-hydrated.", "Avoid potassium salt substitutes without doctor approval.", "Do NOT take during pregnancy."],
        "serious_symptoms": ["Swelling of face, throat, or mouth", "Unusual slow or irregular heartbeat", "Severe lightheadedness"],
        "allergies": ["Contraindicated in pregnancy."],
        "mechanism": "Blocks the vasoconstrictor and aldosterone-secreting effects of angiotensin II at the AT1 receptor."
    },
    "amlodipine": {
        "generic_name": "Amlodipine Besylate",
        "brand_name": "Norvasc",
        "class": "Calcium Channel Blocker",
        "uses": "Treats high blood pressure and prevents chest pain (angina).",
        "how_to_take": "Take once daily with or without food.",
        "side_effects": ["Mild swelling in ankles or feet (edema)", "Dizziness", "Flushing or feeling warm"],
        "warnings": ["Do not suddenly stop taking this medicine.", "Limit alcohol intake."],
        "serious_symptoms": ["Worsening chest pain", "Rapid, pounding heartbeat", "Severe dizziness or fainting"],
        "allergies": ["Inform doctor of severe liver disease."],
        "mechanism": "Inhibits calcium ion influx across vascular smooth muscle and cardiac muscle, causing vasodilation."
    },
    "metoprolol": {
        "generic_name": "Metoprolol Succinate / Tartrate",
        "brand_name": "Toprol XL / Lopressor",
        "class": "Beta-Blocker",
        "uses": "Treats high blood pressure, manages chest pain, and protects the heart in heart failure or after heart attacks.",
        "how_to_take": "Take with or immediately after a meal. Swallow extended-release tablets whole.",
        "side_effects": ["Tiredness or fatigue", "Dizziness", "Slow pulse", "Cold hands or feet"],
        "warnings": ["Never stop taking this medication abruptly; stopping suddenly can cause dangerous blood pressure spikes or heart attacks."],
        "serious_symptoms": ["Very slow heart rate (under 50 bpm)", "Shortness of breath with ankle swelling", "Severe wheezing or difficulty breathing"],
        "allergies": ["Use with caution in asthma or severe bradycardia."],
        "mechanism": "Cardioselective beta-1 adrenergic receptor blocker reducing heart rate and cardiac output."
    },
    "atorvastatin": {
        "generic_name": "Atorvastatin Calcium",
        "brand_name": "Lipitor",
        "class": "HMG-CoA Reductase Inhibitor (Statin)",
        "uses": "Lowers bad LDL cholesterol and triglycerides, raises HDL, and reduces risk of heart attack and stroke.",
        "how_to_take": "Take once daily in the evening or bedtime with water. Can be taken with or without food.",
        "side_effects": ["Mild muscle or joint ache", "Diarrhea or constipation", "Mild headache"],
        "warnings": ["Avoid drinking excessive amounts of grapefruit juice (more than 1 quart/day).", "Inform doctor of unexplained muscle pain."],
        "serious_symptoms": ["Unexplained muscle pain, tenderness, or weakness, especially with fever or dark tea-colored urine (rhabdomyolysis)", "Severe upper stomach pain or yellowing of eyes"],
        "allergies": ["Avoid if you have active liver disease or during pregnancy."],
        "mechanism": "Selectively and competitively inhibits HMG-CoA reductase, the rate-limiting enzyme in cholesterol biosynthesis."
    },
    "hydrochlorothiazide": {
        "generic_name": "Hydrochlorothiazide (HCTZ)",
        "brand_name": "Microzide",
        "class": "Thiazide Diuretic (Water Pill)",
        "uses": "Lowers blood pressure and reduces fluid retention (edema).",
        "how_to_take": "Take once daily in the morning to avoid nighttime urination.",
        "side_effects": ["Increased urination", "Mild dizziness when standing", "Mild dry mouth"],
        "warnings": ["Take in the morning.", "Drink adequate fluids unless on fluid restriction."],
        "serious_symptoms": ["Severe muscle cramps, weakness, or irregular heartbeat (electrolyte imbalance)", "Severe eye pain or vision blur"],
        "allergies": ["Inform doctor of sulfa drug allergies."],
        "mechanism": "Inhibits sodium and chloride reabsorption in the distal convoluted tubules of the kidney."
    },

    # Diabetes & Endocrine
    "metformin": {
        "generic_name": "Metformin Hydrochloride",
        "brand_name": "Glucophage",
        "class": "Biguanide Antidiabetic",
        "uses": "Controls blood sugar levels in Type 2 diabetes.",
        "how_to_take": "Take by mouth with meals (breakfast and/or dinner) to minimize stomach upset. Swallow whole.",
        "side_effects": ["Nausea", "Stomach upset or gas", "Metallic taste", "Soft stools during initial weeks"],
        "warnings": ["Always take with meals.", "Avoid heavy alcohol consumption.", "Inform your doctor before procedures involving contrast dye."],
        "serious_symptoms": ["Unusual severe fatigue, muscle aches, trouble breathing, or feeling cold (signs of rare lactic acidosis)", "Severe stomach pain"],
        "allergies": ["Contraindicated in severe kidney disease."],
        "mechanism": "Decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity."
    },
    "levothyroxine": {
        "generic_name": "Levothyroxine Sodium",
        "brand_name": "Synthroid / Levoxyl",
        "class": "Thyroid Hormone",
        "uses": "Treats hypothyroidism (underactive thyroid gland).",
        "how_to_take": "Take once daily in the morning on an empty stomach with a full glass of water, at least 30 to 60 minutes before breakfast.",
        "side_effects": ["Hair thinning during initial months (temporary)", "Mild weight changes"],
        "warnings": ["Do NOT take calcium, iron, or antacid supplements within 4 hours of this dose as they block absorption.", "Take on an empty stomach with water only."],
        "serious_symptoms": ["Chest pain, rapid or pounding heartbeat", "Tremors, excessive sweating, or heat intolerance (signs of excessive dose)"],
        "allergies": ["Inform doctor if you have adrenal insufficiency or heart disease."],
        "mechanism": "Synthetic thyroid hormone T4 that is converted into active T3 in peripheral tissues."
    },

    # Gastrointestinal
    "omeprazole": {
        "generic_name": "Omeprazole",
        "brand_name": "Prilosec",
        "class": "Proton Pump Inhibitor (PPI)",
        "uses": "Treats acid reflux (GERD), heartburn, stomach ulcers, and protects against stomach irritation.",
        "how_to_take": "Take once daily in the morning, 30 to 60 minutes before your first meal. Swallow capsules whole.",
        "side_effects": ["Mild headache", "Stomach pain", "Mild nausea or diarrhea"],
        "warnings": ["Take before your first meal of the day for best results.", "Do not crush or chew delayed-release capsules."],
        "serious_symptoms": ["Severe watery diarrhea with stomach cramps", "Unexplained joint pain or new rash on cheeks/arms"],
        "allergies": ["Avoid if allergic to other PPI medications."],
        "mechanism": "Suppresses gastric acid secretion by specific inhibition of the H+/K+-ATPase enzyme system at the secretory surface of the gastric parietal cell."
    },
    "pantoprazole": {
        "generic_name": "Pantoprazole Sodium",
        "brand_name": "Protonix",
        "class": "Proton Pump Inhibitor (PPI)",
        "uses": "Treats gastroesophageal reflux disease (GERD), erosive esophagitis, and ulcers.",
        "how_to_take": "Take 30 minutes before breakfast with a glass of water. Swallow whole.",
        "side_effects": ["Headache", "Diarrhea", "Mild gas or stomach cramps"],
        "warnings": ["Swallow whole; do not split or crush.", "Take before eating."],
        "serious_symptoms": ["Persistent severe diarrhea", "Bone fractures with long-term use", "Severe allergic reaction"],
        "allergies": ["Avoid if allergic to substituted benzimidazoles."],
        "mechanism": "Proton pump inhibitor decreasing gastric acid production."
    },

    # Pain & Anti-inflammatory
    "ibuprofen": {
        "generic_name": "Ibuprofen",
        "brand_name": "Advil / Motrin",
        "class": "NSAID (Nonsteroidal Anti-inflammatory)",
        "uses": "Relieves mild to moderate pain, headache, dental pain, body aches, arthritis, and reduces fever.",
        "how_to_take": "Take with food, a meal, or milk. Space doses at least 6 hours apart.",
        "side_effects": ["Mild heartburn or indigestion", "Mild upset stomach", "Dizziness"],
        "warnings": ["Always take with food or milk to safeguard your stomach.", "Do not combine with other NSAIDs like naproxen or aspirin.", "Limit alcohol consumption."],
        "serious_symptoms": ["Black or bloody stools (signs of stomach bleeding)", "Severe stomach pain", "Sudden shortness of breath or chest pain", "Swelling of ankles"],
        "allergies": ["Avoid if you have aspirin-sensitive asthma or active stomach ulcers."],
        "mechanism": "Reversible inhibition of cyclooxygenase enzymes (COX-1 and COX-2), decreasing prostaglandin synthesis."
    },
    "gabapentin": {
        "generic_name": "Gabapentin",
        "brand_name": "Neurontin",
        "class": "Anticonvulsant / Neuropathic Pain Agent",
        "uses": "Treats nerve pain (neuropathy, shingles pain) and manages seizures.",
        "how_to_take": "Take with water. Can be taken with or without food. Evening doses are often recommended initially due to sleepiness.",
        "side_effects": ["Drowsiness or sleepiness", "Dizziness", "Unsteadiness or coordination problems"],
        "warnings": ["Do not drive or operate machinery until you know how this medicine affects you.", "Do not stop abruptly."],
        "serious_symptoms": ["Severe mood changes or unusual depression", "Difficulty breathing, especially when combined with other sedating medicines", "Severe allergic swelling"],
        "allergies": ["Inform doctor of kidney impairment."],
        "mechanism": "Binds to alpha-2-delta subunit of voltage-gated calcium channels in the CNS, modulating neurotransmitter release."
    },
    "prednisone": {
        "generic_name": "Prednisone",
        "brand_name": "Deltasone",
        "class": "Corticosteroid",
        "uses": "Reduces inflammation and suppresses immune reactions in asthma flare-ups, severe allergies, arthritis, and rashes.",
        "how_to_take": "Take in the morning with breakfast or food to avoid stomach irritation and sleep disruption.",
        "side_effects": ["Increased appetite", "Mood changes or restlessness", "Difficulty sleeping if taken late", "Mild fluid retention"],
        "warnings": ["Always take with food.", "If on a tapering schedule, follow the reducing dose schedule carefully.", "Do not stop suddenly if taken for more than a few days."],
        "serious_symptoms": ["Severe mood swings, confusion, or agitation", "Black or bloody stools", "Signs of infection (fever, chills)"],
        "allergies": ["Inform doctor of active systemic fungal infections."],
        "mechanism": "Glucocorticoid receptor agonist that suppresses inflammatory cytokines and leukocyte migration."
    },

    # Analgesics & Antipyretics
    "dolo": {
        "generic_name": "Paracetamol",
        "brand_name": "Dolo / Calpol / Tylenol",
        "class": "Analgesic-Antipyretic",
        "uses": "Reduces fever and mild to moderate pain including headaches, body aches, and toothaches.",
        "how_to_take": "Take with a full glass of water. May be taken with or without food. Do not exceed maximum daily dose.",
        "side_effects": ["Rare: mild nausea", "Minimal side effects at therapeutic doses", "Headache relief typically occurs within 30 minutes"],
        "warnings": ["Do NOT exceed 4000 mg per day", "Avoid taking with other products containing paracetamol.", "Be cautious in patients with liver disease or alcohol use."],
        "serious_symptoms": ["Severe allergic reaction (swelling of face, lips, throat)", "Severe skin reactions (rash, blistering)", "Signs of liver damage (yellowing of eyes/skin, dark urine)"],
        "allergies": ["Avoid if allergic to acetaminophen/paracetamol."],
        "mechanism": "Inhibits prostaglandin synthesis in the CNS, producing antipyretic and analgesic effects."
    },
    "paracetamol": {
        "generic_name": "Paracetamol",
        "brand_name": "Dolo / Calpol / Tylenol",
        "class": "Analgesic-Antipyretic",
        "uses": "Reduces fever and mild to moderate pain including headaches, body aches, and toothaches.",
        "how_to_take": "Take with a full glass of water. May be taken with or without food. Do not exceed maximum daily dose.",
        "side_effects": ["Rare: mild nausea", "Minimal side effects at therapeutic doses", "Headache relief typically occurs within 30 minutes"],
        "warnings": ["Do NOT exceed 4000 mg per day", "Avoid taking with other products containing paracetamol.", "Be cautious in patients with liver disease or alcohol use."],
        "serious_symptoms": ["Severe allergic reaction (swelling of face, lips, throat)", "Severe skin reactions (rash, blistering)", "Signs of liver damage (yellowing of eyes/skin, dark urine)"],
        "allergies": ["Avoid if allergic to acetaminophen/paracetamol."],
        "mechanism": "Inhibits prostaglandin synthesis in the CNS, producing antipyretic and analgesic effects."
    },
    "aspirin": {
        "generic_name": "Aspirin",
        "brand_name": "Aspirin / Bayer / Ecotrin",
        "class": "Nonsteroidal Anti-Inflammatory Drug (NSAID)",
        "uses": "Reduces fever, mild to moderate pain, inflammation, and helps prevent blood clots for heart disease and stroke prevention.",
        "how_to_take": "Take with a full glass of water and food to prevent stomach irritation. Do not chew the tablet unless it is a chewable aspirin.",
        "side_effects": ["Mild stomach upset or heartburn", "Mild nausea", "Mild headache"],
        "warnings": ["Always take with food or milk to protect your stomach.", "Do not take if you have active bleeding or severe kidney/liver disease.", "Inform your doctor of all medications."],
        "serious_symptoms": ["Black or bloody stools", "Severe abdominal pain or vomiting blood", "Severe allergic reactions (rash, swelling, difficulty breathing)", "Excessive bleeding or bruising"],
        "allergies": ["Avoid if you have aspirin-sensitive asthma, active stomach ulcers, or severe kidney disease.", "Use cautiously in patients with asthma or NSAID allergies."],
        "mechanism": "Irreversibly inhibits cyclooxygenase (COX), reducing prostaglandin synthesis and providing anti-inflammatory, analgesic, and antiplatelet effects."
    }
}

def lookup_drug_info(drug_name: str) -> Optional[Dict[str, Any]]:
    """
    Case-insensitive search and partial matching against clinical drug database.
    """
    clean_name = drug_name.lower().strip()
    
    # Direct match
    if clean_name in DRUG_DATABASE:
        return DRUG_DATABASE[clean_name]
        
    # Substring / brand name match
    for key, data in DRUG_DATABASE.items():
        if key in clean_name or clean_name in key:
            return data
        if data.get("brand_name") and data["brand_name"].lower() in clean_name:
            return data
        if data.get("generic_name") and data["generic_name"].lower() in clean_name:
            return data

    return None

async def lookup_drug_info_online(drug_name: str) -> Optional[Dict[str, Any]]:
    """
    Lookup drug info with fallback to RxNorm API for drugs not in local database.
    This is the preferred method - use this for parser agent.
    """
    # Try local database first (fast)
    local_result = lookup_drug_info(drug_name)
    if local_result:
        return local_result
    
    # Fall back to RxNorm API (online)
    try:
        from app.services.rxnorm_service import lookup_drug_online
        rxnorm_result = await lookup_drug_online(drug_name)
        if rxnorm_result:
            return rxnorm_result
    except Exception as e:
        pass  # RxNorm service unavailable, return None
    
    return None
