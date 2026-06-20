from shared.llm import ask_with_file, ask

SYSTEM = """You are an intelligent invoice processing assistant for Globus Group (St. Wendel).
Your job is to analyse supplier invoices and route them to the correct internal department.

Department routing rules:
- IT / Software / Hardware / Cloud / Telecom → IT Department
- Office supplies / Furniture / Stationery → Administration
- Advertising / Marketing / Events / Media → Marketing
- Logistics / Freight / Shipping / Warehouse → Logistics
- Cleaning / Catering / Security / Facility → Facility Management
- Legal / Consulting / Audit → Finance & Legal
- Raw materials / Production parts → Procurement
- Anything else → Finance (general)

Always respond in this exact structure:
---
VENDOR: <name>
INVOICE NO: <number or N/A>
DATE: <date or N/A>
TOTAL AMOUNT: <amount with currency>
VAT: <amount or N/A>
LINE ITEMS: <bullet list>
CATEGORY: <category>
ROUTED TO: <department>
REASON: <one sentence>
FLAGS: <any anomalies, or "None">
---"""


def process_invoice(file_bytes: bytes, mime_type: str) -> str:
    prompt = (
        "Analyse this invoice document. Extract all fields and route it to the correct department "
        "following your routing rules. Highlight any anomalies."
    )
    return ask_with_file(prompt, file_bytes, mime_type, system_instruction=SYSTEM)


def process_invoice_text(text: str) -> str:
    return ask(f"Analyse this invoice and route it:\n\n{text}", system_instruction=SYSTEM)
