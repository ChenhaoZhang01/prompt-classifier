"""Convergent vs. divergent prompt classifier with an overreliance warning.

Convergent prompts have (roughly) one correct answer — facts, definitions,
arithmetic, code with a spec. Divergent prompts are open-ended — brainstorming,
opinion, creative writing, strategy — where many answers are valid.

Why it matters: blindly trusting an AI on a *convergent, verifiable,
high-stakes* question (medical dosage, legal deadline, tax number) is exactly
where overreliance causes harm. This classifier labels the prompt and surfaces
an overreliance risk level so a UI can nudge the user to verify.

The classifier is a transparent logistic-style scorer over interpretable
features — no training data or model weights needed, and every decision is
explainable.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, asdict

CONVERGENT_CUES = [
    r"\bwhat is\b", r"\bwhen (?:did|was|is)\b", r"\bwho (?:is|was|wrote|invented)\b",
    r"\bhow many\b", r"\bcalculate\b", r"\bconvert\b", r"\bsolve\b", r"\bdefine\b",
    r"\bwhat'?s the (?:capital|formula|sum|value|date|deadline|dosage)\b",
    r"\bcorrect\b", r"\bexactly\b", r"\bprecise(?:ly)?\b",
    r"\bfix this (?:bug|error|code)\b", r"\bwhat does .* return\b",
]

DIVERGENT_CUES = [
    r"\bbrainstorm\b", r"\bideas?\b", r"\bsuggest\b", r"\bimagine\b", r"\bwrite a (?:story|poem|song)\b",
    r"\bwhat (?:do you think|should i)\b", r"\bopinion\b", r"\bcreative\b",
    r"\bways to\b", r"\bdesign\b", r"\bcome up with\b", r"\bpros and cons\b",
    r"\bstrateg(?:y|ies)\b", r"\bname some\b", r"\bcould\b", r"\bmight\b", r"\bplan for\b",
]

# High-stakes domains where a wrong convergent answer is costly.
HIGH_STAKES = [
    r"\bdosage\b", r"\bmedication\b", r"\bmg\b", r"\bdiagnos", r"\bsymptom",
    r"\blegal\b", r"\blawsuit\b", r"\bdeadline\b", r"\bstatute\b", r"\btax\b",
    r"\bdose\b", r"\bcontract\b", r"\binvest\b", r"\bsafe to (?:eat|take|mix)\b",
    r"\ballerg", r"\bvoltage\b", r"\bload[- ]bearing\b", r"\bblood\b",
]


def _count(patterns, text) -> int:
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class Classification:
    label: str               # "convergent" | "divergent"
    convergent_probability: float  # 0..1
    confidence: float        # distance from 0.5, scaled to 0..1
    overreliance_risk: str   # "low" | "moderate" | "high"
    warning: str | None
    features: dict
    rationale: str

    def as_dict(self) -> dict:
        return asdict(self)


def classify(prompt: str) -> Classification:
    text = prompt.strip()
    words = re.findall(r"\w+", text)
    n_words = max(1, len(words))

    conv = _count(CONVERGENT_CUES, text)
    div = _count(DIVERGENT_CUES, text)
    high_stakes = _count(HIGH_STAKES, text)
    question = text.count("?")
    has_number = 1 if re.search(r"\d", text) else 0
    list_request = 1 if re.search(r"\b(?:list|some|several|a few|options)\b", text, re.IGNORECASE) else 0

    # Linear score: positive -> convergent, negative -> divergent.
    z = (
        0.9 * conv
        - 1.0 * div
        + 0.4 * has_number
        - 0.6 * list_request
        + 0.5 * (question and conv > div)
        # very long prompts skew open-ended/divergent
        - 0.15 * (n_words > 40)
    )
    p_conv = _sigmoid(z)
    label = "convergent" if p_conv >= 0.5 else "divergent"
    confidence = round(abs(p_conv - 0.5) * 2, 3)

    # Overreliance risk: highest when convergent + high-stakes + confident.
    if label == "convergent" and high_stakes:
        risk = "high"
    elif label == "convergent" and (confidence > 0.4 or has_number):
        risk = "moderate"
    else:
        risk = "low"

    warning = None
    if risk == "high":
        warning = (
            "This looks like a verifiable question in a high-stakes domain. "
            "AI answers can be confidently wrong — independently verify with an "
            "authoritative source before acting."
        )
    elif risk == "moderate":
        warning = (
            "This has a checkable answer. Spot-check the result rather than "
            "relying on it blindly."
        )

    parts = [f"{conv} convergent cue(s)", f"{div} divergent cue(s)"]
    if high_stakes:
        parts.append(f"{high_stakes} high-stakes term(s)")
    if has_number:
        parts.append("contains numbers")
    rationale = "; ".join(parts)

    return Classification(
        label=label,
        convergent_probability=round(p_conv, 3),
        confidence=confidence,
        overreliance_risk=risk,
        warning=warning,
        features={
            "convergent_cues": conv,
            "divergent_cues": div,
            "high_stakes_terms": high_stakes,
            "questions": question,
            "has_number": has_number,
            "list_request": list_request,
            "word_count": n_words,
        },
        rationale=rationale,
    )
