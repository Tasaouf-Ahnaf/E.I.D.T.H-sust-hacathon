import re
from typing import Dict

# -----------------------------------------
# Bengali Unicode Detection
# -----------------------------------------

BANGLA_REGEX = re.compile(r"[\u0980-\u09FF]")

# -----------------------------------------
# Banglish Keywords
# -----------------------------------------

BANGLISH_WORDS = {
    "ami",
    "amar",
    "amake",
    "amra",
    "taka",
    "tk",
    "bhul",
    "vul",
    "korsi",
    "korchi",
    "korlam",
    "korechi",
    "korse",
    "kortese",
    "hoise",
    "hoyeche",
    "hoy",
    "ache",
    "ase",
    "nai",
    "na",
    "eta",
    "oita",
    "ki",
    "keno",
    "paisi",
    "pai",
    "dise",
    "dilo",
    "pathaisi",
    "pathalam",
    "pathaisi",
    "numbere",
    "nombore",
}

# -----------------------------------------
# Common English Words
# -----------------------------------------

ENGLISH_WORDS = {
    "payment",
    "failed",
    "refund",
    "wrong",
    "transfer",
    "money",
    "account",
    "bank",
    "customer",
    "merchant",
    "issue",
    "problem",
    "help",
    "please",
    "send",
    "sent",
    "received",
    "receive",
    "transaction",
    "balance",
    "cash",
    "agent",
    "support",
    "number",
}


# -----------------------------------------
# Normalize Text
# -----------------------------------------

def normalize_text(text: str) -> str:
    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text


# -----------------------------------------
# Detect Language
# -----------------------------------------

def detect_language(text: str) -> str:

    # Bangla Unicode
    if BANGLA_REGEX.search(text):
        return "bn"

    words = []

    for word in text.lower().split():
        cleaned = re.sub(r"[^a-z]", "", word)

        if cleaned:
            words.append(cleaned)

    banglish_score = 0
    english_score = 0

    for word in words:

        if word in BANGLISH_WORDS:
            banglish_score += 1

        if word in ENGLISH_WORDS:
            english_score += 1

    # Banglish only if Banglish dominates
    if banglish_score >= 2 and banglish_score > english_score:
        return "banglish"

    return "en"


# -----------------------------------------
# Main Function
# -----------------------------------------

def detect_and_normalize(
    complaint: str,
    declared_language: str,
) -> Dict:

    normalized = normalize_text(complaint)

    detected = detect_language(normalized)

    result = {
        "detected_language": detected,
        "normalized": normalized,
    }

    if detected == "banglish":
        result["note"] = (
            "Banglish detected — AI will handle as-is"
        )

    if (
        declared_language
        and declared_language.lower() != detected
    ):
        result["declared_language"] = declared_language

    return result


# -----------------------------------------
# Local Testing
# -----------------------------------------

if __name__ == "__main__":

    tests = [

        (
            "I sent money to the wrong person",
            "en",
        ),

        (
            "Payment failed",
            "en",
        ),

        (
            "আমি ৫০০০ টাকা ভুল নম্বরে পাঠিয়েছি",
            "bn",
        ),

        (
            "Ami 500 taka send korsi",
            "banglish",
        ),

        (
            "Ami taka pai nai",
            "banglish",
        ),

        (
            "Refund request",
            "en",
        ),

        (
            "My payment was successful",
            "en",
        ),
    ]

    for complaint, lang in tests:

        print("-" * 60)

        print(complaint)

        print(detect_and_normalize(complaint, lang))