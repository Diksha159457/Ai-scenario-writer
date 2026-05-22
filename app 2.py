import json

import streamlit as st
from pydantic import ValidationError

from src.generator import generate_scenario
from src.schemas import ScenarioInput


st.set_page_config(
    page_title="Scenario Writer",
    page_icon="🧩",
    layout="wide",
)


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 232, 201, 0.8), transparent 30%),
                radial-gradient(circle at top right, rgba(198, 228, 255, 0.75), transparent 28%),
                linear-gradient(180deg, #f7f3ec 0%, #fffdf8 45%, #f1f6fb 100%);
        }
        .hero {
            padding: 1.75rem 1.75rem 1.25rem 1.75rem;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(16, 24, 40, 0.08);
            box-shadow: 0 18px 40px rgba(78, 96, 123, 0.10);
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2.4rem;
            margin-bottom: 0.25rem;
            color: #122033;
        }
        .hero p {
            color: #42526b;
            font-size: 1rem;
            margin-bottom: 0;
        }
        .soft-card {
            background: rgba(255, 255, 255, 0.80);
            border: 1px solid rgba(16, 24, 40, 0.08);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 28px rgba(78, 96, 123, 0.08);
            margin-bottom: 0.9rem;
        }
        .section-title {
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #7a5c2f;
            margin-bottom: 0.35rem;
            font-weight: 700;
        }
        .line-box {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #1f3653 0%, #355b82 100%);
            color: white;
            font-size: 1.05rem;
            line-height: 1.5;
            box-shadow: 0 12px 30px rgba(31, 54, 83, 0.25);
        }
        .chip {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            background: #eef4ff;
            color: #274472;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }
        .json-block pre {
            border-radius: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Scenario Writer UI</h1>
            <p>
                Generate a structured workplace practice scenario from a learner profile,
                skill target, and language preference.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scene(result: dict) -> None:
    scene = result["scene"]
    st.markdown('<div class="section-title">Scene</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="soft-card">
            <strong>{scene["setting"]}</strong><br/>
            <span style="color:#596980;">{scene["time"]}</span><br/><br/>
            <span style="color:#27364c;">{scene["context"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_characters(result: dict) -> None:
    st.markdown('<div class="section-title">Characters</div>', unsafe_allow_html=True)
    cols = st.columns(len(result["characters"]))
    for col, character in zip(cols, result["characters"]):
        col.markdown(
            f"""
            <div class="soft-card">
                <strong>{character["name"]}</strong><br/>
                <span style="color:#42526b;">{character["role"]}</span><br/><br/>
                <span class="chip">{character["mood"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_strategy_chips(result: dict) -> None:
    st.markdown('<div class="section-title">Strategy Options</div>', unsafe_allow_html=True)
    for chip in result["strategy_chips"]:
        st.markdown(
            f"""
            <div class="soft-card">
                <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:0.4rem;">
                    <span class="chip">{chip["id"]}</span>
                    <strong>{chip["label"]}</strong>
                </div>
                <span style="color:#31435d;">{chip["philosophy"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_list_section(title: str, items: list[str]) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    bullet_html = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(
        f"""
        <div class="soft-card">
            <ul style="margin:0; padding-left:1.1rem; color:#31435d;">
                {bullet_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rubric(result: dict) -> None:
    st.markdown('<div class="section-title">Rubric</div>', unsafe_allow_html=True)
    rubric_items = list(result["rubric"].items())
    for left, right in zip(rubric_items[::2], rubric_items[1::2] + [None] * (len(rubric_items) % 2)):
        cols = st.columns(2)
        pairs = [left, right]
        for col, pair in zip(cols, pairs):
            if pair is None:
                continue
            axis_name, axis = pair
            col.markdown(
                f"""
                <div class="soft-card">
                    <strong style="text-transform:capitalize;">{axis_name}</strong><br/>
                    <span class="chip">{axis["min_score"]} - {axis["max_score"]}</span><br/><br/>
                    <span style="color:#31435d;">{axis["what_good_looks_like"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_json(result: dict) -> None:
    with st.expander("View raw JSON output"):
        st.markdown('<div class="json-block">', unsafe_allow_html=True)
        st.code(json.dumps(result, indent=2, ensure_ascii=False), language="json")
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    apply_styles()
    render_header()

    left, right = st.columns([0.95, 1.55], gap="large")

    with left:
        st.markdown("### Input")
        with st.form("scenario_form"):
            icp_type = st.selectbox("ICP Type", ["high_wage", "low_wage"])
            milestone_code = st.selectbox(
                "Milestone Code",
                ["M01", "M02", "M03", "M04", "M05", "M06", "M07"],
            )
            skill_target = st.text_input(
                "Skill Target",
                value="stakeholder_communication" if icp_type == "high_wage" else "problem_reporting",
            )
            language = st.selectbox("Language", ["en", "hi"])
            submitted = st.form_submit_button("Generate Scenario", use_container_width=True)

        st.markdown("### Input Preview")
        payload = {
            "icp_type": icp_type,
            "milestone_code": milestone_code,
            "skill_target": skill_target.strip(),
            "language": language,
        }
        st.code(json.dumps(payload, indent=2), language="json")

    with right:
        st.markdown("### Generated Scenario")
        if submitted:
            try:
                validated_payload = ScenarioInput.model_validate(payload)
                with st.spinner("Creating a workplace scenario..."):
                    scenario = generate_scenario(validated_payload.model_dump())
                result = scenario.model_dump()

                st.markdown(
                    f"""
                    <div class="soft-card">
                        <div class="section-title">Episode Title</div>
                        <div style="font-size:1.55rem; font-weight:700; color:#122033;">
                            {result["episode_title"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                render_scene(result)
                render_characters(result)

                st.markdown('<div class="section-title">Opening Tension</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="line-box">{result["antagonist_opening_line"]}</div>',
                    unsafe_allow_html=True,
                )

                render_strategy_chips(result)
                render_list_section("Success Criteria", result["success_criteria"])
                render_rubric(result)
                render_list_section("Transfer Targets", result["transfer_targets"])
                render_json(result)

            except ValidationError as error:
                st.error(f"Input validation failed: {error}")
            except Exception as error:
                st.error(f"Scenario generation failed: {error}")
        else:
            st.info("Fill in the form and click Generate Scenario to preview the UI.")


if __name__ == "__main__":
    main()
