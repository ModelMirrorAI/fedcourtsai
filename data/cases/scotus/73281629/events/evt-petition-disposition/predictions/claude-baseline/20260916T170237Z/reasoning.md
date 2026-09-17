# Rationale for the numbers

**P(grant) = 0.14; predicted disposition: denied.**

## Inputs read

- `record/snapshots/2026-09-15.json` (the provisioned baseline; `context.json` names it, mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025, paid docket).
- `record/documents/questions-presented.txt`, `petition.txt` (120 pages, truncated — I read the petition body and the appended Ninth Circuit memorandum and the start of the district court findings) and `brief-in-opposition.txt` (28 pages, full).
- `metrics/statpack.md`: the modern-cert disposition, relist, CVSG and circuit cuts, and the per-Term "Segment base rate by salience band (sal-v4)" table.
- Beyond the provisioned inputs (forward mode, retrieval unrestricted): petitioner's September 2, 2026 reply and supplemental brief (downloaded from the supremecourt.gov docket, not provisioned), the Fourth Circuit's published opinion in *Kelly v. Altria Client Services* (Aug. 10, 2026) via the CourtListener MCP server, and a CourtListener check of this docket for entries after the snapshot (none). Details in `retrieval.md`.

## Anchor

The band table's heading names `sal-v4`, matching `context.salience_version`, and `elevated` is a column, so the table is my anchor. Pooling the bracketed `reached` figures for `elevated` over the eight rendered Terms strictly before OT2025 (OT2017–OT2024) gives **484.4 / 2810 ≈ 17.2%**. The terminal figure for the band (7–13% per Term) is not the right yardstick because this petition is still in play.

Two things about that anchor for this case. First, the band folds in the relist signal, and the relist cut is the classic pre-grant signal (relist-1 petitions grant ~8% plus ~5% GVR against ~1.7% at relist-0). But this docket's two distributions are not a true relist: the April 15 distribution for the May 1 conference was superseded by the April 24 call for a response, and the July 15 distribution for the September 28 conference is the first at which the petition will actually be considered. The statpack itself notes the count is an upper bound for exactly this reason. Second, what the count does inadvertently capture is the **call for a response after Netflix waived**, which is the Court's own signal that at least one chambers wanted the petition briefed. That signal is real and roughly of the size the elevated band implies, so I treat 17% as a fair prior rather than discounting it for the false relist.

## Adjustments

Upward:

- **The split is real and has just been widened by a published decision.** The BIO's central argument (June 25) is that there is no split: every circuit uses a Hughes-like "formal governing documents" test and the Seventh and Tenth Circuits' results in *Mondry* and *Premera* turned on their facts. On August 10 the Fourth Circuit, in *Kelly v. Altria*, reversed a district court that had applied Hughes-style reasoning and held that a ministerial recordkeeping agreement is a document "under which the plan is operated" because it "governs some part of the plan's process," expressly aligning with *Mondry* and *Premera* in footnote 8. I verified the opinion text on CourtListener; the reply's characterization is accurate. So on the precise question — are administration contracts disclosable — the Fourth, Seventh and Tenth Circuits say yes, and the Ninth Circuit (the unpublished *Hively* order and this memorandum, both bound by the en banc *Hughes*) says no. Kelly does not mention the Ninth Circuit, so the split is not "acknowledged" in the strong sense, but it is now three published decisions against one circuit's entrenched en banc rule, and the Court will see it in the reply/supplemental brief.
- **The Court itself flagged the petition** by calling for a response after a waiver.
- **The legal disagreement is outcome-determinative on the panel's own description.** The Ninth Circuit said the four agreements "govern only the relationship between Netflix and the third parties providing various claims-related services." Under *Kelly*, *Mondry* and *Premera* that is precisely what makes them disclosable. That blunts the BIO's clear-error argument more than the BIO's framing suggests.

Downward:

- **Vehicle.** The decision below is a six-page unpublished memorandum, the case was resolved on Rule 52 findings after a bench trial on a paper record, and the panel layered clear-error review over the district court's document-by-document findings. The Court tends to prefer a published opinion squarely adopting the disputed rule; the BIO exploits this well, and its "future Ninth Circuit panel could go the other way" argument, while weak given *Hughes* is en banc, gives a denial-inclined Justice cover.
- **Importance and stakes.** Zero amicus briefs for a petition claiming exceptional national importance affecting 153 million plan participants. The dispute is over document access and a vacated $765 penalty, with no benefits denial tied to the request. The BIO's point that § 503 and its regulations give claimants access to claim-relevant documents after a denial reduces the practical urgency. The Court has let the Seventh/Ninth disagreement sit since 2009 and denied cert in *Hughes* (1996) and *Faircloth* (1997).
- **Petition quality and counsel.** A solo practitioner's 16-page petition with overheated framing ("Kafkaesque," a "9-1 split" on general interpretation that the BIO credibly shows is mostly a difference in verbal formulation). The Court grants on issues not lawyers, but petitions from non-repeat players carry less credibility in the pool memo and the BIO here is by an experienced Supreme Court advocate.
- **Pathway.** Some of the grant probability runs through a CVSG rather than a September 28 grant. Eventual grant ≈ P(grant without CVSG) + P(CVSG) × P(grant | CVSG) ≈ 0.10 + 0.12 × 0.33 ≈ 0.14.

Net: the negatives (vehicle, stakes, no amici) roughly cancel the positives (Kelly, the CFR), and I land slightly below the 17% anchor at **0.14**.

## Claims

- `disposition` 0.14 — identical to `probability`.
- `relist-increment` 0.30 — from the two-distribution state described above. Components: ~0.09 (grants, nearly all preceded by a relist), ~0.12 (CVSG then redistribution), ~0.09 (relist then deny). Rounded to 0.30 to reflect overlap between the first two.
- `cvsg-increment` 0.12 — ERISA Title I question DOL administers; the Court often wants the SG's views before taking such a question; but the question is narrow and the Court chose a CFR rather than a CVSG when it first flagged the case. Paid-segment CVSG base rate is ~1.2%; for a petition at this stage with a claimed split on a federal statute the conditional rate is an order of magnitude higher.
- `summary-disposition-route` 0.05 — no intervening decision of this Court; no basis for a GVR; per curiam reversal implausible on an open question.
- `dissent-from-denial` 0.05 — low-profile statutory question, no evident champion, unpublished factbound decision below.

## Uncertainties and where to discount me

- I do not know how `sal-v4` weights the response request versus the distribution count, so my claim that the band's 17% is a fair prior for a CFR'd petition is a judgment, not a read of the scorer.
- My sense of the conditional grant rate for called-for-response petitions (~10%) is from general knowledge of Supreme Court practice, not from the statpack, which carries no CFR cut.
- Netflix had not filed a supplemental brief answering *Kelly* as of the September 15 snapshot; if one arrives before September 28 arguing Kelly concerned a recordkeeper rather than a claims administrator, the split argument narrows somewhat.
- The petition text was truncated at 120 pages; I read the petition body, the Ninth Circuit memorandum and the opening of the district court findings, not the full findings. My read of the factual record is therefore mostly from the BIO's and memorandum's descriptions.
- No outcome knowledge: the September 28 conference postdates today (September 16, 2026); CourtListener shows no docket entries after the snapshot, and nothing I retrieved discloses a disposition.
