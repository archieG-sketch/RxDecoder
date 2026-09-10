"""
Medical Sig Translation Utility
Translates standard Latin prescription abbreviations into clear, human-understandable plain English.
"""

SIG_DICTIONARY = {
    # Frequency
    "QD": "once daily",
    "Q.D.": "once daily",
    "QDAY": "once daily",
    "OD": "once daily",
    "BID": "two times a day (every 12 hours)",
    "B.I.D.": "two times a day (every 12 hours)",
    "TID": "three times a day (every 8 hours)",
    "T.I.D.": "three times a day (every 8 hours)",
    "QID": "four times a day (every 6 hours)",
    "Q.I.D.": "four times a day (every 6 hours)",
    "Q4H": "every 4 hours",
    "Q6H": "every 6 hours",
    "Q8H": "every 8 hours",
    "Q12H": "every 12 hours",
    "Q24H": "every 24 hours",
    "QAM": "every morning",
    "QPM": "every evening",
    "QHS": "every night at bedtime",
    "PRN": "as needed",
    "STAT": "immediately",

    # Route
    "PO": "by mouth",
    "P.O.": "by mouth",
    "SL": "under the tongue (sublingual)",
    "PR": "rectally",
    "IM": "into the muscle (intramuscular injection)",
    "IV": "into the vein (intravenous)",
    "SC": "under the skin (subcutaneous injection)",
    "SQ": "under the skin (subcutaneous injection)",
    "TOP": "apply to the skin topically",
    "INH": "inhale through the mouth",
    "NEB": "inhale via nebulizer",
    "OU": "in both eyes",
    "OS": "in the left eye",
    "OD": "in the right eye",
    "AU": "in both ears",
    "AS": "in the left ear",
    "AD": "in the right ear",

    # Timing & Food
    "AC": "before meals",
    "A.C.": "before meals",
    "PC": "after meals (after food)",
    "P.C.": "after meals (after food)",
    "CF": "with food",
    "WM": "with meals",
    "WF": "with food",
    "WA": "while awake",
    "HS": "at bedtime",

    # Units & Dosage
    "TAB": "tablet",
    "TABS": "tablets",
    "CAP": "capsule",
    "CAPS": "capsules",
    "GTT": "drop",
    "GTTS": "drops",
    "TSP": "teaspoon (5 mL)",
    "TBSP": "tablespoon (15 mL)",
    "PUFF": "spray/puff",
    "PUFFS": "sprays/puffs",
}

def decode_sig_string(sig_text: str) -> str:
    """
    Translates a medical shorthand sig line into conversational plain English.
    Example: '1 tab PO BID PC x 7d' -> 'Take 1 tablet by mouth two times a day after meals for 7 days.'
    """
    if not sig_text:
        return "Take as directed by your doctor."
    
    words = sig_text.strip().split()
    translated_words = []
    
    for word in words:
        cleaned_upper = word.strip(".,;:").upper()
        if cleaned_upper in SIG_DICTIONARY:
            translated_words.append(SIG_DICTIONARY[cleaned_upper])
        else:
            translated_words.append(word)
            
    result = " ".join(translated_words)
    return result
