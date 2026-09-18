# Rationale for the numbers

**P(grant) = 0.30; predicted disposition: denied.**

## Anchors

- **Salience band.** `record/context.json` freezes `band: high` under `sal-v4`, `distribution_count: 3`, `cvsg_date: 2026-04-06`, `term: 2025`, mode `forward`. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's salience version. Pooling the `high` band's bracketed `reached` figures over the eight Terms strictly before OT2025 that the table renders (OT2017–OT2024, n = 127, 99, 98, 111, 140, 105, 102, 116, total 898), the pooled grant rate is about **35%** (314 weighted grants / 898). That is the yardstick the evaluator scores this cell against.
- **CVSG cut** (paid scored segment): `cvsg` bucket resolves granted 29.4%, gvr 5.5%, dismissed 3.1%, denied 62.0% — a grant family of about 35%, consistent with the band anchor.
- **Relist cut**: the stored count of 3 distributions puts the petition in the `2` relist bucket (granted 27.8%, gvr 13.1%), though here one "relist" is the CVSG gap rather than a true reconsideration, so I read this cut as shape, not as a second anchor.
- Modern discretionary-cert petitions grant at a few percent overall; this petition is far above that population by construction (response requested, CVSG, high band), so the whole-docket rate is not the anchor.

## The decisive adjustment: the Solicitor General's recommendation

The snapshot records that the United States filed its amicus brief on August 31, 2026 but not what it said. In forward mode I retrieved the brief from supremecourt.gov (it predates my snapshot and sits on this docket, so it is legitimate forward signal). The government **recommends denial**. Its reasoning:

1. It agrees with petitioners that the Sixth Circuit erred: surcharge against a fiduciary for breach of fiduciary duty is "appropriate equitable relief" under *Amara*, and the Sixth Circuit overread *Montanile*'s footnote.
2. It agrees a genuine circuit conflict exists on surcharge against ERISA fiduciaries, and says the Court "may want to revisit" the question "in a future case."
3. But this case is a "poor vehicle": top-hat plans are exempt from ERISA's fiduciary rules; whether Regions is a fiduciary in *Amara*'s sense is disputed and unaddressed below; no court of appeals has allowed surcharge against a rabbi-trust administrator; and the Fifth Circuit has vacated its *Aramark* panel decision for en banc rehearing.
4. Question 2 (preemption) is correctly decided and presents no conflict.

The CVSG-conditional anchor (~35%) blends grant and deny recommendations. The Court follows the Solicitor General's CVSG recommendation in the large majority of cases, and conditional on a *deny* recommendation the grant rate is well under the pooled CVSG figure. I take roughly 20–25% as the starting point for a deny recommendation, then adjust:

**Up**, because this is the weakest kind of deny recommendation — a vehicle-only denial that concedes error and concedes the split. The Justices can judge vehicle quality for themselves, and the Court already knew the top-hat/fiduciary problem from the BIO when it called for the government's views, which means at least several Justices were interested despite it. Petitioners' supplemental brief (September 16, 2026) has a strong answer: the Sixth Circuit's rule is categorical and is already being applied by district courts in the circuit to ordinary health and 401(k) plans; *Harris Trust* and *Mertens* both decided the § 1132(a)(3) remedial question while reserving the defendant's status; and Regions actually *is* a trustee, which is the analogy *Amara* draws. The petition is from the UVA Supreme Court Litigation Clinic with a Bray amicus, and the Court has shown repeated interest in the question (grant in *LaRue*, extended discussion in *Amara*).

**Down**, because the vehicle problem is real and now has a concrete alternative attached: the en banc Fifth Circuit in *Aramark* will produce a decision in a case where the defendant concededly is a fiduciary, and the Court can wait for it. The Court denied *Rose v. PSA Airlines* in 2024 on the same question. Respondent's BIO (Gregory Garre) presses an independent liability problem the Sixth Circuit itself flagged (it is "far from clear" any plan term was violated). And the historical pattern when the government says "important question, wrong case" is usually denial, sometimes with a statement.

Net: **0.30**. I am above the deny-recommendation conditional rate and below the unconditioned CVSG/band anchors, which is where a vehicle-only denial recommendation on a question the Court plainly wants to reach belongs.

## The other claims

- **relist-increment 0.45.** Increment from three distributions. CVSG'd petitions are often decided at the first post-SG conference, but a statement respecting denial (which I put at 0.30 conditional on denial) or serious consideration of a grant would each add a relist. Roughly even odds.
- **cvsg-increment 0.01.** A CVSG is already on the docket; the harness will resolve this claim as vacuous for my cell.
- **summary-disposition-route 0.04** (conditional on grant). No intervening decision to GVR in light of; a summary reversal of a reasoned published opinion on an open question is not plausible.
- **dissent-from-denial 0.30** (conditional on denial). The government conceded error and the split; a statement noting the question's importance and awaiting a cleaner vehicle is a familiar move in exactly this posture, but most CVSG denials still issue silently.

## Documents read

Provisioned: `record/snapshots/2026-09-17.json`; `record/documents/questions-presented.txt`; `record/documents/petition.txt` (truncated, 118 pp.; I read the QP, statement, and split argument); `record/documents/brief-in-opposition.txt` (full). `documents.json` shows no `empty_text` documents. Retrieved (forward mode): the docket page for 25-590 at supremecourt.gov (matches the snapshot entry-for-entry; no disposition recorded), the United States' amicus brief and petitioners' supplemental brief (both PDFs, text extracted locally), the SCOTUSblog case page (no disposition, no SG summary), and Samuel Bray's January 2026 blog post on his amicus brief.

## Where to discount me

- The conditional grant rate after an SG deny recommendation is from my general knowledge of the empirical literature, not from a statpack cut; the pack does not condition the CVSG bucket on the recommendation's direction.
- I have not read the Sixth Circuit opinion itself beyond the parties' and the government's characterizations of it.
- The en banc *Aramark* timing is unknown to me; if the Court expects it imminently, denial (or a hold-like series of relists) becomes more likely than I have priced.
- The band anchor pools OT2017–OT2024 `high` rows as the table renders them; the salience version matches the context, so no fallback to a caption-class floor was needed.

## Corpus tooling

One `fedcourts query` (see `retrieval.md`) returned recent granted SCOTUS priors; none was a CVSG'd cert petition on an ERISA remedies question, so it informed nothing beyond confirming the corpus service was reachable. The statpack supplied all base rates used.
