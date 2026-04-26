# AI Talent Scouting & Engagement Agent

An end-to-end AI agent that automates candidate discovery, engagement, and ranking based on job descriptions.

## Features
- JD Parsing (extracts role, skills, experience, location)
- Candidate Discovery (mock database)
- Skill Matching with explainability
- Conversational Outreach (simulated recruiter-candidate chat)
- Interest Evaluation using LLM
- Final Ranking with combined score
- Recruiter-ready recommendation

## Agent Workflow
1. JD Parsing
2. Candidate Discovery
3. Matching
4. Conversational Outreach (Simulated)
5. Interest Evaluation
6. Ranking

## Tech Stack
- Python
- Streamlit
- OpenRouter (LLM API)
- JSON (mock database)

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py