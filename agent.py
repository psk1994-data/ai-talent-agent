import json
import os
import re
from typing import Dict, List, Tuple

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


DATA_FILE = "data.json"
DEFAULT_MODEL = "gpt-4o-mini"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

SKILL_ALIASES = {
    "Python": ["python"],
    "SQL": ["sql", "postgresql", "mysql", "sqlite"],
    "NLP": ["nlp", "natural language processing"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "Excel": ["excel", "spreadsheets"],
    "Power BI": ["power bi", "powerbi"],
    "Data Analysis": ["data analysis", "analytics", "analytical"],
    "Data Science": ["data science", "data scientist"],
    "Data Visualization": ["data visualization", "visualization", "dashboards"],
    "Reporting": ["reporting", "reports"],
    "Database Management": ["database management", "database administration"],
    "Business Analysis": ["business analysis", "business analyst"],
}

ROLE_KEYWORDS = [
    "data analyst",
    "business analyst",
    "ml engineer",
    "machine learning engineer",
    "ai engineer",
    "artificial intelligence engineer",
    "data scientist",
    "bi analyst",
    "business intelligence analyst",
    "database analyst",
    "reporting analyst",
]

LOCATION_KEYWORDS = [
    "hyderabad",
    "bangalore",
    "chennai",
    "mumbai",
    "delhi",
    "pune",
    "noida",
    "kolkata",
    "kochi",
    "jaipur",
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_number(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _contains_alias(text: str, alias: str) -> bool:
    return re.search(rf"\b{re.escape(alias)}\b", text) is not None


def _extract_skills(normalized: str) -> List[str]:
    skills = []
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_alias(normalized, alias) for alias in aliases):
            skills.append(canonical)

    if "dashboard" in normalized and "Power BI" not in skills:
        skills.append("Data Visualization")
    if "stakeholder" in normalized and "Business Analysis" not in skills:
        skills.append("Business Analysis")
    if "report" in normalized and "Reporting" not in skills:
        skills.append("Reporting")

    return list(dict.fromkeys(skills))


def _extract_role(normalized: str) -> str:
    role_aliases = {
        "Data Analyst": ["data analyst", "analytics analyst", "analyst"],
        "Business Analyst": ["business analyst"],
        "ML Engineer": ["ml engineer", "machine learning engineer"],
        "AI Engineer": ["ai engineer", "artificial intelligence engineer"],
        "Data Scientist": ["data scientist"],
        "BI Analyst": ["bi analyst", "business intelligence analyst"],
        "Database Analyst": ["database analyst", "database engineer"],
        "Reporting Analyst": ["reporting analyst", "report analyst"],
    }

    for canonical, aliases in role_aliases.items():
        if any(_contains_alias(normalized, alias) for alias in aliases):
            return canonical

    if any(word in normalized for word in ["machine learning", "nlp", "deep learning"]):
        return "ML Engineer"
    if any(word in normalized for word in ["dashboard", "reporting", "power bi"]):
        return "Data Analyst"

    return "General Analytics / AI"


def _extract_location(normalized: str) -> str | None:
    for location in LOCATION_KEYWORDS:
        if _contains_alias(normalized, location):
            return location.title()
    return None


def _extract_minimum_experience(normalized: str) -> int | None:
    patterns = [
        r"(\d+)\s*-\s*(\d+)\s*years?",
        r"(\d+)\s*\+?\s*years?",
        r"minimum\s+(\d+)\s*years?",
        r"at least\s+(\d+)\s*years?",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if not match:
            continue
        if len(match.groups()) == 2:
            return int(match.group(1))
        return int(match.group(1))
    return None


def load_candidates() -> List[Dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_jd(jd_text: str) -> Dict:
    normalized = _normalize_text(jd_text)
    skills = _extract_skills(normalized)
    preferred_role = _extract_role(normalized)
    preferred_location = _extract_location(normalized)
    minimum_experience = _extract_minimum_experience(normalized)

    return {
        "skills": skills,
        "role": preferred_role,
        "location": preferred_location,
        "minimum_experience": minimum_experience,
    }


def _score_role_alignment(candidate_role: str, jd_role: str) -> Tuple[float, str]:
    if jd_role == "General Analytics / AI":
        return 70.0, "No explicit target role in JD, so role alignment is treated as broad fit."
    if candidate_role.lower() == jd_role.lower():
        return 100.0, f"Role matches exactly: {candidate_role}."
    if any(token in candidate_role.lower() for token in jd_role.lower().split()):
        return 80.0, f"Role is adjacent to the target role: {candidate_role} vs {jd_role}."
    return 45.0, f"Role is less aligned: {candidate_role} vs {jd_role}."


def _score_location_alignment(candidate_location: str, jd_location: str | None) -> Tuple[float, str]:
    if not jd_location:
        return 70.0, "JD does not specify a location, so location is treated as flexible."
    if candidate_location.lower() == jd_location.lower():
        return 100.0, f"Candidate is in the requested location: {candidate_location}."
    return 55.0, f"Candidate is in {candidate_location}, while JD mentions {jd_location}."


def _score_experience_alignment(candidate_experience: int, minimum_experience: int | None) -> Tuple[float, str]:
    if minimum_experience is None:
        return 75.0, "JD does not define a minimum experience threshold."
    if candidate_experience >= minimum_experience:
        return 100.0, f"Candidate meets the experience bar with {candidate_experience} years."

    gap = minimum_experience - candidate_experience
    score = max(30.0, 100.0 - gap * 25.0)
    return score, f"Candidate is {gap} year(s) below the requested experience."


def calculate_match(candidate: Dict, jd_summary: Dict) -> Tuple[float, Dict]:
    jd_skills = jd_summary["skills"]
    candidate_skills = candidate["skills"]
    matched_skills = sorted(set(candidate_skills) & set(jd_skills))
    missing_skills = sorted(set(jd_skills) - set(candidate_skills))

    skill_score = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 70.0
    role_score, role_reason = _score_role_alignment(candidate["role"], jd_summary["role"])
    exp_score, exp_reason = _score_experience_alignment(
        candidate["experience"], jd_summary["minimum_experience"]
    )
    location_score, location_reason = _score_location_alignment(
        candidate["location"], jd_summary["location"]
    )

    match_score = round(
        (skill_score * 0.5) + (role_score * 0.2) + (exp_score * 0.2) + (location_score * 0.1),
        2,
    )

    explanation = {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": round(skill_score, 2),
        "role_score": round(role_score, 2),
        "experience_score": round(exp_score, 2),
        "location_score": round(location_score, 2),
        "reasons": [
            f"Matched skills: {', '.join(matched_skills) if matched_skills else 'none'}.",
            f"Missing skills: {', '.join(missing_skills) if missing_skills else 'none'}.",
            role_reason,
            exp_reason,
            location_reason,
        ],
    }
    return match_score, explanation


def _heuristic_interest_score(candidate: Dict, jd_summary: Dict, match_score: float) -> Tuple[int, List[str]]:
    reasons = []
    score = 45

    if match_score >= 80:
        score += 25
        reasons.append("The role is closely aligned with the candidate's profile.")
    elif match_score >= 60:
        score += 15
        reasons.append("The role overlaps well with the candidate's existing strengths.")
    else:
        reasons.append("The role has partial overlap but would need some upskilling.")

    if candidate["experience"] >= 2:
        score += 10
        reasons.append("The candidate has enough experience to evaluate a move confidently.")

    if jd_summary["location"] and candidate["location"].lower() == jd_summary["location"].lower():
        score += 10
        reasons.append("The location is a convenient fit.")
    elif not jd_summary["location"]:
        score += 5
        reasons.append("No location constraint makes the opportunity easier to consider.")

    aspirational_roles = {"ML Engineer", "AI Engineer", "Data Scientist"}
    if candidate["role"] in aspirational_roles and any(
        skill in jd_summary["skills"] for skill in ["Machine Learning", "NLP", "Python"]
    ):
        score += 10
        reasons.append("The JD includes high-growth AI/ML work that is likely attractive.")

    return min(100, score), reasons


def _simulate_conversation(candidate: Dict, jd_summary: Dict, interest_score: int) -> List[Dict]:
    matched_skills = ", ".join(set(candidate["skills"]) & set(jd_summary["skills"])) or "relevant analytics skills"
    role_line = jd_summary["role"]

    if interest_score >= 80:
        response = (
            f"Thanks for reaching out. This {role_line} opportunity feels strongly aligned with my work in "
            f"{matched_skills}, and I would be interested in learning more about scope and team structure."
        )
        follow_up = "Happy to explore next steps if the role is actively hiring this month."
    elif interest_score >= 60:
        response = (
            f"This looks relevant to my background, especially around {matched_skills}. "
            "I am open to a conversation if the role offers good growth and ownership."
        )
        follow_up = "Please share the compensation band and the core day-to-day expectations."
    else:
        response = (
            f"I can see some overlap with my background in {matched_skills}, but I may not be the closest fit "
            "for the full scope right now."
        )
        follow_up = "I would keep an eye on similar openings that are a bit closer to my current focus."

    return [
        {
            "speaker": "Recruiter",
            "message": (
                f"Hi {candidate['name']}, I found your profile for a {role_line} opening. "
                "Would you be open to a quick conversation if the role aligns?"
            ),
        },
        {"speaker": "Candidate", "message": response},
        {
            "speaker": "Recruiter",
            "message": "What would determine whether you seriously consider this opportunity?",
        },
        {"speaker": "Candidate", "message": follow_up},
    ]


def _generate_llm_summary(candidate: Dict, jd_text: str, interest_score: int) -> str | None:
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    api_key = openrouter_api_key or openai_api_key
    if not api_key or OpenAI is None:
        return None

    try:
        client_kwargs = {"api_key": api_key}
        model = DEFAULT_MODEL

        if openrouter_api_key:
            client_kwargs["base_url"] = OPENROUTER_BASE_URL
            model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

        client = OpenAI(**client_kwargs)
        prompt = f"""
You are simulating a short candidate outreach summary.

Candidate:
- Name: {candidate["name"]}
- Current role: {candidate["role"]}
- Skills: {", ".join(candidate["skills"])}
- Experience: {candidate["experience"]} years
- Location: {candidate["location"]}

Job Description:
{jd_text}

Write 2 concise lines summarizing how interested this candidate sounds.
Keep the tone realistic and professional.
Target interest score: {interest_score}/100.
        """.strip()

        response = client.responses.create(
            model=model,
            input=prompt,
        )
        return response.output_text.strip()
    except Exception:
        return None


def build_shortlist(results: List[Dict], top_n: int = 5) -> List[Dict]:
    return sorted(results, key=lambda item: item["final_score"], reverse=True)[:top_n]


def run_agent(jd_text: str, top_n: int = 5) -> List[Dict]:
    jd_summary = parse_jd(jd_text)
    candidates = load_candidates()
    results = []

    for candidate in candidates:
        match_score, explanation = calculate_match(candidate, jd_summary)
        interest_score, interest_reasons = _heuristic_interest_score(candidate, jd_summary, match_score)
        conversation = _simulate_conversation(candidate, jd_summary, interest_score)
        llm_summary = _generate_llm_summary(candidate, jd_text, interest_score)

        final_score = round((match_score * 0.65) + (interest_score * 0.35), 2)

        results.append(
            {
                "name": candidate["name"],
                "current_role": candidate["role"],
                "experience": candidate["experience"],
                "location": candidate["location"],
                "match_score": match_score,
                "interest_score": interest_score,
                "final_score": final_score,
                "matched_skills": explanation["matched_skills"],
                "missing_skills": explanation["missing_skills"],
                "match_explanation": explanation["reasons"],
                "interest_explanation": interest_reasons,
                "conversation": conversation,
                "candidate_summary": llm_summary,
            }
        )

    return build_shortlist(results, top_n=top_n)
