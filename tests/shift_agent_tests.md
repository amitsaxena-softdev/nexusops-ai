# Shift Replacement Agent — Manual Test Cases

Paste each prompt into the shift agent text area and click **Find Staff & Draft Messages**.
Each test targets one specific filter rule. Verify the agent's output against the expected result.

---

## Test 1 — Baseline Demo (ICU, BLS + ACLS)

**Rule tested:** Basic eligibility — correct dept + certs + off tonight + hours OK.

**Prompt to paste:**
```
Felix Haddad (HOSP-1059) just called in sick. He was scheduled for tonight's ICU night shift
(19:00–07:00, Saturday 20 June). We need a Registered Nurse with BLS and ACLS. Who can cover?
```

**Expected — should appear:**
| Name | ID | Why eligible |
|------|----|--------------|
| Mateo Bianchi | HOSP-1079 | ICU RN · BLS+ACLS · Sat=Off · 24h headroom · OT OK |
| Zara Dlamini | HOSP-1019 | ICU RN · BLS+ACLS · Sat=Off · 18h headroom · OT OK |
| Otto Okafor | HOSP-1031 | ICU RN · BLS+ACLS · Sat=Off · 12h headroom · OT OK |

**Must NOT appear:**
- Hassan Esposito (HOSP-1055) — On Leave
- Caleb Marino (HOSP-1010) — CNA role, already working Sat
- Isla Lindgren (HOSP-1095) — OT OK = No (lower priority, may appear 4th)
- Any Emergency department nurse

---

## Test 2 — Department + Certification Filter (Emergency, TNCC required)

**Rule tested:** Agent must filter by Department first, then check that TNCC literally appears in the Certifications column. ICU nurses must not appear even if they are available and have BLS+ACLS.

**Prompt to paste:**
```
We need Emergency night shift cover tonight (19:00–07:00, Saturday 20 June).
The shift requires TNCC, BLS, and ACLS. Several nurses are off tonight — who qualifies?
```

**Expected — should appear:**
| Name | ID | Why eligible |
|------|----|--------------|
| Nora Nguyen | HOSP-1043 | Emergency RN · BLS+ACLS+TNCC · Sat=Off · 12h headroom · OT OK |
| Greta Novak | HOSP-1089 | Emergency NP · BLS+ACLS+TNCC · Sat=Off · 12h headroom · OT OK |

**Must NOT appear (all reasons):**
| Name | Why excluded |
|------|-------------|
| Otto Okafor | ICU dept — wrong department |
| Mateo Bianchi | ICU dept — wrong department |
| Isla Lindgren | ICU dept — wrong department |
| Aisha Hernandez (HOSP-1017) | Emergency but already working Sat Day shift + over cap (48/36) |
| Malik Dubois (HOSP-1052) | Emergency but already working tonight (Sat=N) |
| Malik Romano (HOSP-1077) | Emergency, TNCC ✓, Sat=Off, but 48/48 hrs — at hard cap |
| Hana Costa (HOSP-1091) | Emergency, TNCC ✓, Sat=Off, but 36/30 hrs — already over cap |
| Niko Sato (HOSP-1093) | Emergency but already working Sat Day shift + over cap (48/30) |

**This is the hardest test.** If the agent returns ANY ICU nurse, the department filter is broken.

---

## Test 3 — Already Working Trap (offers from staff already scheduled)

**Rule tested:** Agent must check the schedule code for tonight and exclude anyone already working — even if they volunteer.

**Prompt to paste:**
```
Emergency night shift tonight (19:00–07:00, Saturday 20 June) needs cover. TNCC, BLS, ACLS required.
Malik Dubois and Niko Sato both called to say they can come in. Can we take them?
```

**Expected answer:** Neither can cover.
- **Malik Dubois (HOSP-1052):** Sat = N — already scheduled for tonight's night shift. Double-booking.
- **Niko Sato (HOSP-1093):** Sat = D — works the day shift ending ~19:00. No rest before night shift. Also already over cap (48/30).

Agent should say no eligible candidates found from those two, and ideally surface Nora Nguyen and Greta Novak as the correct alternatives.

---

## Test 4 — Hours Cap Trap (off tonight but over weekly limit)

**Rule tested:** Agent must apply the hours cap check. Staff can be off tonight and have the right certs but still be ineligible if their scheduled hours + 12 would exceed Max Hrs/Week.

**Prompt to paste:**
```
Emergency department needs a nurse with TNCC for tonight's night shift (19:00–07:00, Saturday 20 June).
Malik Romano and Hana Costa are both off tonight and have TNCC. Can either of them cover?
```

**Expected answer:** Neither is eligible.

| Name | Scheduled hrs | Max hrs | Headroom | Result |
|------|--------------|---------|----------|--------|
| Malik Romano (HOSP-1077) | 48 | 48 | 0 | At hard cap. Adding 12h = 60 > 48. INELIGIBLE. Also OT OK = No. |
| Hana Costa (HOSP-1091) | 36 | 30 | -6 | Already over cap. Adding 12h = 48 > 30. INELIGIBLE. |

Agent should correctly exclude both and suggest Nora Nguyen / Greta Novak as the eligible alternatives.

---

## Quick reference — Emergency staff eligibility matrix (Sat 20 June)

| Name | Dept | TNCC | Sat | SchedHrs/Max | Verdict |
|------|------|------|-----|--------------|---------|
| Nora Nguyen (1043) | Emergency | ✅ | Off | 36/48 (+12 headroom) | ✅ ELIGIBLE |
| Greta Novak (1089) | Emergency | ✅ | Off | 36/48 (+12 headroom) | ✅ ELIGIBLE |
| Aisha Hernandez (1017) | Emergency | ✅ | Day | 48/36 (over cap) | ❌ Working + over cap |
| Malik Dubois (1052) | Emergency | ✅ | Night | 24/48 | ❌ Already on tonight's shift |
| Malik Romano (1077) | Emergency | ✅ | Off | 48/48 (no headroom) | ❌ At cap, OT No |
| Hana Costa (1091) | Emergency | ✅ | Off | 36/30 (over cap) | ❌ Already over cap |
| Niko Sato (1093) | Emergency | ✅ | Day | 48/30 (over cap) | ❌ Working + over cap |
| Hassan Novak (1004) | Emergency | ❌ (BLS only) | Night | — | ❌ Missing TNCC, working |
