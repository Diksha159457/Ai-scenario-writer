import argparse
import json
from pathlib import Path

from generator import generate_scenario_json


TEST_INPUTS_PATH = Path(__file__).resolve().parent.parent / "tests" / "test_inputs.json"


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
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input_json:
        payload = json.loads(args.input_json)
    elif args.sample is not None:
        samples = load_test_inputs()
        payload = samples[args.sample]
    else:
        raise SystemExit("Use --sample or --input-json.")

    output = generate_scenario_json(payload)
    print(output)


if __name__ == "__main__":
    main()
