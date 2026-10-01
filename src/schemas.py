"""Input/output contracts for the scenario writer.

The system prompt asks the model to follow a number of rules (exactly three
chips SC1–SC3, distinct rubric weights, no extra keys …). Prompts are requests,
not guarantees, so every rule that can be checked mechanically is enforced here
too. A violation becomes a ``ValidationError`` whose message is fed back to the
model on the next retry.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScenarioInput(BaseModel):
    icp_type: str = Field(pattern="^(high_wage|low_wage)$")
    milestone_code: str = Field(pattern="^M0[1-7]$")
    skill_target: str = Field(min_length=3, max_length=60, pattern=r"^[a-z][a-z_]*$")
    language: str = Field(pattern="^(en|hi)$")


class _Strict(BaseModel):
    """Reject keys the schema doesn't define — the prompt promises 'no extra fields'."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Scene(_Strict):
    setting: str = Field(min_length=1)
    time: str = Field(min_length=1)
    context: str = Field(min_length=1)


class Character(_Strict):
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    mood: str = Field(min_length=1)


class StrategyChip(_Strict):
    id: str
    label: str = Field(min_length=1)
    philosophy: str = Field(min_length=10)


class RubricAxis(_Strict):
    min_score: int = Field(ge=0, le=100)
    max_score: int = Field(ge=0, le=100)
    what_good_looks_like: str = Field(min_length=10)

    @model_validator(mode="after")
    def _range(self) -> RubricAxis:
        if self.min_score != 0:
            raise ValueError("min_score must be 0")
        if self.max_score <= self.min_score:
            raise ValueError("max_score must be greater than min_score")
        return self


class Rubric(_Strict):
    communication: RubricAxis
    composure: RubricAxis
    clarity: RubricAxis
    strategy: RubricAxis
    outcome: RubricAxis

    @model_validator(mode="after")
    def _distinct_weights(self) -> Rubric:
        scores = [axis.max_score for axis in self.axes().values()]
        if len(set(scores)) != len(scores):
            raise ValueError(f"each rubric axis needs a different max_score, got {scores}")
        return self

    def axes(self) -> dict[str, RubricAxis]:
        return {name: getattr(self, name) for name in type(self).model_fields}


def _norm(text: str) -> str:
    return re.sub(r"\W+", " ", text).strip().lower()


class ScenarioOutput(_Strict):
    episode_title: str = Field(min_length=1)
    scene: Scene
    characters: list[Character] = Field(min_length=2)
    antagonist_opening_line: str = Field(min_length=15)
    strategy_chips: list[StrategyChip] = Field(min_length=3, max_length=3)
    success_criteria: list[str] = Field(min_length=3)
    rubric: Rubric
    transfer_targets: list[str] = Field(min_length=2)

    @model_validator(mode="after")
    def _cross_field_rules(self) -> ScenarioOutput:
        ids = [chip.id for chip in self.strategy_chips]
        if ids != ["SC1", "SC2", "SC3"]:
            raise ValueError(f"strategy_chips ids must be ['SC1', 'SC2', 'SC3'] in order, got {ids}")

        labels = [_norm(chip.label) for chip in self.strategy_chips]
        if len(set(labels)) != len(labels):
            raise ValueError("strategy_chips labels must be distinct")

        criteria = [_norm(c) for c in self.success_criteria]
        if len(set(criteria)) != len(criteria) or not all(criteria):
            raise ValueError("success_criteria must be non-empty and distinct")

        names = [_norm(c.name) for c in self.characters]
        if len(set(names)) != len(names):
            raise ValueError("characters must have distinct names")
        return self

    def text_values(self) -> list[str]:
        """Every human-readable string value (used for language checks)."""
        out: list[str] = []

        def walk(node: object) -> None:
            if isinstance(node, str):
                out.append(node)
            elif isinstance(node, dict):
                for key, value in node.items():
                    if key not in {"id", "min_score", "max_score"}:
                        walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(self.model_dump())
        return out
