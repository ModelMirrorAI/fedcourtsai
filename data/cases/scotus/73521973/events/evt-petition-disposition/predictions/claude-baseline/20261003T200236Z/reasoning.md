# Rationale for the numbers

**P(grant) = 0.08; predicted disposition: denied.**

## Anchor

`record/context.json` freezes `band: baseline` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table, so the table is a valid anchor. Per the prompt I pooled the bracketed `reached` figure for `baseline` over the Terms strictly before this case's Term (OT2025), i.e. OT2017 through OT2024 (OT2026 renders empty):

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled, weighted by n: **5.1%** (n = 11,580). That is the grant-family rate for a paid petition that reached the baseline band, and is the yardstick my skill is scored against.

Other cuts I read for shape, not as the answer: relist bucket 0 (granted 1.2%, GVR 0.5%) is a terminal-count figure and understates a petition still at its first conference; CA11 origin (granted 1.7%, GVR 1.9%) is close to the overall modern rate; the capital-case marking cut (capital: granted 11.8%, GVR 5.6% versus unmarked 4.2% / 2.3%) is the most favorable cut, but it is a marginal split that pools State petitions (where the Court frequently grants to reverse habeas relief) with prisoner petitions, so I treat it as an upper bound rather than this posture's rate.

## Adjustments up from 5.1%

- **Capital case with a published, divided panel opinion** (120 F.4th 768, confirmed Published on CourtListener), a panel dissent by Judge Rosenbaum, and **two dissents from denial of rehearing en banc** (Rosenbaum and Abudu) answered by a Branch concurrence joined by Grant. Published dissents at both stages are the strongest conventional signal in the record.
- **Serious counsel**: Christopher Kise as counsel of record with Foley & Lardner and Bradley Arant; the petition is professionally framed around a 6-3 circuit split.
- **A genuinely striking record fact**: the ACCA's first opinion called the omitted mitigation "powerful" and said it would have been "compelled to grant relief" but for a procedural bar the Alabama Supreme Court then rejected, after which the ACCA reversed itself as "dicta." Combined with the 7-5 jury note and 11-1 verdict, this is the kind of fact pattern that draws a written dissent from denial.
- The Rompilla parallel on the unexamined prior-conviction file is close on its facts.

## Adjustments down

- **Vehicle problems on QP 1 are real and documented in the record itself.** The Branch concurrence (quoted in the BIO at Pet. App. 171-72) states that Davis never argued the state court's failure to consider juror hesitation; it surfaced first in the panel dissent. The BIO adds that it was not in the en banc petition, the district court briefing, or any state-court filing (unexhausted). The panel majority's footnote 25 also holds in the alternative that the hesitation would carry little weight given a one-hour deliberation. The Court rarely takes a question first raised by a dissenting judge, and an alternative holding makes QP 1 potentially non-dispositive.
- **The split is contestable.** The BIO shows that six of the petitioner's eleven pro-split authorities are pre-AEDPA or de novo, and the remaining ones turn on facts (e.g., Williams v. Stirling involved a two-day deadlock and an Allen charge). A "jury hesitation must be considered" rule framed as clearly established law under §2254(d)(1) is a hard sell to this Court, which has repeatedly reversed circuits for sharpening Strickland into specific rules (Marshall v. Rodgers, Woodall, Kayer; and the 2026 decisions the BIO cites, McCarthy v. Hernandez and Klein v. Martin, show the deference line is active this Term).
- **Posture.** Prisoner-side AEDPA Strickland grants are rare; the Court's recent capital Strickland interventions (Thornell v. Jones, Shinn v. Kayer, Mays v. Hines, Dunn v. Reeves) went the State's way. Under 1993 Alabama law the judge, not the jury, was the sentencer, which blunts the jury-primacy framing (the BIO points out Judge Abudu's dissent assumed otherwise).
- **QP 2 is fact-bound** error correction with no asserted split.
- **No amicus support** on a capital petition with sophisticated counsel and a claimed six-circuit split is a mild negative.
- The crime facts as the State tells them (bragging about the shooting) make summary intervention for the petitioner less attractive.

Net: the up-adjustments (dissents, capital, counsel, record facts) roughly offset against the down-adjustments (not raised below, alternative holding, AEDPA posture). I land at **0.08**, somewhat above the 5.1% anchor, mostly on the strength of the published dissents and the capital marking.

## Claims

- `disposition` 0.08 — equals the top-level probability.
- `relist-increment` 0.35 — from one distribution. Roughly a quarter of paid scored petitions see at least one further distribution (the relist cut's buckets 1, 2 and 3+ against the whole), and I raise that because a capital case with a plausible dissent from denial is the archetypal relist-for-writing petition.
- `cvsg-increment` 0.02 — no federal interest.
- `summary-disposition-route` 0.30, conditional on grant — no intervening decision to GVR against; plenary on the QP 1 split is the likelier grant shape, with an Andrus-style summary vacatur as the residual.
- `dissent-from-denial` 0.30, conditional on denial — the record facts invite a Sotomayor dissent, but most capital Strickland denials still pass silently.

## Inputs used and their condition

- Snapshot `record/snapshots/2026-10-03.json` (paid docket, capital flag set, one distribution for 10/9/2026, reply filed, no amici, linked only to the extension application 25A1168).
- `questions-presented.txt`, `petition.txt` (713 pages, `truncated: true`; the body through the Conclusion was intact and the truncation falls in the appendix, so nothing I relied on was cut), and `brief-in-opposition.txt` (40 pages, complete). The reply brief is on the docket but was not provisioned and I did not retrieve it.
- `metrics/statpack.md` as above.
- CourtListener MCP: confirmed the Eleventh Circuit opinion's Published status and citation, and the two rehearing-denial opinions dated 2026-02-19. A search for a Supreme Court docket in White v. Plappert (the Sixth Circuit case the petition cites as part of the split) returned nothing, so I do not know whether a related petition is pending; had one been granted or held, I would have moved up.
- `fedcourts query` returned mostly recent application dockets (26A-series) rather than comparable cert petitions and did not change the number; transfer lines are in `retrieval.md`.

## Where to discount me

I have no visibility into the Justices' internal views on the juror-hesitation question, and the 0.08 depends heavily on my judgment that the "not raised below" problem dominates the published dissents. If the Court treats the ACCA's about-face as the kind of injustice it occasionally corrects summarily in capital cases, I am too low. If it treats this as a routine AEDPA denial, the anchor's 5% is closer than my 8%. Forward mode: this petition is undecided (conference is October 9, 2026); I encountered no outcome material.
