import json
from pathlib import Path

try:
    from .generator import generate_scenario_json
except ImportError:
    from generator import generate_scenario_json


ROOT_DIR = Path(__file__).resolve().parent.parent
TEST_INPUTS_PATH = ROOT_DIR / "tests" / "test_inputs.json"
OUTPUTS_DIR = ROOT_DIR / "outputs"


def main() -> None:
    samples = json.loads(TEST_INPUTS_PATH.read_text(encoding="utf-8"))
    OUTPUTS_DIR.mkdir(exist_ok=True)

    saved_files: list[str] = []

    for index, payload in enumerate(samples):
        output = generate_scenario_json(payload)
        output_path = OUTPUTS_DIR / f"sample_{index:02d}_{payload['icp_type']}_{payload['language']}.json"
        output_path.write_text(output, encoding="utf-8")
        saved_files.append(str(output_path))
        print(f"Saved: {output_path}")

    print(f"\nCompleted batch generation for {len(saved_files)} test cases.")


if __name__ == "__main__":
    main()
