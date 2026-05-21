import argparse
import json
from pathlib import Path

from generator import generate_scenario_json


TEST_INPUTS_PATH = Path(__file__).resolve().parent.parent / "tests" / "test_inputs.json"
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"


def load_test_inputs() -> list[dict]:
    with TEST_INPUTS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Group 2 Scenario Writer demo.")
    parser.add_argument(
        "--sample",
        type=int,
        help="Run one sample from tests/test_inputs.json by index.",
    )
    parser.add_argument(
        "--input-json",
        type=str,
        help="Pass a raw JSON string as input.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the generated output into the outputs directory.",
    )
    return parser.parse_args()


def save_output(payload: dict, output: str, sample_index: int | None) -> Path:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    if sample_index is not None:
        filename = f"sample_{sample_index:02d}_{payload['icp_type']}_{payload['language']}.json"
    else:
        filename = f"custom_{payload['icp_type']}_{payload['language']}.json"
    output_path = OUTPUTS_DIR / filename
    output_path.write_text(output, encoding="utf-8")
    return output_path


def main() -> None:
    args = parse_args()
    sample_index: int | None = None

    if args.input_json:
        payload = json.loads(args.input_json)
    elif args.sample is not None:
        samples = load_test_inputs()
        sample_index = args.sample
        payload = samples[sample_index]
    else:
        raise SystemExit("Use --sample or --input-json.")

    output = generate_scenario_json(payload)
    print(output)
    if args.save:
        saved_path = save_output(payload, output, sample_index)
        print(f"\nSaved output to: {saved_path}")


if __name__ == "__main__":
    main()
