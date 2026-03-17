"""Policy checks for Zeerak health guidance."""

from typing import Tuple

TABIB_EMERGENCY_KEYWORDS = [
    "chest pain",
    "cannot breathe",
    "can't breathe",
    "severe bleeding",
    "unconscious",
    "stroke",
    "heart attack",
    "suicide",
    "self-harm",
    "overdose",
    "seizure",
]

TABIB_EMERGENCY_TEMPLATE = (
    "This may be an emergency. Call local emergency services now or go to the nearest hospital immediately. "
    "If breathing is difficult, chest pain is severe, bleeding is heavy, or there is risk of self-harm, "
    "do not wait for online advice. If possible, ask a trusted person to stay with you while you seek urgent care."
)

TABIB_SAFE_PROMPT = (
    "Use this structured triage style: 1) possible risk level, 2) immediate self-care, "
    "3) warning signs that require urgent care, 4) when to contact a clinician. "
    "Do not give a definitive diagnosis or medication dosage."
)


def apply_tabib_policy(task: str) -> Tuple[bool, str]:
    lowered = task.lower()

    if any(keyword in lowered for keyword in TABIB_EMERGENCY_KEYWORDS):
        return True, TABIB_EMERGENCY_TEMPLATE

    return False, TABIB_SAFE_PROMPT
