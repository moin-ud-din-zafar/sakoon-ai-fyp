"""Application constants for Sakoon AI."""

# Session limits
MAX_SESSIONS_PER_USER = 3

# Crisis detection
CRISIS_THRESHOLD = 0.6  # Suicidal class probability threshold
CRISIS_KEYWORDS = [
    "kill myself",
    "kill myself.",
    "end my life",
    "end it all",
    "want to die",
    "want to end",
    "suicide",
    "suicidal",
    "taking my life",
    "end myself",
    "better off dead",
    "no reason to live",
    "hurt myself",
]

# Mental health classification classes (must match dataset labels)
MH_CLASSES = [
    "Normal",
    "Stress",
    "Anxiety",
    "Depression",
    "Suicidal",
    "Bipolar",
    "Personality disorder",
]

# Severity order for personalization (highest first)
MH_SEVERITY_ORDER = [
    "Suicidal",
    "Depression",
    "Bipolar",
    "Personality disorder",
    "Anxiety",
    "Stress",
    "Normal",
]

# Pakistan helpline numbers
HELPLINE_NUMBERS = [
    {"name": "Umang Pakistan", "number": "0311-7786264"},
    {"name": "PMHW", "number": "1020"},
    {"name": "Sehat Tahaffuz", "number": "1166"},
]
