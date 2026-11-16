# Reasoning — Inendino v. Nance-Holt, No. 26-522 (cert, distribution moment)

**P(grant) = 0.07; call: denied.**

## What I read
Snapshot `2026-11-16.json`, `context.json`, the questions presented, the petition (QP, split section, vehicle section), the party letter, `lower-court-docket.txt`, and the opening of `decision-below.txt` (Seventh Circuit, No. 24-2908, Lee, J., joined by Ripple and Pryor; published; the CourtListener copy is dated 2026-07-20 against a 2026-07-16 judgment, but the caption, number and holding match what the petition describes, so I treat it as the judgment under review). No brief in opposition exists yet. `same-question.json` lists no matching petitions, so nothing here rests on a hold or a companion.

## Anchor
- `context.json` freezes band `baseline` (sal-v8) with `cert_anchor.rate` = 0.0517. That is the yardstick.
- `cert_amicus_line` (arm `some`, basis `arm`, n=2315) gives 0.163. I weigh it but do not adopt it: the prompt itself warns the `some` rate runs high in a weak band, and one brief from a local police union is the weakest form of amicus support.
- Statpack cross-checks: CA7 petitions grant-family about 2.5%; amicus-count bucket `1` about 14.8% grant family (n=1163), `2+` about 22.7% (n=1453), both read at disposition.

## Adjustments up
- **Response requested after a waiver** (Nov 2, due Dec 2; the City has moved for an extension). At least one chambers wanted the City's answer. No committed table conditions on this; my own prior is that paid petitions drawing a call for response are granted at very roughly 8–10%, a modest step above the band rate.
- **Amicus interest.** One brief is filed (Illinois Council of Police), and counsel's letter says FIRE, the Fraternal Order of Police and the ACLJ intend to file by Nov 18. That would move the petition into the `2+` bucket. I discount the letter slightly as a statement of intent, not a filing.
- **A Justice has asked for this question.** Justice Thomas's statement respecting denial in *MacRae v. Mattos* criticised crediting speculative disruption under Pickering, and the petition is built around it. The call for a response is consistent with interest from that quarter.
- The Seventh Circuit conceded the record lacked meaningful evidence of workplace disruption and rested on public trust, which isolates the legal question more cleanly than usual. Clinic counsel (FSU First Amendment Clinic) is competent though not a repeat Supreme Court specialist.

## Adjustments down
- **The facts are poor for the petitioner.** The posts were racially offensive, directed at groups the firefighter/EMT served in a predominantly Black neighbourhood, on a public page identifying him as a CFD firefighter, and two members of the public complained. A Court inclined to tighten Pickering would likely prefer a more sympathetic speaker, and the City's BIO will say the public-trust harm here was evidenced, not speculative.
- **Pickering balancing is fact-bound.** The claimed five-way split is largely a description of how circuits phrase a case-by-case balance; the BIO will characterise it that way with some force.
- **Recent denials on the neighbouring question.** *MacRae* was denied with only one Justice writing, and *Hedgepeth v. Britton* (No. 25-819, also CA7, Paul Clement as counsel, several amici) was denied — the corpus row shows it denied after two distributions. Those say there are not four votes eager for this area on better-lawyered vehicles; the petition's answer is that this record is cleaner on the evidence point, which is fair but not decisive.
- Qualified immunity for the individual defendants is in the background (the appendix mentions it); the City is also a defendant, so it is a minor vehicle point only.

Netting these: slightly above the 5.2% anchor, well below the amicus-line 16%. 0.07.

## Other claims
- `relist-increment` 0.97: the docket shows one distribution (conference of 11/13/2026), superseded by the Nov 2 call for a response. The petition must be distributed again once the response is in; only a withdrawal or dismissal avoids it.
- `cvsg-increment` 0.01: no federal interest; the Court does not ask the SG about municipal Pickering disputes.
- `summary-disposition-route` 0.12 (conditional on grant): I know of no pending merits case that would produce a GVR; a summary reversal of a fact-bound balancing decision is possible but unlikely. Most of any grant mass is plenary.
- `dissent-from-denial` 0.13 (conditional on denial): above the tiny base rate because Justice Thomas wrote on this exact theme in *MacRae*; below a coin flip by a wide margin because he has already said his piece and the facts here are unattractive.
- `order-writers`: consistent with the above — Thomas carries most of it, small amounts for Alito and Gorsuch, token for the rest.

## Uncertainty and discounts
- I have not seen the BIO; my read of the opposition is inference.
- My call-for-response conditional rate is from general knowledge, not a committed table.
- I did not verify the petition's characterisation of the circuit split against the cited cases, nor the *MacRae* / *Hedgepeth* citations beyond the corpus row for 25-819.
- The context's `response_requested` field is null although the snapshot shows the Nov 2 entry; I read the snapshot. The band (`baseline`) therefore does not reflect that signal, which is part of why I sit above the anchor.
- No knowledge of the outcome; forward cell, and I did not search for this case's disposition or anyone's forecast.
