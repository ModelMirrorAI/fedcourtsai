# Reasoning for my numbers

**P(any grant) = 0.47; label `denied`; granted = 0.**

## What I read
- Snapshot `2026-11-24.json`: paid petition by the United States (SG Sauer), CA2 judgment of Aug. 21, 2026, BIO filed Nov. 2 (Verrilli for the NY OAG), reply Nov. 16, distributed once for the Dec. 4, 2026 conference. No amici, no CVSG.
- `questions-presented.txt`, `petition.txt` (body; appendix truncated by the pipeline), `brief-in-opposition.txt`, `cert-reply.txt`, `decision-below.txt` (headings and the dissent's existence only; I did not read the opinion in full), `lower-court-docket.txt` (no en banc petition).
- `same-question.json`: one match, No. 26-304 (score 1.0, pending). That is United States v. Jackson (CA9), the petition the government asks this one to be held for. I checked its live docket on supremecourt.gov: BIO Nov. 2, reply Nov. 17, distributed for the same Dec. 4 conference. My forecast rests heavily on this link. It is not a `Vide` link on the docket; the parties' own briefs establish the relationship.

## Anchor and why I leave it
`context.json` gives band `federal`, `cert_anchor.rate` 0.731 (I reproduce it from the statpack's federal reached column, 2017–2025: 155/212), and the amicus-line `none` arm at 0.689. I depart well below that because of one case-specific fact the band cannot see: **the government itself asks only for a hold**, not plenary review, and calls its own case the worse vehicle (discharged grand jury, expired acting tenure, capable-of-repetition mootness). So the outcome here is almost entirely derivative of Jackson:

- P(Jackson granted) ≈ 0.82. SG petition; three circuits (CA3 Giraud, CA9 Jackson, CA2 here) have rejected a long-standing executive-branch practice; an acknowledged conflict with the Federal Circuit's Arthrex decision on the delegation question; Judge Park dissented below; about a dozen U.S. Attorney's Offices are said to be affected. Against: the regional circuits are unanimous on question 1, and Jackson has asserted vehicle/mootness objections I did not read first-hand (I did not open the Jackson filings).
- Given a Jackson grant: this petition granted and consolidated ≈ 0.15 (respondent's alternative ask; experienced counsel; the Court sometimes takes a second vehicle), held ≈ 0.85.
- Given a hold: P(GVR) ≈ 0.50, i.e. my estimate that the government wins on at least one question in Jackson. I have no strong view; SW General shows the Court reading the FVRA strictly against the executive, and three circuits agree, but the Court is receptive to executive-branch staffing arguments and the delegation question has real support.
- Given Jackson denied (0.18): this petition denied.

0.82 × (0.15 + 0.85 × 0.50) ≈ 0.47. P(denied) ≈ 0.53, P(GVR) ≈ 0.35, P(plenary grant) ≈ 0.12. The top-level label follows the modal outcome, but this is close to a coin flip and the label could easily be `gvr`.

## Other claims
- `relist-increment` 0.77: held petitions are redistributed after the lead decision; a consolidation path involves a relist; only a first-conference denial of both leaves one distribution. I am unsure how the harness counts a post-decision redistribution, but it is a further distribution entry.
- `cvsg-increment` 0.01: the United States is the petitioner.
- `summary-disposition-route` 0.74 = 0.35 / 0.47, conditional on a grant.
- `dissent-from-denial` 0.08: most denial mass is a quiet post-Jackson denial; writing is plausible only if both petitions are denied at the cert stage.
- `order-writers`: low single digits each, consistent with the above.

## Where to discount me
- The merits coin flip in Jackson drives nearly half the number and I have little basis for anything but 0.5.
- The event may not resolve until mid-2027; mootness events in between (a confirmed U.S. Attorney, a Munsingwear vacatur, a dismissal under Rule 46) could move it either way.
- The case concerns events after my training cutoff; I relied on the filings, not on memory. Citations in the briefs to 2026 decisions I could not independently verify, and none matters to the number.
- The statpack's band table heading reads sal-v8 while my context is sal-v9; the federal column pools to exactly the frozen anchor, so nothing turned on it (noted in `flags.json`).
- Corpus query was used only for a generic GVR sample; it did not move the number.
