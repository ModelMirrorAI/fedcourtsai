# Reasoning — Jack v. Whateley, No. 26-584 (arrival moment)

**P(grant) = 0.17.**

## What I read
- Snapshot `record/snapshots/2026-11-04.json`: paid petition docketed Nov 3, 2026, filed Oct 29; one entry (petition filed, response due Dec 3). No distributions, no CVSG — the arrival moment's defining state, not a data gap.
- `record/context.json`: forward mode, `band: state`, `salience_version: sal-v6`, `cert_anchor.rate` = 0.235 (10 prior Terms).
- `record/documents/questions-presented.txt` and `petition.txt` (read in full through the vehicle section). I skimmed `decision-below.txt`/`appendix.txt` only to confirm the petition's characterization. The 4th Circuit opinion is published, and the CourtListener record matches No. 25-1751, decided 2026-07-31. `lower-court-docket.txt` shows no en banc petition.
- `record/same-question.json`: no petition scored above the 0.5 threshold.
- Corpus lookup of Gilliam v. Gerregano, No. 25-107: denied 2025-12-08 after 2 distributions. It had several amici, including FIRE, Volokh/Simon Tam, and ACLJ.

## Anchor
This is a state petitioner (Virginia DMV Commissioner, represented by the Virginia SG's office), so the class floor is `state`. The frozen `cert_anchor` is 23.5%, and the statpack table's `state` reached figures from OT2017–OT2025 run 14–39%.

## Adjustments
Factors pushing up:
- Real, acknowledged split. The 4th Cir. and Maryland (Mitchell) hold that vanity-plate characters are private speech. Tennessee (Gilliam) and Indiana (Vawter) hold they are government speech.
- This is now the first federal court of appeals ruling. Tennessee's opposition to cert in Gilliam leaned on the absence of one, and the petition answers that directly.
- The issue is a pure question of law. Walker expressly reserved it.
- A state is the losing government party. The Court often takes a sovereign's petition when a federal court has struck down how its program is administered.

Factors pushing down:
- **Interlocutory posture.** The 4th Circuit vacated and remanded on forum analysis, so no final judgment exists. Virginia may still win on remand under nonpublic- or limited-forum reasonableness. That gives the Court a classic reason to deny now. The petition argues around this with Hosanna-Tabor and Mount Lemmon, but it is a real drag.
- **The Court denied Gilliam last Term** with the same split, minus a circuit court. That shows limited appetite, though a petition from a winning state's opponent is a different posture.
- **The 7th Circuit (M J Nichols) was argued Sept. 2026 and is pending.** The Court may wait to see whether the split deepens, or for a vehicle with a final judgment.
- The facts are an unappealing vehicle ("FTP&ATF"), though that hardly matters on a government-speech threshold question.

Net: I start at the state anchor and shade down for the interlocutory posture and the recent Gilliam denial, but not far, given the federal-circuit conflict. Result: 0.17.

## Other claims
- relist-increment 0.97: from zero distributions, any first distribution counts. Only withdrawal could prevent one.
- cvsg-increment 0.03: the dispute is state-on-private, the United States has little stake, and federal plates are not at issue.
- summary-disposition-route 0.05 given a grant: no intervening decision to GVR on, and a summary reversal on an open doctrinal question is implausible.
- dissent-from-denial 0.10 given a denial: Gilliam appears to have been denied without a noted writing. Alito (who wrote the Walker dissent) or Thomas might write respecting an interlocutory denial, but that is unlikely.

## Uncertainty
I did not read the respondent's position, since no BIO exists yet. I did not verify the Gilliam order text for writings. The corpus row shows only the denial. No MCP or web retrieval was attempted.
