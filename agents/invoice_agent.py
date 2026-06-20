from shared.llm import ask_with_file, ask

PARSE_SYSTEM = """You are an invoice data extractor for Globus Group (St. Wendel).
Your ONLY job is to extract every visible field from the invoice document.

The document may be a bad scan, faded photocopy, angled photo, or digital file.
Extract whatever is visible. Never refuse. Never say the document is invalid.
If a field is partially visible, give your best reading. If truly invisible, write N/A.

Return ONLY this structure — nothing else:
---
VENDOR: <supplier name>
INVOICE NO: <invoice number>
DATE: <invoice date>
TOTAL AMOUNT: <total with currency symbol>
VAT: <VAT amount or rate>
CATEGORY: <type of product or service, e.g. Gas supply, Software licenses, Hardware>
LINE ITEMS:
  - <item description and amount>
---"""

ROUTE_SYSTEM = """You are a routing assistant for Globus Group's Finance inbox.
Given extracted invoice data, determine which internal department should receive it.

Routing rules (apply the first matching rule):
- Software / SaaS / Cloud / IT services / Telecom / Internet / Hardware → IT Department
- Office supplies / Stationery / Furniture → Administration
- Advertising / Marketing / Events / Media / Design → Marketing
- Freight / Logistics / Shipping / Warehouse → Logistics
- Gas / Electricity / Water / Utilities / Cleaning / Catering / Security / Facility → Facility Management
- Consulting / Legal / Audit / Professional services / Accounting → Finance & Legal
- Hotel / Accommodation / Travel → Finance & Legal
- Raw materials / Production parts / Manufacturing → Procurement
- Anything else → Finance (general)

Return ONLY this structure — nothing else:
---
ROUTED TO: <department name>
REASON: <one sentence explaining the routing decision>
STATUS: READY TO FORWARD
STATUS REASON: Invoice data extracted and routed successfully.
---"""


def parse_invoice(file_bytes: bytes, mime_type: str, context: str = "") -> str:
    prompt = context + "\n\nExtract all fields from this invoice." if context else "Extract all fields from this invoice."
    return ask_with_file(prompt, file_bytes, mime_type, system_instruction=PARSE_SYSTEM)


def parse_invoice_text(text: str, context: str = "") -> str:
    prompt = f"{context}\n\n{text}" if context else text
    return ask(prompt, system_instruction=PARSE_SYSTEM)


def route_invoice(parsed_data: str) -> str:
    return ask(
        f"Route this invoice to the correct Globus Group department:\n\n{parsed_data}",
        system_instruction=ROUTE_SYSTEM,
    )
