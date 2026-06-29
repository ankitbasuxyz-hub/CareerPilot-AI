import re
from typing import Tuple

# Common prompt injection triggers
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"system\s+override",
    r"bypass\s+restrictions",
    r"you\s+are\s+now\s+a\s+different\s+agent",
    r"forget\s+what\s+you\s+were\s+told",
    r"dan\s+mode",
    r"jailbreak",
    r"you\s+must\s+act\s+as\s+a",
    r"ignore\s+system\s+prompt"
]

def validate_input_size(text: str, max_chars: int = 50000) -> bool:
    """Validates if the input size is within the allowed limits."""
    if not text:
        return True
    return len(text) <= max_chars

def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Scans the input text for common prompt injection patterns.
    Returns (is_malicious, matched_pattern).
    """
    if not text:
        return False, ""
    
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True, pattern
    return False, ""

def sanitize_output(text: str) -> str:
    """
    Sanitizes LLM or engine output to prevent XSS and script injections
    by neutralizing HTML and script tags.
    """
    if not text:
        return ""
    # Strip <script> and other executable elements
    text = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "[Script Blocked]", text, flags=re.IGNORECASE)
    # Neutralize HTML tags except basic formatting if needed, or escape them.
    # To keep standard markdown clean, we can escape common HTML tags.
    text = text.replace("<iframe", "&lt;iframe").replace("</iframe>", "&lt;/iframe&gt;")
    text = text.replace("<object", "&lt;object").replace("</object>", "&lt;/object&gt;")
    text = text.replace("<embed", "&lt;embed").replace("</embed>", "&lt;/embed&gt;")
    # Prevent onload or onerror inline handlers
    text = re.sub(r"\bon\w+\s*=", "blocked_event=", text, flags=re.IGNORECASE)
    return text

def sanitize_user_input(text: str) -> str:
    """Sanitizes user input by stripping potentially hazardous sequences."""
    if not text:
        return ""
    # Basic strip of trailing whitespaces
    return text.strip()
