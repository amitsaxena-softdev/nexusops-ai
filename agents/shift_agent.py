from shared.llm import ask

STAFF_DB = [
    {"name": "Anna Becker", "id": "UKS-001", "role": "Intensivpflegefachkraft",
     "qualifications": ["ICU", "Anästhesie", "Beatmung"],
     "phone": "+49 176 11110001", "email": "a.becker@uks.eu",
     "shifts_this_week": 3, "available_nights": True},
    {"name": "Thomas Kraus", "id": "UKS-002", "role": "Pflegefachkraft",
     "qualifications": ["Chirurgie", "Orthopädie", "Notaufnahme"],
     "phone": "+49 176 11110002", "email": "t.kraus@uks.eu",
     "shifts_this_week": 2, "available_nights": True},
    {"name": "Maria Schmidt", "id": "UKS-003", "role": "Intensivpflegefachkraft",
     "qualifications": ["ICU", "Neonatologie", "Pädiatrie"],
     "phone": "+49 176 11110003", "email": "m.schmidt@uks.eu",
     "shifts_this_week": 4, "available_nights": False},
    {"name": "Lars Hoffmann", "id": "UKS-004", "role": "Pflegefachkraft",
     "qualifications": ["Innere Medizin", "Kardiologie", "Notaufnahme"],
     "phone": "+49 176 11110004", "email": "l.hoffmann@uks.eu",
     "shifts_this_week": 1, "available_nights": True},
    {"name": "Julia Weiss", "id": "UKS-005", "role": "Pflegefachkraft",
     "qualifications": ["Gynäkologie", "Geburtshilfe", "OP"],
     "phone": "+49 176 11110005", "email": "j.weiss@uks.eu",
     "shifts_this_week": 3, "available_nights": True},
    {"name": "Kevin Müller", "id": "UKS-006", "role": "Intensivpflegefachkraft",
     "qualifications": ["ICU", "Beatmung", "Herzchirurgie"],
     "phone": "+49 176 11110006", "email": "k.mueller@uks.eu",
     "shifts_this_week": 2, "available_nights": True},
]

SYSTEM = """You are a shift scheduling assistant for Universitätsklinikum des Saarlandes (UKS) in Homburg.
HR will describe a last-minute shift gap. You will:
1. Review the staff database provided.
2. Identify the best 2-3 candidates (match qualification, prefer fewer shifts this week, available for night if needed).
3. Draft a short, professional WhatsApp/SMS message to send each candidate asking if they can cover the shift.
4. Output a clear summary with contact details.

Always be empathetic but concise. Time is critical in hospital settings."""


def find_staff(gap_description: str) -> str:
    staff_context = "\n".join([
        f"- {s['name']} ({s['role']}) | Quals: {', '.join(s['qualifications'])} | "
        f"Shifts this week: {s['shifts_this_week']} | Night available: {s['available_nights']} | "
        f"Phone: {s['phone']}"
        for s in STAFF_DB
    ])
    prompt = f"""Shift gap reported:
{gap_description}

Available staff:
{staff_context}

Find the best candidates and draft contact messages."""
    return ask(prompt, system_instruction=SYSTEM)
