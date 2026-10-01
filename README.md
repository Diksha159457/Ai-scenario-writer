# AI Engineering Challenge – Group 2: Scenario Writer

[![CI](https://github.com/Diksha159457/Ai-scenario-writer/actions/workflows/ci.yml/badge.svg)](https://github.com/Diksha159457/Ai-scenario-writer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Pydantic](https://img.shields.io/badge/pydantic-v2-e92063)

An AI-powered scenario generation engine that creates structured workplace simulations for different learner personas using LLMs, prompt engineering, and schema validation.

This project was built for the AI Engineering Challenge and focuses on generating realistic, emotionally grounded practice conversations that can be rendered directly inside a scenario-player application.


### Link to Loom

<https://loom.com/share/d02e80deb330482588550dbe79527ecb>
---

# 🚀 Overview

The `Scenario Writer` module accepts a small structured input:

```json
{
  "icp_type": "high_wage",
  "milestone_code": "M03",
  "skill_target": "stakeholder_communication",
  "language": "en"
}
```

and generates a complete scenario JSON containing:

* realistic workplace tension
* characters and emotional context
* strategy choices
* success criteria
* evaluation rubric
* transferable learning outcomes

The system is designed to simulate difficult workplace interactions in a safe, structured, and scalable format.

---

# 🎯 Core Objective

The goal is to generate high-quality roleplay scenarios for two distinct learner ICPs:

## 1. `high_wage`

Professional workplace scenarios for:

* engineering teams
* tech employees
* product stakeholders
* corporate communication

Examples:

* sprint escalation
* deadline negotiation
* stakeholder conflict
* cross-functional misalignment

---

## 2. `low_wage`

Practical and accessible workplace simulations for users transitioning from:

* gig work
* support roles
* retail/service environments

Examples:

* shift communication
* customer conflict
* supervisor interactions
* workplace misunderstandings

---

# ✅ Key Requirements

The generated output must:

* follow a strict JSON schema
* create realistic interpersonal tension
* adapt tone based on ICP type
* support English and Hindi output
* provide 3 meaningfully different strategy paths
* remain structurally valid for downstream rendering systems

---

# 🧠 Example Workflow

```text
User Input
    ↓
Input Validation (Pydantic)
    ↓
Prompt Builder
    ↓
Groq LLM API
    ↓
JSON Parsing
    ↓
Schema Validation
    ↓
Retry if Invalid
    ↓
Structured Scenario Output
```

---

# 📂 Project Structure

```text
Ai-scenario-writer/
├── app.py                  # Streamlit UI
├── prompt_defense.md
├── pyproject.toml
├── src/
│   ├── schemas.py          # Pydantic contracts, incl. cross-field rules
│   ├── quality.py          # input-aware checks (language, specificity)
│   ├── prompt_builder.py
│   ├── generator.py        # retry loop with targeted self-correction
│   ├── evaluate.py         # reliability eval across models
│   ├── run_demo.py
│   └── run_batch.py
├── tests/
│   ├── test_inputs.json    # 10 sample requests (5 en / 5 hi)
│   ├── fixtures/           # known-good en + hi scenarios
│   └── test_generator.py   # 37 offline tests (scripted fake LLM)
└── .github/workflows/
    ├── ci.yml              # ruff + pytest on 3.10–3.12
    └── eval.yml            # on-demand live-model eval
```

---

# ⚙️ Architecture & Design Choices

The project intentionally separates responsibilities for clarity, maintainability, and interview discussion.

## `schemas.py`

Defines:

* input validation
* output validation
* strict schema enforcement

Built using:

* Pydantic

---

## `prompt_builder.py`

Responsible for:

* system prompts
* ICP differentiation
* skill targeting
* language adaptation
* output-format instructions

Keeps prompting logic modular and easy to debug.

---

## `generator.py`

Handles:

* model calls
* retries
* parsing
* validation recovery
* structured output generation

This file acts as the orchestration layer.

---

## `run_demo.py`

Simple CLI utility for:

* testing samples
* running custom inputs
* saving outputs locally

Useful during demos and interviews.

---

## `run_batch.py`

Runs all predefined test cases automatically.

Helps validate:

* schema consistency
* prompt stability
* ICP variation quality

---

# 🛠️ Tech Stack

## Core Technologies

* Python
* Groq API
* Pydantic

## LLM Model

* `llama-3.3-70b-versatile`

---

# 🔐 Validation Strategy

Prompts are requests, not guarantees. Every rule the system prompt states that can be checked mechanically is also enforced in code, and every rejection is fed back to the model.

## 1. Input validation

`icp_type`, `milestone_code` and `language` are enum-checked. `skill_target` must be `snake_case` (3–60 chars). That also stops free text such as *"ignore previous instructions…"* from being injected into the prompt through the input fields.

## 2. Schema validation (`schemas.py`)

| Rule (from the prompt) | Enforced by |
|---|---|
| No extra keys, anywhere | `extra="forbid"` on every output model |
| Exactly 3 chips, ids `SC1`, `SC2`, `SC3` in order | `ScenarioOutput` cross-field validator |
| Chips are genuinely different | distinct labels (normalised) |
| Every rubric axis has `min_score = 0` | `RubricAxis` validator |
| Each axis has a **different** `max_score` | `Rubric` validator |
| ≥ 3 distinct success criteria, ≥ 2 transfer targets, ≥ 2 distinct characters | field constraints + validator |

Two of these (chip ids, varied rubric scores) were bugs fixed by hand in earlier sample outputs. They're now caught on every run.

## 3. Quality checks (`quality.py`)

These depend on the request as well as the output:

* **Language:** for `hi`, at least 60% of letters must be Devanagari; for `en`, at most 5%.
* **Specificity:** reject known generic openers; English scenarios must name a character in the opening line or scene.

## 4. Self-correcting retries (`generator.py`)

Each failed attempt is classified (`json` / `schema` / `quality` / `provider`). The next prompt then includes the **exact** errors, e.g. `strategy_chips: ids must be ['SC1','SC2','SC3'] in order`, instead of a generic "try again". Provider errors back off exponentially. If only soft quality issues remain after 3 attempts, the scenario is returned with `warnings` rather than failing the user.

`generate_with_report()` returns the scenario plus a per-attempt trace (error kind, detail, latency), which the eval uses.

---

# 🌍 Language Support

Supported:

* English (`en`)
* Hindi (`hi`)

The schema remains identical across languages while only the natural language content changes.

---

# 🎭 Output Schema

The generated JSON includes:

```json
{
  "episode_title": "",
  "scene": {},
  "characters": [],
  "antagonist_opening_line": "",
  "strategy_chips": [],
  "success_criteria": [],
  "rubric": {},
  "transfer_targets": []
}
```

---

# 💡 Sample Output Highlights

The generated scenarios include:

* emotional tension
* public pressure
* interpersonal conflict
* strategic communication choices
* actionable learning transfer

Example themes:

* missed deadlines
* customer escalation
* unclear dependencies
* workplace pressure
* leadership communication

---

# 📸 Demo Features

## CLI Demo

Run a predefined sample:

```bash
python3 src/run_demo.py --sample 0
```

Run with custom JSON:

```bash
python3 src/run_demo.py --input-json '{"icp_type":"high_wage","milestone_code":"M03","skill_target":"stakeholder_communication","language":"en"}'
```

Save generated output:

```bash
python3 src/run_demo.py --sample 0 --save
```

---

## Streamlit UI

Launch the UI:

```bash
streamlit run app.py
```

---

## Batch Testing

Run all 10 test cases:

```bash
python3 src/run_batch.py
```

---

# 🧪 Testing & Evaluation

### Offline test suite

```bash
pip install -e ".[dev]"
pytest --cov=src          # 37 tests, no API key or network needed
```

A scripted fake LLM drives the retry loop through every path: first-try success, malformed JSON, schema rejection with targeted feedback, wrong language, provider timeout with backoff, and retries running out. Each schema rule has a test that breaks a known-good fixture in exactly one way.

### Live reliability eval

```bash
export GROQ_API_KEY=gsk_...
python -m src.evaluate --models llama-3.3-70b-versatile llama-3.1-8b-instant --repeats 2 \
  --out outputs/eval_report.md
```

Runs all 10 sample requests per model and reports:

| Metric | Meaning |
|---|---|
| Valid 1st try | prompt quality |
| Valid after retries | system reliability |
| Avg tries | cost multiplier |
| p50 / p95 | latency including retries |
| Rejections by check | which validator the model trips most |

You can also trigger it from the **Actions → Reliability eval** tab (needs a `GROQ_API_KEY` secret). The table is posted to the job summary.

---

# 🏗️ Setup Instructions

## Clone Repository

```bash
git clone https://github.com/Diksha159457/ai_challenge_group2.git
```

---

## Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure API Key

```bash
export GROQ_API_KEY="your_key_here"
```

---

# 🧠 Interview Talking Points

This repository is optimized for technical discussions and final-round walkthroughs.

Strong areas to explain:

* prompt engineering decisions
* schema validation strategy
* retry architecture
* ICP differentiation logic
* structured JSON enforcement
* language abstraction
* modular file separation
* production-readiness considerations

---

# 🔥 Why This Project Stands Out

Unlike generic chatbot demos, this system focuses on:

* structured AI generation
* controllable outputs
* educational simulations
* validation-first architecture
* production-style reliability

This makes it closer to a real AI product workflow than a simple prompt wrapper.

---

# 🚀 Future Improvements

Potential production upgrades:

* ~~automatic malformed-response repair~~ ✅ targeted self-correcting retries
* diversity scoring between generated scenarios
* ~~snapshot-based regression testing~~ ✅ fixture-based schema tests + live eval
* evaluator models for scenario quality
* RAG-based workplace realism enhancement
* multilingual expansion
* persistent scenario memory
* analytics dashboard for learner performance

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch
3. Commit changes
4. Push updates
5. Open a Pull Request

---

# 📜 License

MIT License

---

# 👩‍💻 Author

Developed by Diksha Shahi

GitHub: [https://github.com/Diksha159457](https://github.com/Diksha159457)

---

# ⭐ Support

If you found this project useful:

* Star the repository
* Fork the project
* Share feedback
* Contribute improvements
