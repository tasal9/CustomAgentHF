"""Policy checks for Zeerak health and public-guidance features."""

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

RAHNAMA_SENSITIVE_KEYWORDS = [
    "lawsuit",
    "court",
    "legal advice",
    "attorney",
    "lawyer",
    "guarantee approval",
    "visa refusal",
    "immigration decision",
]

RAHNAMA_SAFE_PROMPT = (
    "Give practical document and process guidance in this structure: 1) likely purpose of the process, "
    "2) common documents or information typically needed, 3) suggested next steps, 4) where local office rules may differ. "
    "Do not claim guaranteed approvals, legal outcomes, or official policy certainty without verification."
)

RAHNAMA_SENSITIVE_PROMPT = (
    "Treat the request as sensitive legal or administrative guidance. Provide general informational steps only, "
    "state clearly that official rules can change, and advise verifying with the relevant office or a qualified legal professional "
    "before acting on deadlines, appeals, immigration status, contracts, or court matters."
)


def apply_tabib_policy(task: str) -> Tuple[bool, str]:
    lowered = task.lower()

    if any(keyword in lowered for keyword in TABIB_EMERGENCY_KEYWORDS):
        return True, TABIB_EMERGENCY_TEMPLATE

    return False, TABIB_SAFE_PROMPT


def apply_rahnama_policy(task: str) -> str:
    lowered = task.lower()

    if any(keyword in lowered for keyword in RAHNAMA_SENSITIVE_KEYWORDS):
        return RAHNAMA_SENSITIVE_PROMPT

    return RAHNAMA_SAFE_PROMPT
