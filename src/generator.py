import json
import os

from groq import Groq
from pydantic import ValidationError

from prompt_builder import build_system_prompt, build_user_prompt
from schemas import ScenarioInput, ScenarioOutput


MODEL_NAME = "llama-3.3-70b-versatile"
MAX_RETRIES = 3


def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


def call_model(client: Groq, validated_input: ScenarioInput, extra_instruction: str = "") -> str:
    user_prompt = build_user_prompt(validated_input)
    if extra_instruction:
        user_prompt += f"\n\nIMPORTANT FIX INSTRUCTION:\n{extra_instruction}"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.4,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def build_retry_instruction(error_message: str) -> str:
    return (
        "Return valid JSON only. Fix the validation issues from the previous attempt. "
        "Ensure success_criteria has at least 3 distinct items, transfer_targets has at least 2 items, "
        "strategy_chips has exactly 3 items, and all required keys are present. "
        f"Validation feedback: {error_message}"
    )


def generate_scenario(payload: dict) -> ScenarioOutput:
    validated_input = ScenarioInput.model_validate(payload)
    client = get_client()
    extra_instruction = ""
    last_error: Exception | None = None

    for _ in range(MAX_RETRIES):
        raw_text = call_model(client, validated_input, extra_instruction)

        try:
            parsed = json.loads(raw_text)
            return ScenarioOutput.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as error:
            last_error = error
            extra_instruction = build_retry_instruction(str(error))

    raise RuntimeError(f"Model failed to return a valid scenario after {MAX_RETRIES} attempts: {last_error}")


def generate_scenario_json(payload: dict) -> str:
    scenario = generate_scenario(payload)
    return json.dumps(scenario.model_dump(), indent=2, ensure_ascii=False)
