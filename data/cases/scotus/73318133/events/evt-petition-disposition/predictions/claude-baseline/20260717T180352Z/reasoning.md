# Veto v. The Boeing Company, No. 25-1270 — petition disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.002.**

## The case

Christopher Veto, proceeding pro se (paid docket, no counsel of record), petitions
from an unpublished Ninth Circuit memorandum (No. 24-7060, decided February 6,
2026) affirming summary judgment for Boeing in a California wrongful-termination /
whistleblower-retaliation action (C.D. Cal. No. 8:24-cv-00509). Veto alleges he was
suspended and separated after reporting marijuana use by coworkers at Boeing's Long
Beach facility; the district court and Ninth Circuit held he lacked an objectively
reasonable belief that his complaints disclosed a violation of law (the Cal. Lab.
Code §§ 1102.5/6310 "reasonable cause" standard) and that his complaints were not
corroborated.

Docket posture as of the 2026-07-17 snapshot: petition filed May 5, 2026, docketed
May 8; response was due June 8, 2026 and no brief in opposition appears on the
docket; distributed June 24, 2026 for the Conference of September 28, 2026 (the
Term-opening "long conference"). No relist, no CVSG, no amicus support.

## Why this petition will be denied

1. **No certworthy question.** The questions presented (nine of them) do not
   allege a circuit split, a conflict with this Court's precedent, or an important
   unsettled federal question. Several are literally advisory-opinion requests
   ("What is the penalty to Boeing for…?", QPs 2–4) or abstract policy questions
   (whether Boeing is a monopoly, whether Ex-Im Bank financing is unfair — QPs 6–7),
   which are not questions a court of certiorari review can answer. The one
   arguable legal claim — that federal marijuana illegality (21 U.S.C. § 802) made
   his complaints objectively reasonable under state whistleblower law — is a
   fact-bound application of a state-law standard in a diversity case, the classic
   Rule 10 denial profile.

2. **Fact-bound, splitless, unpublished, interlocutory-free error correction.**
   The decision below is a non-precedential memorandum applying settled summary-
   judgment and state-law retaliation standards to one employee's record. The
   petition's "Reasons for Granting" section argues national significance from
   aviation-safety headlines and drug policy, not from any legal conflict.

3. **Relief the Court cannot grant on certiorari.** The petition asks the Court to
   declare dozens of enumerated state cannabis statutes unconstitutional, enjoin
   Boeing's Long Beach operations, seize aircraft, break Boeing into separate
   corporations, bar named engineers from practicing, and award a $20 million fine
   to the petitioner — remedies far outside the case's actual judgment and outside
   Article III bounds for this posture. This signals the petition will not survive
   a cert-pool memo's first pass.

4. **Docket signals all point the same way.** No brief in opposition on the docket
   (respondent has evidently not been called on to respond); a single distribution
   to the long conference, where the overwhelming mass of unrelisted petitions are
   denied on the first order list of the Term; no relist, no CVSG, no amici.

## Base rates and adjustment

From the committed `metrics/statpack.md` (live/historical slice, denial-reweighted):

- Modern discretionary-cert petitions: ~2.5–3.3% grant rate per recent Term
  (Term 2025: denied 95.4%, granted 2.5%).
- **Relist count 0** (this case's bucket): denied 97.3%, granted **0.8%**.
- Originating circuit CA9: granted 3.0% — no meaningful lift.
- CVSG none: granted 3.0% vs 27.1% with CVSG — this case has none.

The statpack's salience-band table is not present in the committed roll-up I read,
so the relist-0 bucket is my closest yardstick. This petition sits far below the
median relist-0 paid petition: it is pro se, splitless, fact-bound, and seeks
relief unavailable on certiorari. Pro se paid petitions of this profile are granted
at a rate well below even the 0.8% bucket average; plenary grants effectively
require counsel and a genuine legal conflict. There is no intervening-decision hook
that could support a GVR either. I set P(grant, including GVR) at **0.002** and
predict **denied** — the most likely concrete path being denial on the
October 2026 order list following the September 28 long conference. The main
alternative disposition (dismissal under Rule 39 or withdrawal) is far less likely
than a straight denial on a paid docket.

## Big-case score

0.03. Boeing is a newsworthy respondent and the petition invokes aviation-safety
headlines, but the decision here — denial of a pro se employment petition — would
be a one-line order with no doctrinal, market, or public consequence.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket entries, paid
  case type, conference distribution).
- Provisioned `record/documents/petition.txt` (full 60-page petition text,
  including the questions presented, statement, and suggested remedies) —
  `documents.json` shows no brief in opposition was available to fetch, consistent
  with the docket showing none filed.
- Committed base rates in `metrics/statpack.md`.
- One `fedcourts query` for recent resolved SCOTUS priors and one CourtListener
  MCP docket lookup confirming the case remains pending (forward mode) — see
  `retrieval.md`.
