# Prompt Defense

## Why this prompt design

I separated the prompt into:

1. System rules
2. Input interpretation
3. Output schema requirements
4. Quality constraints

This makes the model easier to control and easier to explain in the live round.

## What I optimized for

- Correct JSON every time
- Clear differences between `high_wage` and `low_wage`
- Realistic tension in `antagonist_opening_line`
- Three truly different `strategy_chips`
- Natural English or Hindi output depending on input

## What usually breaks in this task

- Generic scenarios
- Three strategies that are basically the same
- Rubric values that are vague or random
- Language switching that changes format
- Model adding extra keys

## How I handled that

- I explicitly told the model to return only valid JSON.
- I described how the two ICPs should differ.
- I defined the role of the antagonist line and strategy philosophies.
- I validate the response against a strict schema using Pydantic.

## If Sanket changes one field live

- If `icp_type` changes, the job world, characters, and tension should change.
- If `skill_target` changes, the core conflict and strategies should change.
- If `language` changes, wording should change but keys should remain the same.
- If `milestone_code` changes, scenario difficulty and complexity should adapt.
