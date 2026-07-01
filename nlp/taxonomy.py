"""Failure classification labels for zero-shot NLP."""

FAILURE_CATEGORIES = [
    "mechanical failure",
    "electrical failure",
    "software or firmware issue",
    "thermal or cooling problem",
    "structural or body damage",
    "sensor or calibration issue",
]

SEVERITY_LEVELS = [
    "critical safety issue",
    "high severity functional failure",
    "medium severity inconvenience",
    "low severity cosmetic issue",
]

ROOT_CAUSE_TYPES = [
    "manufacturing defect",
    "wear and tear",
    "environmental damage",
    "user-induced damage",
    "design flaw",
]

ZERO_SHOT_MODEL = "facebook/bart-large-mnli"
