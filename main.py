from agent import parse_jd, run_agent


def print_conversation(conversation):
    for turn in conversation:
        print(f"   {turn['speaker']}: {turn['message']}")


jd = input("Enter Job Description: ")

jd_summary = parse_jd(jd)
results = run_agent(jd)

print("\n==============================")
print("   TALENT SHORTLIST RESULTS")
print("==============================\n")

print(f"Target role        : {jd_summary['role']}")
print(
    f"Required skills    : {', '.join(jd_summary['skills']) if jd_summary['skills'] else 'Not explicitly detected'}"
)
print(f"Preferred location : {jd_summary['location'] or 'Flexible / not specified'}")
print(
    f"Minimum experience : {str(jd_summary['minimum_experience']) + ' years' if jd_summary['minimum_experience'] is not None else 'Not specified'}"
)
print()

for index, candidate in enumerate(results, start=1):
    print(f"{index}. {candidate['name']} | {candidate['current_role']} | {candidate['location']}")
    print(f"   Match Score     : {candidate['match_score']}%")
    print(f"   Interest Score  : {candidate['interest_score']}%")
    print(f"   Final Score     : {candidate['final_score']}%")
    print(
        f"   Matched Skills  : {', '.join(candidate['matched_skills']) if candidate['matched_skills'] else 'None'}"
    )
    print(
        f"   Missing Skills  : {', '.join(candidate['missing_skills']) if candidate['missing_skills'] else 'None'}"
    )

    print("\n   Why this candidate?")
    for reason in candidate["match_explanation"]:
        print(f"   - {reason}")

    print("\n   Why they may respond?")
    for reason in candidate["interest_explanation"]:
        print(f"   - {reason}")

    print("\n   Simulated outreach:")
    print_conversation(candidate["conversation"])

    if candidate["candidate_summary"]:
        print("\n   LLM summary:")
        print(f"   {candidate['candidate_summary']}")

    print("\n" + "-" * 60 + "\n")

top_candidate = results[0]
print("FINAL RECOMMENDATION")
print(
    f"{top_candidate['name']} is the top candidate with a {top_candidate['final_score']}% combined score."
)
