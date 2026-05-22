import json

try:
    from .schemas import ScenarioInput
except ImportError:
    from schemas import ScenarioInput


def build_system_prompt() -> str:
    return """
You are an AI module called Scenario Writer.

Your task is to generate one realistic workplace practice scenario as JSON.

You must obey these rules:
1. Return only valid JSON.
2. Do not include markdown fences.
3. Do not add any keys beyond the required schema.
4. The scenario must be realistic, specific, and useful for deliberate practice.
5. The antagonist_opening_line must create genuine tension without sounding cartoonish.
6. The 3 strategy_chips must be meaningfully different in approach.
7. The philosophy field must explain why that strategy works.
8. ICP differences must be strong:
   - high_wage: software engineering, product, QA, support engineering, sprint reviews, bug triage, code reviews, deadlines, cross-functional tech workplace contexts
   - low_wage: customer support, front desk, data entry, delivery-to-office transitions, supervisor pressure, practical and confidence-building contexts
9. If language is 'hi', produce natural Hindi in Devanagari script while keeping JSON keys in English.
10. rubric must contain only these 5 numeric fields: communication, composure, clarity, strategy, outcome.
11. Each rubric field must be an integer from 0 to 100.
12. Use realistic score values based on the scenario. Do not make all rubric values identical unless truly necessary.
13. success_criteria must contain at least 3 distinct bullet-like strings.
14. transfer_targets must contain at least 2 items.
15. strategy_chips must contain exactly 3 items.
16. If any required list is too short, regenerate mentally before answering.
17. Avoid generic scenes like "conference room", "startup office", or "team meeting" unless the input is too broad. Prefer concrete, high-friction moments.
18. The antagonist_opening_line should sound like a real person under workplace pressure, not a training manual.
19. The 3 strategy_chips must differ in philosophy, not just wording. Examples of different philosophies include clarifying, de-escalating, aligning, boundary-setting, or proposing a plan.
20. Do not make characters feel random. Their roles should directly create the tension in the scene.
21. For high_wage scenarios, prefer specific tech moments like sprint standup, release review, production issue, PR feedback, stakeholder sync, or project estimation.
22. For low_wage scenarios, prefer grounded moments like customer escalation, shift handover, supervisor check-in, missed process step, office coordination issue, or data-entry accuracy pressure.
23. For Hindi output, keep the language simple, natural, and spoken. Avoid heavy translation style or overly formal vocabulary.
24. success_criteria should be observable and measurable, not generic.
25. Vary names, roles, settings, and tensions across scenarios. Do not default to the same template.
""".strip()


def build_user_prompt(payload: ScenarioInput) -> str:
    schema_guide = {
        "episode_title": "string",
        "scene": {
            "setting": "string",
            "time": "string",
            "context": "string",
        },
        "characters": [
            {
                "name": "string",
                "role": "string",
                "mood": "string",
            }
        ],
        "antagonist_opening_line": "string",
        "strategy_chips": [
            {
                "id": "string",
                "label": "string",
                "philosophy": "string",
            }
        ],
        "success_criteria": ["string"],
        "rubric": {
            "communication": 0,
            "composure": 0,
            "clarity": 0,
            "strategy": 0,
            "outcome": 0,
        },
        "transfer_targets": ["string"],
    }

    return f"""
Generate one scenario object for this input:
{payload.model_dump_json(indent=2)}

Additional guidance:
- milestone_code should influence the difficulty and maturity of the scenario.
- skill_target should drive the central conflict.
- characters should fit the world of the ICP.
- make the scenario specific enough that it feels like a real moment.
- avoid generic scenes if a more concrete workplace moment can be inferred.
- make the antagonist_opening_line feel like a real line spoken under pressure.
- make all three strategy chips different in style, not just wording.
- high_wage outputs should feel clearly tied to tech or corporate skill-building.
- low_wage outputs should feel simpler, more practical, and more confidence-building.
- Hindi output should sound natural to a real Hindi speaker and not like direct translation.
- rubric values must be integer scores between 0 and 100.
- success_criteria must contain at least 3 items.
- transfer_targets must contain at least 2 items.
- strategy_chips must contain exactly 3 items.
- success_criteria should be observable outcomes, not vague statements.
Return JSON matching this shape exactly:
{json.dumps(schema_guide, indent=2, ensure_ascii=False)}
""".strip()
