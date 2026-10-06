# Rationale for the numbers

**P(grant) = 0.42; predicted disposition `denied`; claims as stated in `prediction.json`.**

## Inputs read

- `record/snapshots/2026-10-05.json` (the provisioned baseline; its last entry is today's CVSG order).
- `record/context.json`: `mode: forward`, `band: high` under `sal-v4`, `distribution_count: 2`, `cvsg_date: 2026-10-05`, `term: 2025`, `cut_kind: date`, `cutoff: 2026-10-06`.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (39 pp., full text), `brief-in-opposition.txt` (44 pp., full text); none flagged `empty_text`.
- `metrics/statpack.md`: the modern-cert disposition table, the relist and CVSG cuts, the originating-circuit cut, and the sal-v4 segment-by-band table.
- Retrieval beyond those inputs is listed in `retrieval.md`. I did not read the predictions on the sibling `evt-petition-disposition` event; this moment is scored separately and I forecast from its own record.

## Anchor

The context's band (`high`) and the table's salience version (`sal-v4`) match, so the band table is the anchor. Pooling the bracketed `reached` figure for `high` over every Term strictly before this case's docket Term (OT2017 through OT2024, the whole rendered window):

| pool | reached rate | n |
| --- | --- | --- |
| high, OT2017–OT2024 | 35.0% | 898 |

The CVSG cut on the paid scored segment says the same thing from another angle: granted 29.4% plus GVR 5.5%, a grant family of 34.9% over 163 resolved petitions. The originating-circuit cut gives CA2 a grant family of about 4.9% (2.6% granted, 2.3% GVR), modestly above the typical circuit, but that is a whole-docket figure that the band already subsumes. I treat 0.35 as the base rate.

## Adjustments up

- **Trajectory.** The Court has twice escalated this petition on its own motion: it called for a response after the respondents waived, and after full briefing it rescheduled and then invited the SG rather than denying. That is already priced into the `high` band, but the CVSG moment is the strongest tier within it.
- **Petitioner strength and amici.** Four major manufacturers with Supreme Court-specialist counsel (Arnold & Porter, Jones Day, Kirkland, King & Spalding); cert-stage amicus briefs from the Chamber of Commerce with NAM and from the Electric Power Supply Association, which signals cross-industry interest in the trade-association question.
- **Two live questions, one with an acknowledged split.** The Sixth Circuit's *Amerigroup* decision rejects the lost-profits route around Illinois Brick, and the statements from Judges Bush and Murphy on rehearing explicitly invite this Court to look at the issue. A companion petition raising the scope of Illinois Brick, *United Biologics v. Amerigroup* (No. 25-1388, docketed June 2026), is pending, which raises the chance the Court resolves the question in one of the two vehicles and gives this case a hold-and-GVR path that counts as a grant.
- **Question 2's valence.** Treating joint lobbying as evidence of conspiracy has a First Amendment and Noerr-Pennington flavor the current majority tends to find attractive, and it is the question the amici brief.

## Adjustments down

- **Interlocutory posture.** The Second Circuit vacated a dismissal and remanded for leave to amend; nothing is final. The SG frequently cites this posture against review, and the Court often agrees even where a question is otherwise worthy.
- **The BIO is effective on vehicle.** On question 2 it shows that the panel's plausibility finding rested first on parallel action against individual self-interest and on the one-business-day timing between AstraZeneca's private notice and Sanofi's public announcement, with the lobbying allegations as "further support"; the petition does not challenge those primary findings. The Second Circuit's own precedent (*Gamm*) already says mere opportunity to conspire is not enough, which undercuts the claimed split. On question 1 the BIO argues there was no overcharge at all because sales were refused, so the Illinois Brick question the petition frames may not be fairly presented, and it raises a preservation doubt.
- **The SG's likely posture.** The Antitrust Division has generally defended the pleading standard as applied holistically and has not pressed to widen Illinois Brick's bar; the federal government also has its own 340B interests that cut against siding with the manufacturers on the policy backdrop. My rough decomposition is P(SG recommends grant on at least one question, or a hold for *Amerigroup*) about 0.40, with the Court following a grant recommendation about 85% of the time and granting against a denial recommendation about 15% of the time, which produces roughly 0.43 before rounding.
- **Recent antitrust CVSGs** have more often ended in denial than grant, by my impression rather than a corpus figure, so I did not push the number above the mid-40s.

Net: 0.35 anchor, up for trajectory, counsel, amici, the companion petition, and the Illinois Brick split, down for interlocutory posture and the BIO's vehicle arguments, landing at **0.42**. Since that is below one half, `granted` is 0 and `predicted_disposition` is `denied`; conditional on a grant the likeliest label is plenary `granted`, with a GVR via *Amerigroup* the minority route (hence `summary-disposition-route` at 0.18, a little above the CVSG bucket's 16% GVR share of grants because the companion path is concrete here).

## Claims

- `disposition` 0.42, equal to `probability`.
- `relist-increment` 0.96: from two distributions, a CVSG petition is always redistributed once the SG files; the residual is settlement or withdrawal before then.
- `cvsg-increment` 0.02: the CVSG is on the docket, so the harness masks this claim; stated for completeness.
- `summary-disposition-route` 0.18, conditional on a grant, as above.
- `dissent-from-denial` 0.10, conditional on denial: a CVSG'd petition the SG recommends denying usually draws no writing, but the Illinois Brick critique has standing advocates on the Court.

## Uncertainty and where to discount me

- The largest uncertainty is the SG's recommendation, which will not exist for months; this cell is a forecast of that brief as much as of the Court.
- I could not verify the posture of the *Amerigroup* companion petition beyond its docket existence (CourtListener shows no entries for it), so the hold-and-GVR path is reasoned from the BIO's description of that petition, not from its docket.
- The corpus query surface returned no CVSG-bearing rows among the 400 most recent 2020s SCOTUS priors, so the CVSG-conditional evidence here is the statpack cut alone, not case-level priors.
- I carry no knowledge of this petition's outcome; it was invited today and is pending.
