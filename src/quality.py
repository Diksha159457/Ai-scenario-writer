"""Soft quality checks that depend on the *input* as well as the output.

Schema validation (``schemas.py``) answers "is this a well-formed scenario?".
These checks answer "is it the scenario we asked for?" — right language,
grounded in the requested skill, specific rather than generic.
"""

from __future__ import annotations

import re

try:
    from .schemas import ScenarioInput, ScenarioOutput
except ImportError:  # pragma: no cover - script mode
    from schemas import ScenarioInput, ScenarioOutput

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_LATIN = re.compile(r"[A-Za-z]")

GENERIC_OPENERS = (
    "i am unhappy with your work",
    "we need to talk",
    "this is not acceptable",
    "you made a mistake",
)


def devanagari_ratio(texts: list[str]) -> float:
    """Share of letters that are Devanagari (0.0 = all Latin, 1.0 = all Hindi script)."""
    joined = " ".join(texts)
    dev = len(_DEVANAGARI.findall(joined))
    lat = len(_LATIN.findall(joined))
    return dev / (dev + lat) if dev + lat else 0.0


def quality_issues(scenario: ScenarioOutput, request: ScenarioInput) -> list[str]:
    issues: list[str] = []

    ratio = devanagari_ratio(scenario.text_values())
    if request.language == "hi" and ratio < 0.6:
        issues.append(f"language is 'hi' but only {ratio:.0%} of letters are Devanagari; write values in Hindi")
    if request.language == "en" and ratio > 0.05:
        issues.append(f"language is 'en' but {ratio:.0%} of letters are Devanagari; write values in English")

    opener = scenario.antagonist_opening_line.strip().lower().rstrip(".!")
    if opener in GENERIC_OPENERS:
        issues.append("antagonist_opening_line is generic; name the character and the exact issue")

    names = [c.name for c in scenario.characters]
    if (
        request.language == "en"
        and not any(n.split()[0] in scenario.antagonist_opening_line for n in names)
        and not any(n.split()[0] in scenario.scene.context for n in names)
    ):
        issues.append("characters are not referenced in the opening line or scene context")

    scores = [axis.max_score for axis in scenario.rubric.axes().values()]
    if all(s == 100 for s in scores):  # belt-and-braces; schema already forbids duplicates
        issues.append("rubric max_scores must not all be 100")

    return issues
