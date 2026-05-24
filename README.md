# AI Engineering Challenge – Group 2: Scenario Writer

An AI-powered scenario generation engine that creates structured workplace simulations for different learner personas using LLMs, prompt engineering, and schema validation.

This project was built for the AI Engineering Challenge and focuses on generating realistic, emotionally grounded practice conversations that can be rendered directly inside a scenario-player application.

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
ai_challenge_group2/
├── README.md
├── requirements.txt
├── prompt_defense.md
├── app.py
├── run_batch.py
│
├── tests/
│   └── test_inputs.json
│
└── src/
    ├── generator.py
    ├── prompt_builder.py
    ├── run_demo.py
    └── schemas.py
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

The system validates at multiple layers.

## 1. Input Validation

Before the model call:

* invalid ICP types rejected
* malformed requests rejected
* missing fields rejected

---

## 2. Output Validation

After generation:

* schema structure checked
* required fields verified
* numeric rubric values validated
* malformed JSON detected

---

## 3. Retry Mechanism

If the LLM produces:

* incomplete JSON
* invalid schema
* malformed output

the system retries automatically up to 3 times.

This significantly improves reliability during demos.

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
python3 run_batch.py
```

---

# 🧪 Test Coverage

`tests/test_inputs.json` contains:

* 5 high_wage scenarios
* 5 low_wage scenarios

Used to evaluate:

* output consistency
* language switching
* difficulty scaling
* scenario diversity

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

* automatic malformed-response repair
* diversity scoring between generated scenarios
* snapshot-based regression testing
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
