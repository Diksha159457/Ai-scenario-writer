import json
import os

from groq import Groq
from pydantic import ValidationError

try:
    from .prompt_builder import build_system_prompt, build_user_prompt
    from .schemas import ScenarioInput, ScenarioOutput
except ImportError:
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

    content = response.choices[0].message.content
    if content is None:
        return ""
    return content.strip()


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

    return cleaned[first_brace:last_brace + 1]


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
    last_raw_text = ""

    for _ in range(MAX_RETRIES):
        raw_text = call_model(client, validated_input, extra_instruction)
        last_raw_text = raw_text

        try:
            json_text = extract_json_text(raw_text)
            parsed = json.loads(json_text)
            return ScenarioOutput.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as error:
            last_error = error
            extra_instruction = build_retry_instruction(str(error))

    snippet = last_raw_text[:400].replace("\n", " ")
    raise RuntimeError(
        f"Model failed to return a valid scenario after {MAX_RETRIES} attempts: {last_error}. "
        f"Last raw response snippet: {snippet!r}"
    )


def generate_scenario_json(payload: dict) -> str:
    scenario = generate_scenario(payload)
    return json.dumps(scenario.model_dump(), indent=2, ensure_ascii=False)
