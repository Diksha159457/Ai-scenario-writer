"""Scenario generation: prompt → LLM → JSON → schema + quality checks → retry.

Every failed attempt feeds its *specific* validation errors back to the model,
so the retry fixes the actual problem instead of re-rolling the dice.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from pydantic import ValidationError

try:
    from .prompt_builder import build_system_prompt, build_user_prompt
    from .quality import quality_issues
    from .schemas import ScenarioInput, ScenarioOutput
except ImportError:  # pragma: no cover - script mode (python src/run_demo.py)
    from prompt_builder import build_system_prompt, build_user_prompt
    from quality import quality_issues
    from schemas import ScenarioInput, ScenarioOutput


MODEL_NAME = os.getenv("SCENARIO_MODEL", "llama-3.3-70b-versatile")
MAX_RETRIES = 3


class ScenarioGenerationError(RuntimeError):
    """Raised when no valid scenario could be produced within the retry budget."""


class Completion(Protocol):
    """Anything that maps (system, user, model) -> raw text. Lets tests run offline."""

    def __call__(self, *, system: str, user: str, model: str) -> str: ...


def get_client():
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ScenarioGenerationError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


def groq_completion(client=None, temperature: float = 0.4) -> Completion:
    client = client or get_client()

    def _complete(*, system: str, user: str, model: str) -> str:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return (response.choices[0].message.content or "").strip()

    return _complete


def call_model(client, validated_input: ScenarioInput, extra_instruction: str = "") -> str:
    """Backwards-compatible single call used by older scripts."""
    user_prompt = build_user_prompt(validated_input)
    if extra_instruction:
        user_prompt += f"\n\nIMPORTANT FIX INSTRUCTION:\n{extra_instruction}"
    return groq_completion(client)(system=build_system_prompt(), user=user_prompt, model=MODEL_NAME)


def extract_json_text(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if not cleaned:
        raise json.JSONDecodeError("Empty model response", cleaned, 0)

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")

    if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
        raise json.JSONDecodeError("Could not find JSON object in model response", cleaned, 0)

    return cleaned[first_brace : last_brace + 1]


def _summarise_validation(error: ValidationError, limit: int = 6) -> str:
    parts = []
    for err in error.errors()[:limit]:
        loc = ".".join(str(p) for p in err["loc"]) or "<root>"
        parts.append(f"{loc}: {err['msg']}")
    more = len(error.errors()) - limit
    return "; ".join(parts) + (f"; (+{more} more)" if more > 0 else "")


def build_retry_instruction(problems: str) -> str:
    return (
        "Your previous answer was rejected. Return the COMPLETE scenario again as valid JSON only, "
        "fixing exactly these problems:\n"
        f"{problems}\n"
        "Remember: strategy_chips ids are SC1, SC2, SC3 in order; every rubric axis has min_score 0 and "
        "a different max_score; no keys outside the schema."
    )


@dataclass
class Attempt:
    ok: bool
    error_kind: str | None = None  # "json" | "schema" | "quality" | "provider"
    detail: str = ""
    latency_s: float = 0.0


@dataclass
class GenerationReport:
    scenario: ScenarioOutput | None
    attempts: list[Attempt] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.scenario is not None

    @property
    def total_latency_s(self) -> float:
        return sum(a.latency_s for a in self.attempts)


def generate_with_report(
    payload: dict | ScenarioInput,
    *,
    completion: Completion | None = None,
    model: str = MODEL_NAME,
    max_retries: int = MAX_RETRIES,
    strict_quality: bool = True,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.perf_counter,
) -> GenerationReport:
    """Generate a scenario and return it with a per-attempt trace.

    Quality issues (wrong language, generic opener) trigger a retry like schema
    errors do. If only quality issues remain on the final attempt, the scenario is
    returned with ``warnings`` instead of failing outright.
    """
    request = payload if isinstance(payload, ScenarioInput) else ScenarioInput.model_validate(payload)
    completion = completion or groq_completion()
    system = build_system_prompt()
    base_user = build_user_prompt(request)
    user = base_user
    report = GenerationReport(scenario=None)
    best_with_warnings: tuple[ScenarioOutput, list[str]] | None = None

    for attempt_no in range(max_retries):
        start = clock()
        try:
            raw = completion(system=system, user=user, model=model)
        except Exception as exc:  # network / rate limit: back off, same prompt
            report.attempts.append(Attempt(False, "provider", str(exc), clock() - start))
            if attempt_no < max_retries - 1:
                sleep(min(2**attempt_no, 8))
            continue
        latency = clock() - start

        try:
            scenario = ScenarioOutput.model_validate(json.loads(extract_json_text(raw)))
        except json.JSONDecodeError as exc:
            report.attempts.append(Attempt(False, "json", str(exc), latency))
            user = f"{base_user}\n\n{build_retry_instruction(f'invalid JSON: {exc}')}"
            continue
        except ValidationError as exc:
            detail = _summarise_validation(exc)
            report.attempts.append(Attempt(False, "schema", detail, latency))
            user = f"{base_user}\n\n{build_retry_instruction(detail)}"
            continue

        issues = quality_issues(scenario, request) if strict_quality else []
        if issues:
            report.attempts.append(Attempt(False, "quality", "; ".join(issues), latency))
            best_with_warnings = (scenario, issues)
            user = f"{base_user}\n\n{build_retry_instruction(chr(10).join(issues))}"
            continue

        report.attempts.append(Attempt(True, latency_s=latency))
        report.scenario = scenario
        return report

    if best_with_warnings:
        report.scenario, report.warnings = best_with_warnings
    return report


def generate_scenario(payload: dict, *, completion: Completion | None = None) -> ScenarioOutput:
    report = generate_with_report(payload, completion=completion)
    if report.scenario is None:
        last = report.attempts[-1] if report.attempts else Attempt(False, "none", "no attempts made")
        raise ScenarioGenerationError(
            f"Model failed to return a valid scenario after {len(report.attempts)} attempts "
            f"(last error: {last.error_kind}: {last.detail[:300]})"
        )
    return report.scenario


def generate_scenario_json(payload: dict, *, completion: Completion | None = None) -> str:
    scenario = generate_scenario(payload, completion=completion)
    return json.dumps(scenario.model_dump(), indent=2, ensure_ascii=False)
