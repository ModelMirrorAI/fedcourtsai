# Why 0.07, and where to discount me

## What I read

Provisioned inputs: the snapshot `2026-09-18.json`, `context.json` (mode `forward`, band `elevated` under sal-v4, `distribution_count` 2, no CVSG, Term 2025, paid docket), `questions-presented.txt`, `petition.txt` (41 pages, full text), and `brief-in-opposition.txt` (24 pages, full text, filed by the Solicitor General). All three documents extracted cleanly; none was flagged `empty_text` or truncated.

## Anchor

The harness band is `elevated`. Pooling the bracketed `reached` rate for `elevated` across the eight Term rows strictly before Term 2025 in the statpack's sal-v4 segment table (2017 through 2024) gives roughly 17 percent (about 484 weighted grants over about 2,810 weighted petitions that reached the band). That is the yardstick my skill is scored against, so it is my starting point.

## Why I sit well below the anchor

1. **The band overstates this docket's signal.** `elevated` here comes from `distribution_count` 2, which the scorer reads as one relist. But the first distribution (for June 25) was superseded by the Court's call for a response on June 17, and the second (for September 28) is the ordinary post-BIO redistribution. The statpack's own relist-cut caption says a reschedule before first consideration inflates the count. The petition has never been voted on at conference. The correct comparison population is call-for-response paid petitions before their first conference, whose grant rate I estimate at roughly 8 to 12 percent from the relist-1 paid bucket (grant family about 13 percent) discounted for the parse artefact, not the 17 percent reached rate that includes true post-conference relists.

2. **The Court's Bivens record runs one way.** Every Bivens plaintiff to reach the Court since *Carlson* has lost, and the Court has taken the government's petitions (*Egbert*, *Hernández*, *Nielsen v. Watanabe* this Term) while denying plaintiffs' (*Cantú v. Moody* 2020; *Mohamud v. Weyker* twice, the second denial in 2026 on a fabricated-evidence false-arrest theory that the SG cites as controlling here; *Quinones-Pimentel*; *Hernandez v. Causey*; *Johnson v. Terry*). A grant here would be a grant to consider ruling for a Bivens plaintiff, which no four Justices have wanted.

3. **The SG's opposition is strong on vehicle.** The per curiam has no controlling rationale; Judge Lee's ground (fabrication is a different context) is independent of Judge Pérez's (alternative remedy alone suffices); question 2 was addressed by no court below except in a single concurrence; and petitioner's own complaint pleaded the entry-and-search claims against agents other than the respondent, so the "Bivens itself" framing is contestable on the pleadings. The SG also documents a lower-court consensus, post-*Egbert*, that fabricated-evidence Fourth Amendment claims are a new context (Eighth, Ninth, Third, Fourth, Fifth, First Circuits).

## Why I am not lower

- The Court called for a response after the government waived. Some chambers wanted the SG's view, which is a real, if modest, signal.
- Judge Lynch's dissent and Judge Pérez's concurrence both say the false-arrest claim is not a new context. Two of three judges below thought the petitioner was right on question 1.
- *Nielsen v. Watanabe* is pending on a closely related step-one question. A hold and later GVR is a live grant path (I put hold at about 0.30, a plaintiff-side *Nielsen* outcome near 0.25, GVR given both around 0.6, contributing roughly 0.04 to P(grant)). Plenary grant contributes about 0.03. Total about 0.07.

## Claims

- `disposition` 0.07, as above.
- `relist-increment` 0.50: a hold for *Nielsen* alone would eventually add a distribution; without a hold, a call-for-response petition off the long conference relists perhaps 30 percent of the time. 0.30 + 0.70 × 0.30 ≈ 0.51.
- `cvsg-increment` 0.01: the SG is the respondent.
- `summary-disposition-route` 0.60: the GVR path dominates the plenary path in my grant decomposition (0.04 versus 0.03).
- `dissent-from-denial` 0.20: plausible Sotomayor or Jackson writing on a "Bivens on its own facts" denial; recent plaintiff-side Bivens denials have mostly been silent.

## Big-case score

0.45. Decided on the merits it would define whether *Bivens* has any remaining field of operation, which matters to civil-rights litigation broadly. But the modal outcome is a quiet denial, and a GVR would be a footnote to *Nielsen*.

## Uncertainties and discounts

- My estimates of the call-for-response grant rate and of *Nielsen*'s outcome are judgment, not statpack figures. The statpack publishes no call-for-response cut.
- I could not confirm the *Nielsen* grant, its argument date, or the *Mohamud* denial independently: CourtListener's SCOTUS docket rows for 25-417 and 25-760 exist but carry no cert dates or entries. I rely on the SG's brief for those facts, which is a reliable source for them.
- I did not read the Second Circuit opinion itself (cluster 10661588 on CourtListener); both filed documents characterize it at length and largely agree on what each judge said.
- Retrieval was otherwise thin: two corpus `query` calls on 2020s GVR and granted priors returned nothing Bivens-specific, and the CourtListener docket search index returned no SCOTUS docket hits by name.
- Reader should discount toward the anchor if they believe the elevated band's population is the right comparison regardless of how the second distribution arose; that would put the number closer to 0.12.
