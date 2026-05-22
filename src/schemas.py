from typing import List

from pydantic import BaseModel, Field


class ScenarioInput(BaseModel):
    icp_type: str = Field(pattern="^(high_wage|low_wage)$")
    milestone_code: str = Field(pattern="^M0[1-7]$")
    skill_target: str
    language: str = Field(pattern="^(en|hi)$")


class Scene(BaseModel):
    setting: str
    time: str
    context: str


class Character(BaseModel):
    name: str
    role: str
    mood: str


class StrategyChip(BaseModel):
    id: str
    label: str
    philosophy: str


class Rubric(BaseModel):
    communication: int = Field(ge=0, le=100)
    composure: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    strategy: int = Field(ge=0, le=100)
    outcome: int = Field(ge=0, le=100)


class ScenarioOutput(BaseModel):
    episode_title: str
    scene: Scene
    characters: List[Character] = Field(min_length=2)
    antagonist_opening_line: str
    strategy_chips: List[StrategyChip] = Field(min_length=3, max_length=3)
    success_criteria: List[str] = Field(min_length=3)
    rubric: Rubric
    transfer_targets: List[str] = Field(min_length=2)
