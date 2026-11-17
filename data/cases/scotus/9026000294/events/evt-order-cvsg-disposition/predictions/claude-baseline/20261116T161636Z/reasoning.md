# Reasoning — Owens v. Taliban, No. 26-294 (CVSG moment)

**P(any grant) = 0.27; call: denied.**

## What I read
- Snapshot `2026-11-16.json`: paid petition from the Second Circuit, filed Aug 31 2026; no brief in opposition (the Taliban has not appeared); one amicus brief (Naseer Faiq, chargé d'affaires of Afghanistan's UN mission, filed across all three dockets); distributed for the Nov 6 and Nov 13 conferences; CVSG issued Nov 16 2026.
- `petition.txt` / `questions-presented.txt`: one question — whether courts must independently decide if an entity is a "foreign state" under the FSIA or must defer to Executive statements (a State Department fact sheet and a DOJ district-court letter). The petition reports a divided panel (Judge Sullivan dissenting in part) and a denial of rehearing en banc with five judges dissenting.
- `lower-court-docket.txt`: confirms rehearing en banc was sought and denied; it records "dissent noted: no", which conflicts with the petition's account of five dissenters. I follow the petition (its appendix lists the dissenting opinions), as the prompt directs. No `decision-below.txt` was staged.
- `record/related/`: 26-292 (Havlish) and 26-293 (Ashton), both `vided-amicus` rows with one shared brief. I read both dockets: same Second Circuit judgment, same extension application, same conference dates, and a CVSG the same day. They are true companions. Havlish also drew a state amicus brief (Iowa et al.) and a supplemental brief. Both companion CVSG entries note Justice Kagan took no part; this docket's entry carries no such note.
- `same-question.json`: empty list — nothing to rest on.
- No brief in opposition was filed, so there is no opposition text to weigh.

## Anchor
- `context.json` band `high` (sal-v8), `cert_anchor.rate` = 0.350. The amicus line (`some` arm, 543 resolved) is 0.352 — same number.
- Statpack CVSG cut (paid scored segment): 166 resolved; granted 29.5% + GVR 6.0% = 35.5% grant family, denied 62.0%. Also the same number. It pools every Term and is not split by the SG's recommendation.

## Adjustments (net down to 0.27)
Down:
- The decision below deferred to the Executive on statehood/recognition. The Solicitor General's institutional interest is to defend that deference, and the United States' own district-court filing is what the panel relied on. I think a recommendation to deny is more likely than not (roughly 60–65%), and the Court follows a deny recommendation most of the time. This is my judgement; no committed table conditions on the recommendation, and the present administration's view on these assets may differ from the earlier filing.
- The claimed split is soft. The First, Third and Sixth Circuit cases the petition cites applied the Restatement test or addressed alter-ego status; none squarely rejected deference to an Executive statement on statehood. The petition's stronger framing is "first circuit ever to hold this", which is an error-correction pitch.
- This petition is the weakest vehicle of the three: it arises from a denied *pre-judgment* attachment, and it presents only the deference question. If the Court takes the issue it may grant Havlish (judgment creditors, more amici) and hold this one.

Up:
- The Court called for the SG's views with no response on file, after one relist-style second distribution — a real sign of interest.
- Five en banc dissenters, including the Chief Judge, and separate writings; a foreign-affairs/separation-of-powers question with about $3.5 billion at stake; experienced Supreme Court counsel.
- A hold followed by a GVR would count as a grant, which is why I do not discount much for the vehicle point.

## Other claims
- `relist-increment` 0.96: two distributions so far; the petition will be redistributed after the SG files. Only a withdrawal/dismissal first would stop that.
- `cvsg-increment` 0.02: already issued; vacuous for this cell.
- `summary-disposition-route` 0.20 (conditional on grant): mostly the hold-for-Havlish-then-GVR path; a straight summary reversal is unlikely.
- `dissent-from-denial` 0.08 and `order-writers`: small; slightly higher for Thomas, Alito and Gorsuch on a text-over-deference theme. Kagan is low because she appears recused in the companions.

## Where to discount me
- I have not seen the Second Circuit opinion itself, only the petition's description.
- The SG's recommendation is the dominant unknown and I am guessing its direction.
- I recall the general background of this litigation (the frozen Da Afghanistan Bank funds and the 2025 Second Circuit ruling) from training; I know of no outcome for this petition.
- Retrieval: one corpus query (generic granted priors, not informative for this case) and the statpack. No CourtListener MCP or web calls.
