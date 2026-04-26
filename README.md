# AI Talent Scouting & Engagement Agent

🔗 **Live App:** https://ai-talent-agent-gpsdsjycvyph3vsbuwb5a7.streamlit.app/

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

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py

Note:If the live app is slow or temporarily unavailable due to API limits, please run the project locally using the steps above.