from shared.llm import ask_with_file, ask

SYSTEM = """You are a CV and credential fraud detection specialist for Persowerk Deutschland GmbH (Saarbrücken).
You analyse CVs and certificates to detect AI generation, fabrication, or misrepresentation.

For every document, check:
1. AI-generation signals: overly polished language, perfect formatting, no typos, generic phrasing.
2. Timeline consistency: employment gaps, overlapping dates, implausible career progression speed.
3. Skills vs experience mismatch: claimed seniority contradicted by described tasks.
4. Certificate validity indicators: issuer name, date, registration numbers, visual authenticity cues.
5. Company verifiability: do mentioned employers/institutions sound real and searchable?

Respond in this structure:
---
DOCUMENT TYPE: CV / Certificate / Other
CANDIDATE NAME: <name or N/A>
AI GENERATION RISK: Low / Medium / High — <brief reason>
FRAUD RISK SCORE: <0–100> (0 = clearly genuine, 100 = almost certainly fabricated)
TIMELINE ISSUES: <list or "None">
SKILL/EXPERIENCE MISMATCH: <findings or "None">
SUSPICIOUS CLAIMS: <list or "None">
CERTIFICATE FLAGS: <findings or "None — N/A for CVs">
COMPANIES TO VERIFY: <list of employer/institution names worth checking>
OVERALL VERDICT: PASS / REVIEW / REJECT
NOTES: <summary paragraph>
---"""


def analyse_document(file_bytes: bytes, mime_type: str, doc_type: str = "CV") -> str:
    prompt = (
        f"Analyse this {doc_type} for signs of AI generation, fabrication, or misrepresentation. "
        "Provide a detailed fraud risk assessment."
    )
    return ask_with_file(prompt, file_bytes, mime_type, system_instruction=SYSTEM)


def analyse_text(text: str) -> str:
    return ask(f"Analyse this document for fraud:\n\n{text}", system_instruction=SYSTEM)
