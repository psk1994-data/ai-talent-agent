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
```

## Sample Input & Output

### Sample Input
We are hiring a Data Analyst in Hyderabad with 2+ years of experience. The candidate should be strong in Python, SQL, Power BI, and data visualization.

### Sample Output
- Top Candidate: Rahul Sharma  
- Match Score: 75%  
- Interest Score: 80%  
- Final Score: 76.75%  

The system ranks candidates based on skill match and simulated interest level, providing recruiter-ready recommendations.

Note: If the live app is slow or temporarily unavailable due to API limits, please run the project locally using the steps above.