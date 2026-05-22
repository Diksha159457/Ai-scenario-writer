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
                radial-gradient(circle at 0% 0%, rgba(241, 199, 122, 0.30), transparent 24%),
                radial-gradient(circle at 100% 0%, rgba(102, 168, 255, 0.22), transparent 26%),
                linear-gradient(180deg, #f5efe5 0%, #fbfaf7 44%, #edf4fb 100%);
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .hero {
            padding: 1.9rem;
            border-radius: 28px;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(16, 24, 40, 0.08);
            box-shadow: 0 22px 50px rgba(57, 73, 99, 0.10);
            margin-bottom: 1rem;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: 1.35fr 0.9fr;
            gap: 1rem;
            align-items: center;
        }
        .hero h1 {
            font-size: 2.65rem;
            line-height: 1.05;
            margin: 0 0 0.5rem 0;
            color: #132238;
        }
        .hero p {
            color: #44556f;
            font-size: 1rem;
            margin: 0;
            line-height: 1.55;
        }
        .hero-panel {
            border-radius: 22px;
            padding: 1rem 1.1rem;
            background: linear-gradient(135deg, #16314d 0%, #335f8d 100%);
            color: white;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }
        .hero-panel small {
            display: block;
            opacity: 0.75;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .hero-panel strong {
            display: block;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        .hero-panel span {
            display: block;
            font-size: 0.95rem;
            line-height: 1.55;
            opacity: 0.92;
        }
        .soft-card {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(16, 24, 40, 0.08);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(78, 96, 123, 0.08);
            margin-bottom: 0.9rem;
        }
        .result-card {
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(16, 24, 40, 0.08);
            border-radius: 24px;
            padding: 1rem 1.1rem;
            box-shadow: 0 14px 34px rgba(78, 96, 123, 0.08);
            margin-bottom: 1rem;
        }
        .section-title {
            font-size: 0.82rem;
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
            line-height: 1.55;
            box-shadow: 0 12px 30px rgba(31, 54, 83, 0.22);
        }
        .chip {
            display: inline-block;
            padding: 0.28rem 0.7rem;
            border-radius: 999px;
            background: #eef4ff;
            color: #274472;
            font-size: 0.79rem;
            font-weight: 650;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }
        .accent-chip {
            display: inline-block;
            padding: 0.33rem 0.75rem;
            border-radius: 999px;
            background: #fff2d8;
            color: #885c09;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            margin: 0.4rem 0 1rem 0;
        }
        .metric {
            border-radius: 18px;
            padding: 0.9rem 1rem;
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(16, 24, 40, 0.08);
            box-shadow: 0 10px 20px rgba(78, 96, 123, 0.06);
        }
        .metric small {
            display: block;
            color: #66758b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.7rem;
            margin-bottom: 0.35rem;
        }
        .metric strong {
            color: #132238;
            font-size: 1rem;
        }
        .compare-label {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            background: #16314d;
            color: white;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.65rem;
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
            <div class="hero-grid">
                <div>
                    <h1>Scenario Writer</h1>
                    <p>
                        A recruiter-friendly UI for generating structured workplace practice scenarios
                        from learner profile, milestone, skill target, and language preference.
                    </p>
                </div>
                <div class="hero-panel">
                    <small>Demo Focus</small>
                    <strong>Structured + Personalized + Explainable</strong>
                    <span>
                        Show the same scenario logic across different ICPs and compare how the output
                        changes when only the language changes from English to Hindi or vice versa.
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(payload: dict) -> None:
    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric">
                <small>ICP</small>
                <strong>{payload["icp_type"]}</strong>
            </div>
            <div class="metric">
                <small>Milestone</small>
                <strong>{payload["milestone_code"]}</strong>
            </div>
            <div class="metric">
                <small>Language Mode</small>
                <strong>{payload["language"]}</strong>
            </div>
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
                    <span class="accent-chip">{chip["id"]}</span>
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


def render_result_view(result: dict, payload: dict, label: str | None = None) -> None:
    if label:
        st.markdown(f'<div class="compare-label">{label}</div>', unsafe_allow_html=True)
    render_metric_strip(payload)
    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-title">Episode Title</div>
            <div style="font-size:1.55rem; font-weight:700; color:#122033;">
                {result["episode_title"]}
            </div>
            <div style="margin-top:0.7rem;">
                <span class="chip">{payload["skill_target"]}</span>
                <span class="chip">{payload["language"]}</span>
                <span class="chip">{payload["milestone_code"]}</span>
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


def build_payload(icp_type: str, milestone_code: str, skill_target: str, language: str) -> dict:
    return {
        "icp_type": icp_type,
        "milestone_code": milestone_code,
        "skill_target": skill_target.strip(),
        "language": language,
    }


def generate_validated_scenario(payload: dict) -> tuple[dict, dict]:
    validated_payload = ScenarioInput.model_validate(payload)
    scenario = generate_scenario(validated_payload.model_dump())
    return scenario.model_dump(), validated_payload.model_dump()


def main() -> None:
    apply_styles()
    render_header()

    left, right = st.columns([0.95, 1.65], gap="large")

    with left:
        st.markdown("### Input")
        with st.form("scenario_form"):
            icp_type = st.selectbox("ICP Type", ["high_wage", "low_wage"])
            milestone_code = st.selectbox(
                "Milestone Code",
                ["M01", "M02", "M03", "M04", "M05", "M06", "M07"],
            )
            default_skill = "stakeholder_communication" if icp_type == "high_wage" else "problem_reporting"
            skill_target = st.text_input("Skill Target", value=default_skill)
            language = st.selectbox("Primary Language", ["en", "hi"])
            compare_languages = st.checkbox(
                "Compare Hindi vs English for the same scenario",
                value=False,
                help="Useful for showing that language changes expression, not scenario identity.",
            )
            submitted = st.form_submit_button("Generate Scenario", use_container_width=True)

        payload = build_payload(icp_type, milestone_code, skill_target, language)

        st.markdown("### Input Preview")
        st.code(json.dumps(payload, indent=2), language="json")

        st.markdown(
            """
            <div class="soft-card">
                <div class="section-title">How To Explain This UI</div>
                <div style="color:#31435d;">
                    Use the primary mode to show one clean scenario. Use compare mode to show that
                    the same low_wage or high_wage context stays stable while only the output language changes.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Generated Scenario")
        if submitted:
            try:
                if compare_languages:
                    alt_language = "hi" if language == "en" else "en"
                    compare_payload = build_payload(icp_type, milestone_code, skill_target, alt_language)

                    with st.spinner("Creating both language versions..."):
                        primary_result, primary_payload = generate_validated_scenario(payload)
                        compare_result, compare_validated_payload = generate_validated_scenario(compare_payload)

                    st.success("Comparison ready. The ICP and skill remain the same; only the language changes.")
                    col_a, col_b = st.columns(2, gap="large")
                    with col_a:
                        render_result_view(primary_result, primary_payload, f"Primary - {primary_payload['language']}")
                    with col_b:
                        render_result_view(compare_result, compare_validated_payload, f"Comparison - {compare_validated_payload['language']}")
                else:
                    with st.spinner("Creating a workplace scenario..."):
                        result, validated_payload = generate_validated_scenario(payload)

                    st.success("Scenario generated successfully.")
                    render_result_view(result, validated_payload)

            except ValidationError as error:
                st.error(f"Input validation failed: {error}")
            except Exception as error:
                st.error(f"Scenario generation failed: {error}")
        else:
            st.info("Fill in the form and click Generate Scenario to preview the UI.")


if __name__ == "__main__":
    main()
