import json

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
   - high_wage: software engineering, product, tech workplace, professional English-first contexts
   - low_wage: support, operations, delivery-to-office transitions, practical and confidence-building contexts
9. If language is 'hi', produce natural Hindi in Devanagari script while keeping JSON keys in English.
10. Rubric axes must clearly explain what strong performance looks like.
11. success_criteria must contain at least 3 distinct bullet-like strings.
12. transfer_targets must contain at least 2 items.
13. strategy_chips must contain exactly 3 items.
14. If any required list is too short, regenerate mentally before answering.
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
            "communication": {
                "min_score": 0,
                "max_score": 100,
                "what_good_looks_like": "string",
            },
            "composure": {
                "min_score": 0,
                "max_score": 100,
                "what_good_looks_like": "string",
            },
            "clarity": {
                "min_score": 0,
                "max_score": 100,
                "what_good_looks_like": "string",
            },
            "strategy": {
                "min_score": 0,
                "max_score": 100,
                "what_good_looks_like": "string",
            },
            "outcome": {
                "min_score": 0,
                "max_score": 100,
                "what_good_looks_like": "string",
            },
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
- make all three strategy chips different in style, not just wording.
- success_criteria must contain at least 3 items.
- transfer_targets must contain at least 2 items.
- strategy_chips must contain exactly 3 items.
Return JSON matching this shape exactly:
{json.dumps(schema_guide, indent=2, ensure_ascii=False)}
""".strip()
