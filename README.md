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
- `generator.py` handles the model call, retry-on-validation-failure, parsing, and schema validation
- `run_demo.py` provides a simple CLI for demoing sample or live inputs
- `run_batch.py` runs all 10 test inputs and saves the generated outputs

This separation makes the system easier to explain, test, and debug in the final round.

## Tech stack

- Python
- Groq API
- Pydantic for schema validation

Current configured model:

- `llama-3.3-70b-versatile`

## Setup

```bash
cd /Users/dikshashahi/Desktop/ai_challenge_group2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your_key_here"
```

## How to run

Run one predefined sample:

```bash
python3 src/run_demo.py --sample 0
```

Run the UI:

```bash
streamlit run app.py
```

The UI also supports a language comparison mode so you can show the same scenario in English and Hindi side by side.

Run with a custom input:

```bash
python3 src/run_demo.py --input-json '{"icp_type":"high_wage","milestone_code":"M03","skill_target":"stakeholder_communication","language":"en"}'
```

Run and save a sample output:

```bash
python3 src/run_demo.py --sample 0 --save
```

Run all 10 test cases and save outputs:

```bash
python3 src/run_batch.py
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
3. retries up to 3 times if the model returns invalid or incomplete output

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

## Strong sample input

```json
{
  "icp_type": "high_wage",
  "milestone_code": "M03",
  "skill_target": "stakeholder_communication",
  "language": "en"
}
```

## Strong sample output

```json
{
  "episode_title": "Sprint Review Delay Escalation",
  "scene": {
    "setting": "Wednesday sprint review, 2 days before release, in a video call with engineering and product",
    "time": "4:30 PM",
    "context": "You built most of the authentication flow, but one dependency from another service team is still unclear. The product manager wants a firm delivery update in front of the group."
  },
  "characters": [
    {
      "name": "Priya",
      "role": "Product Manager",
      "mood": "Pressured"
    },
    {
      "name": "Rohan",
      "role": "Tech Lead",
      "mood": "Watching closely"
    }
  ],
  "antagonist_opening_line": "We have already told stakeholders this will be ready for release. Why are we hearing now that the estimate is still unclear?",
  "strategy_chips": [
    {
      "id": "SC1",
      "label": "Clarify the dependency gap",
      "philosophy": "This works because it reduces ambiguity before making a risky commitment and shows that the delay is tied to a concrete blocker, not confusion."
    },
    {
      "id": "SC2",
      "label": "Acknowledge pressure, then realign on facts",
      "philosophy": "This works because it de-escalates the public tension while still bringing the conversation back to the current technical reality."
    },
    {
      "id": "SC3",
      "label": "Offer a bounded next-step plan",
      "philosophy": "This works because it replaces uncertainty with a visible recovery plan and gives stakeholders a clear decision point."
    }
  ],
  "success_criteria": [
    "The learner names the unresolved dependency clearly instead of giving a vague answer.",
    "The learner communicates timeline risk without sounding defensive.",
    "The learner proposes a concrete next step or checkpoint to restore alignment."
  ],
  "rubric": {
    "communication": {
      "min_score": 0,
      "max_score": 100,
      "what_good_looks_like": "The response is calm, direct, and easy for both technical and non-technical stakeholders to follow."
    },
    "composure": {
      "min_score": 0,
      "max_score": 100,
      "what_good_looks_like": "The learner stays steady under public pressure and avoids sounding flustered or defensive."
    },
    "clarity": {
      "min_score": 0,
      "max_score": 100,
      "what_good_looks_like": "The learner explains exactly what is known, what is blocked, and what can be committed right now."
    },
    "strategy": {
      "min_score": 0,
      "max_score": 100,
      "what_good_looks_like": "The learner chooses a response that reduces ambiguity, aligns stakeholders, and moves the conversation toward a plan."
    },
    "outcome": {
      "min_score": 0,
      "max_score": 100,
      "what_good_looks_like": "The discussion ends with shared understanding of the blocker, timeline risk, and immediate next action."
    }
  },
  "transfer_targets": [
    "Communicating blockers to stakeholders",
    "Handling public pressure in team meetings",
    "Turning uncertainty into an action plan"
  ]
}
```

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
