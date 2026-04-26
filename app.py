import pandas as pd
import streamlit as st

from agent import parse_jd, run_agent


st.set_page_config(page_title="AI Talent Scouting Agent", layout="wide")
st.title("AI Talent Scouting & Engagement Agent")
st.caption("End-to-end AI agent for talent scouting, engagement, and decision-making")

jd = st.text_area(
    "Paste the Job Description",
    placeholder=(
        "Example: We are hiring a Data Analyst in Hyderabad with 2+ years of experience. "
        "The candidate should be strong in Python, SQL, Power BI, dashboards, reporting, "
        "and stakeholder communication."
    ),
    height=220,
)

if st.button("Find Candidates", type="primary") and jd.strip():
    jd_summary = parse_jd(jd)
    results = run_agent(jd)
    top_candidate = results[0]

    st.markdown("## Agent Workflow")
    workflow_columns = st.columns(6)
    workflow_steps = [
        "1. JD Parsing",
        "2. Candidate Discovery",
        "3. Matching",
        "4. Conversational Outreach",
        "5. Interest Evaluation",
        "6. Ranking",
    ]
    for column, step in zip(workflow_columns, workflow_steps):
        column.info(step)

    st.markdown("## JD Summary")
    summary_columns = st.columns(4)
    summary_columns[0].metric("Target Role", jd_summary["role"])
    summary_columns[1].metric(
        "Preferred Location",
        jd_summary["location"] or "Flexible",
    )
    summary_columns[2].metric(
        "Minimum Experience",
        (
            f"{jd_summary['minimum_experience']} years"
            if jd_summary["minimum_experience"] is not None
            else "Not specified"
        ),
    )
    summary_columns[3].metric(
        "Skills Identified",
        str(len(jd_summary["skills"])),
    )
    st.write(
        f"**Required Skills:** {', '.join(jd_summary['skills']) if jd_summary['skills'] else 'Not explicitly detected'}"
    )

    st.markdown("## Ranked Shortlist")
    table = pd.DataFrame(
        [
            {
                "Name": item["name"],
                "Role": item["current_role"],
                "Location": item["location"],
                "Experience": item["experience"],
                "Match Score": item["match_score"],
                "Interest Score": item["interest_score"],
                "Final Score": item["final_score"],
                "Matched Skills": ", ".join(item["matched_skills"]) or "None",
            }
            for item in results
        ]
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("## Candidate Details")
    for item in results:
        with st.expander(f"{item['name']} • {item['current_role']} • Final Score {item['final_score']}%"):
            score_columns = st.columns(3)
            score_columns[0].metric("Match Score", f"{item['match_score']}%")
            score_columns[1].metric("Interest Score", f"{item['interest_score']}%")
            score_columns[2].metric("Final Score", f"{item['final_score']}%")

            st.markdown("### Agent Decision Summary")
            st.write(
                f"**Matched Skills:** {', '.join(item['matched_skills']) if item['matched_skills'] else 'None'}"
            )
            st.write(
                f"**Missing Skills:** {', '.join(item['missing_skills']) if item['missing_skills'] else 'None'}"
            )

            st.markdown("#### Match Explanation")
            for reason in item["match_explanation"]:
                st.write(f"- {reason}")

            st.markdown("#### Interest Explanation")
            for reason in item["interest_explanation"]:
                st.write(f"- {reason}")

            st.markdown("#### Conversation")
            for turn in item["conversation"]:
                st.write(f"**{turn['speaker']}**: {turn['message']}")

            if item["candidate_summary"]:
                st.markdown("#### LLM-Generated Summary")
                st.write(item["candidate_summary"])

    st.markdown("## Final Recommendation")
    st.success(
        f"Top Candidate: {top_candidate['name']} | {top_candidate['current_role']} | Final Score {top_candidate['final_score']}%"
    )
    st.write(
        f"**Why selected:** {top_candidate['name']} has the strongest combined ranking based on "
        f"match fit and candidate interest."
    )
    st.write(
        f"**Matched Skills:** {', '.join(top_candidate['matched_skills']) if top_candidate['matched_skills'] else 'None'}"
    )
    st.write(f"**Match Score:** {top_candidate['match_score']}%")
    st.write(f"**Interest Score:** {top_candidate['interest_score']}%")
    if top_candidate["interest_explanation"]:
        st.write(f"**Interest Signal:** {top_candidate['interest_explanation'][0]}")
