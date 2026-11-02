import re

# Arabic-Indic digits (٠١٢٣...) → normal digits, so "٧٨٤" is caught like "784"
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# What personal data looks like, as patterns
PII_PATTERNS = {
    "EMIRATES_ID": r"\b784[- ]?\d{4}[- ]?\d{7}[- ]?\d\b",              # 784-1990-1234567-1
    "PHONE": r"(?:\+971|00971|\b0)[ -]?5\d[ -]?\d{3}[ -]?\d{4}\b",     # +971 50 123 4567 / 0501234567
    "EMAIL": r"[\w.+-]+@[\w-]+\.[\w.-]+",                              # name@example.com
}

# Phrases people use to trick an AI (English + Arabic)
INJECTION_PHRASES = [
    "ignore previous instructions",
    "ignore all previous",
    "ignore your instructions",
    "disregard your instructions",
    "reveal your system prompt",
    "you are now",
    "developer mode",
    "jailbreak",
    "تجاهل التعليمات",
    "تجاهل جميع التعليمات",
]


def normalize(text: str) -> str:
    """Convert Arabic digits to normal digits."""
    return text.translate(ARABIC_DIGITS)


def mask_pii(text: str) -> tuple[str, list[str]]:
    """Replace personal data with labels. Returns (masked text, list of what was found)."""
    found = []
    for label, pattern in PII_PATTERNS.items():          # .items() = loop over key + value
        if re.findall(pattern, text):                    # is there at least one?
            found.append(label)
            text = re.sub(pattern, f"[{label}]", text)   # replace it with [LABEL]
    return text, found                                   # a function can return two things


def looks_like_injection(text: str) -> bool:
    """True if the message contains a known trick phrase."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in INJECTION_PHRASES)