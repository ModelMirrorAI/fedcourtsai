# Rationale: P(grant) = 0.10

## Inputs read

- `record/context.json`: mode `forward`, band `state` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, `signals_observable` true, `cutoff` null.
- `record/snapshots/2026-10-08.json`: paid petition docketed July 7, 2026 (No. 26-22, CA9 No. 23-15602); waiver by one respondent (Dr. Freeman, ACLU) July 29; distributed August 19 for the September 28 conference; response requested August 26; both the Guam Society respondents and the Governor of Guam obtained extensions to November 24, 2026. No amicus filings.
- `record/documents/petition.txt` (121 pages, text truncated, not OCR) and `questions-presented.txt`: the QP, the statement of the case, Parts I–IV of the reasons, the Ninth Circuit's two-sentence dismissal order (App. A), and Judge VanDyke's statement respecting denial of rehearing en banc (App. F). No brief in opposition is on the docket yet, so the respondents' side is inferred from the appellate record rather than read.

## Anchor

Cert-stage cell with a frozen `state` band under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table. Pooling the `state` column's bracketed `reached` figures over Terms 2017–2025 (all nine rendered Terms strictly before this case's Term 2026) gives:

| pooled state-band reached rate | n |
| --- | --- |
| 23.6% | 419 |

That is the yardstick the evaluator scores this cell against. For context, the paid relist-count cut's relist-0 bucket runs at a grant family of about 1.7%, and the CVSG cut's `none` bucket at about 6.3%.

## Adjustments from the anchor

**Down, substantially.** A typical petition in the state band is a state that lost on a substantive federal question, often with a split. This one is weaker on every axis the Court cares about:

- **No conflict.** The petition identifies no circuit split. Its only comparator, the Fifth Circuit's McCorvey v. Hill, reached the same result on Roe-era Texas statutes, and the petition can only distinguish it by date.
- **Binding territorial law decides the vehicle.** The Ninth Circuit dismissed in light of In re Leon Guerrero, 2023 Guam 11, in which the Supreme Court of Guam held P.L. 20-134 impliedly repealed and of no force. Federal courts take that construction as given. Vacating a 1990 injunction against a statute that does not exist gives the Attorney General no enforcement power, which is why the court of appeals saw no effectual relief. The Court is unlikely to spend a grant on a mootness holding whose premise it cannot revisit.
- **The friendliest judge below conceded the point.** Judge VanDyke's published statement, which the petition leans on, says the panel "made the right call" and explains that the injunction does not restrain Guam from enforcing any future abortion law. That removes the "lingering Roe injunction" hook a conservative Justice might otherwise find attractive. The en banc call failed with no dissent noted.
- **Thin petition.** Part I rests on the Court's "supervisory responsibility," which is not a Rule 10 ground; Part IV's importance argument is generic to aging injunctions. The Guam Attorney General's office is not a repeat Supreme Court advocate, and the territory's own Governor is a respondent opposing the petition, represented by experienced Supreme Court counsel.
- **Guam-specific.** A one-off posture in a territory with no prospect of recurrence elsewhere in this form.

**Up, modestly.** The Court requested a response after a waiver, which means at least one chambers thought the petition worth a reply. Historically a response request raises a paid petition's odds well above the no-response floor, and the Dobbs-cleanup framing has some appeal to the Justices who joined Dobbs. The Munsingwear argument in Part III is the one piece a Justice could act on cheaply, through a GVR directing vacatur of the district court's 60(b)(5) denial.

Netting these, I land at **0.10**, well under the band anchor. I would put the plausible range at 0.05–0.18. The main way I am wrong on the high side is if the Court treats this as a vehicle to say something general about Rule 60(b)(5) after Dobbs; on the low side, the response request may be no more than a single clerk's curiosity.

## Claims

- `disposition` 0.10 — equals the top-level probability.
- `relist-increment` 0.96 — the docket shows one distribution, superseded by the response request; the petition must be redistributed after the November 24 response, so another distribution entry is near-certain. The residual covers withdrawal, dismissal, or a docket-parse oddity.
- `cvsg-increment` 0.04 — no federal interest; the paid CVSG cut shows invitations are rare (about 1.2% of the segment) and this petition has less federal hook than most.
- `summary-disposition-route` 0.45 — conditional on a grant. The harness baseline for a Term-2026 cell is 0.353 (paid cert-order share of grants pooled over 2017–2025). I go above it because the only grant-worthy argument is a Munsingwear vacatur that is naturally handled in the cert order, and because the record is too thin for plenary review.
- `dissent-from-denial` 0.20 — conditional on a denial. The response request and the abortion-adjacent subject raise the chance of a statement, but VanDyke's concession of mootness lowers it; a bare denial is the expected outcome.

## Big-case score

0.35. Newsworthy because it is abortion-adjacent and would be the Court's first word on Roe-era injunctions after Dobbs, but legally narrow and practically inert in Guam.

## Retrieval and its limits

CourtListener (forward mode, unrestricted) confirmed the published rehearing order with VanDyke's statement, the Guam Supreme Court decision's existence, and turned up no other post-Dobbs Rule 60(b)(5) mootness opinions on a text search. A docket search for No. 26-22 on CourtListener returned nothing, so the supremecourt.gov snapshot (dated today) is the only docket source; it is current as of this run. One `fedcourts query` over granted 2020s SCOTUS rows returned no comparable prior, as the query surface has no text filter, so my comparators come from the petition and general knowledge rather than the corpus. I did not encounter any disposition of this petition, and nothing in the snapshot suggests one exists.

## Where to discount me

The brief in opposition is not yet filed, so I am guessing at the respondents' arguments. The Munsingwear angle is my own reading of Part III rather than the petition's headline request, so my summary-route number depends on a route the Court might never consider. And the state-band anchor is wide: a thin caption class pooled across nine Terms with per-Term rates from 14% to 41%.
