import json, re
from shared.llm import ask, ask_with_file, ask_with_search

QUESTIONS_SYSTEM = """You are an expert interview preparation coach for Kohlpharma GmbH (Merzig).
You help non-technical hiring managers run structured technical interviews.

Return ONLY a valid JSON object — no markdown, no code fences, no prose before or after.

{
  "technical": [
    {"q": "Question text in plain language", "a": "What a good answer sounds like — 2-3 sentences, plain language"}
  ],
  "probe": [
    {"q": "Question targeting a specific gap or claim in this CV", "trigger": "One sentence: what exactly in the CV triggered this", "a": "What a good answer sounds like"}
  ],
  "behavioural": [
    {"q": "Situational question tailored to this role", "a": "What a good answer sounds like"}
  ],
  "red_flags": [
    "Specific thing to watch or listen for — tied to this exact role, not generic advice"
  ],
  "mini_tasks": [
    {"task": "Practical thing the candidate can do in the room in 5-10 minutes", "tip": "What good performance looks like"}
  ]
}

Exact counts: technical=5, probe=3 (empty array [] if no CV provided), behavioural=3, red_flags=5, mini_tasks=2.
Tailor every item to this specific role and candidate — no placeholders."""


CHAT_SYSTEM = """You are a concise interview coaching assistant for Kohlpharma GmbH (Merzig).
A non-technical manager asks you questions during or after an interview.
- Evaluating an answer → start with Strong / Partial / Weak, then explain in 1-2 plain sentences
- Red flag or follow-up question → be direct, max 2-3 sentences
- Explain all technical terms in plain language"""


def generate_questions(role_description: str, cv_summary: str = "") -> dict:
    prompt = f"Role I'm hiring for:\n\n{role_description}"
    if cv_summary:
        prompt += f"\n\nCandidate CV:\n{cv_summary}"
    for attempt in range(3):
        raw = ask(prompt, system_instruction=QUESTIONS_SYSTEM)
        m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
        if m:
            raw = m.group(1)
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            if attempt == 2:
                raise
    raise RuntimeError("Could not parse interview pack after 3 attempts")


def send_followup(conversation: list, new_message: str, role: str) -> str:
    prior = "\n\n".join(
        f"{'Manager' if m['role'] == 'user' else 'Coach'}: {m['content']}"
        for m in conversation
    ) if conversation else "(none)"
    prompt = (
        f"Role being interviewed for:\n{role}\n\n"
        f"Conversation so far:\n{prior}\n\n"
        f"Manager's question: {new_message}"
    )
    return ask(prompt, system_instruction=CHAT_SYSTEM)


def extract_cv_summary(file_bytes: bytes, mime_type: str) -> str:
    return ask_with_file(
        "Summarise this CV concisely: full name, current role, total years of experience, "
        "top 5 skills, education, and any gaps, inconsistencies, or missing details.",
        file_bytes, mime_type,
    )


def fetch_job_from_indeed(url: str) -> str:
    import urllib.parse
    params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    jk     = params.get("jk", [None])[0]
    jk_hint = f' (job ID: "{jk}")' if jk else ""

    prompt = (
        f"Use Google Search to find the full job description for this Indeed posting{jk_hint}.\n"
        f"URL: {url}\n\n"
        f"Search for the job ID or the company+title to locate the listing. "
        f"Return: job title, company, location, requirements, and main responsibilities.\n"
        f"If the posting cannot be found or is inaccessible, respond with exactly: FETCH_FAILED"
    )
    result = ask_with_search(
        prompt,
        system_instruction=(
            "You are a job description extractor. "
            "Return only the job details in plain text, or FETCH_FAILED if not found."
        ),
    )
    if "FETCH_FAILED" in result or len(result.strip()) < 80:
        raise ValueError(
            "Indeed restricts automated access — the posting isn't publicly indexed. "
            "Please paste the job description into the text box below."
        )
    return result


def generate_feedback_letter(role: str, candidate_name: str, strengths: str,
                             concerns: str, recommendation: str) -> str:
    prompt = f"""Write a professional, transparent post-interview feedback letter.

Role: {role}
Candidate: {candidate_name}
Recommendation: {recommendation}
Strengths: {strengths}
Concerns: {concerns}

- Address directly to the candidate (Dear {candidate_name},)
- Be specific — actual skills and observations, no generic HR phrases
- If Reject or Hold, give honest constructive development advice
- Under 250 words
- Close with: Kohlpharma GmbH Hiring Team"""
    return ask(prompt, system_instruction=CHAT_SYSTEM)
