# AI Engineering Challenge - Group 2: Scenario Writer

This repository implements the `Scenario Writer` AI module from the challenge brief.

The module takes a small input JSON:

- `icp_type`
- `milestone_code`
- `skill_target`
- `language`

and returns one structured scenario JSON that can be rendered directly by the scenario player.

## Problem statement

The goal is to generate realistic practice scenarios for two different user types:

- `high_wage`: engineering or tech-career users who need professional workplace scenarios
- `low_wage`: users transitioning from gig/support work who need practical, accessible workplace scenarios

The output must:

- follow a fixed JSON schema
- meaningfully differentiate between ICPs
- produce natural English or Hindi output
- create realistic tension through the `antagonist_opening_line`
- offer 3 genuinely different strategy options

## Output schema

The module returns:

- `episode_title`
- `scene { setting, time, context }`
- `characters[] { name, role, mood }`
- `antagonist_opening_line`
- `strategy_chips[3] { id, label, philosophy }`
- `success_criteria[]`
- `rubric { communication, composure, clarity, strategy, outcome }`
- `transfer_targets[]`

## Project structure

```text
ai_challenge_group2/
├── README.md
├── requirements.txt
├── prompt_defense.md
├── tests/
│   └── test_inputs.json
└── src/
    ├── generator.py
    ├── prompt_builder.py
    ├── run_demo.py
    └── schemas.py
```

## Design choices

This project is intentionally simple and interview-friendly:

- `schemas.py` defines strict input and output validation using Pydantic
- `prompt_builder.py` keeps the system prompt and user prompt readable
- `generator.py` handles the Claude API call, parsing, and schema validation
- `run_demo.py` provides a simple CLI for demoing sample or live inputs

This separation makes the system easier to explain, test, and debug in the final round.

## Tech stack

- Python
- Anthropic Claude API
- Pydantic for schema validation

Required model from the brief:

- `claude-sonnet-4-20250514`

## Setup

```bash
cd /Users/dikshashahi/Desktop/ipl_project/ai_challenge_group2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_key_here"
```

## How to run

Run one predefined sample:

```bash
python3 src/run_demo.py --sample 0
```

Run with a custom input:

```bash
python3 src/run_demo.py --input-json '{"icp_type":"high_wage","milestone_code":"M03","skill_target":"stakeholder_communication","language":"en"}'
```

## Test inputs

The file `tests/test_inputs.json` contains 10 sample inputs:

- 5 `high_wage`
- 5 `low_wage`

These are intended to help demonstrate:

- schema consistency
- ICP differentiation
- varied skills and milestone levels
- English and Hindi handling

## Validation strategy

The module validates:

1. input schema before the model call
2. output JSON after the model call

This helps catch:

- invalid input values
- malformed JSON
- missing fields
- unexpected fields
- structurally incorrect responses

## Demo talking points

These are the core behaviors to explain in the final round:

- `icp_type` changes the workplace world, characters, and tone
- `skill_target` changes the central tension and the strategy options
- `language` changes the output language but not the schema
- `milestone_code` changes scenario difficulty and maturity
- schema validation prevents silently passing broken outputs

## Submission notes

This repository is designed for the challenge deliverables:

- clean GitHub repo
- easy local run flow
- test inputs for varied cases
- prompt-defense support through `prompt_defense.md`

## Future improvements

For a production version, I would add:

- automatic retries for malformed model responses
- scenario diversity checks across batches
- snapshot-based output tests
- richer evaluation metrics for strategy quality
