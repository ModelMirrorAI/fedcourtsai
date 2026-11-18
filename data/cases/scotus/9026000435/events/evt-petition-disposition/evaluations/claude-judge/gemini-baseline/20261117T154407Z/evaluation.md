# Evaluation: gemini-baseline, scotus/9026000435, evt-petition-disposition

Cert-stage cell (moment: distribution). Outcome: petition **denied** on 2026-11-16 after a single distribution for the Nov 13 conference; no response requested, no CVSG, no noted dissent.

## Scores

- Predicted `denied` at probability 0.015; actual `denied` (`actual_granted` 0). `correct` = 1, `brier_score` = 0.000225.
- `vote_accuracy` omitted (cert stage). Segment base rate, skill and basis are the harness's to stamp; claim scores are computed in code.

## Reasoning quality: 0.55

The best-calibrated number of the three (1.5%), reached by adjusting *down* from the band anchor, which is the direction the record supported. The vehicle analysis is the right one: a non-precedential summary order, substantial-evidence review of workplace facts, a waiver with no amicus support, the Second Circuit's later published Siren Retail decision removing any standing circuit-level problem, and the observation that Hospital Menonita involved a pre-Loper Bright judgment while this order postdates Loper Bright by two years. The petition itself confirms the Siren Retail point.

Two things hold the grade down, and both concern the reliability of what the document asserts rather than its conclusion.

First, its base-rate figures do not match any pack I can find. `statpack-at` resolves this candidate to the same build as the others (7bcde3b105cb). In that build the relist-0 row is n=10,203 at about 1.8% grant family, the no-CVSG row n=13,556 at about 6.4%, the zero-amicus row n=11,109 at about 3.8%, the ca2 row n=2,070 at about 5.1%, and the baseline risk-set rows run 4.0% to 5.9% per Term with n of roughly 1,200 to 1,740. The rationale instead reports 0.5% (n=2,596), 3.9% (n=3,037), 1.0% (n=1,168), 3.5% (n=340), a pooled "120 / 3,084 = 3.89%", and OT2024/OT2025 rows of "[4.0%] (n=1,355)" and "[1.9%] (n=1,354)". None of those counts appears in the build in force or in the committed pack, and there was no alternative build. I graded against the build `statpack-at` named, and on that build the anchor section is wrong in every number it quotes. The error happens to push in the direction the outcome went, but an anchor stated with false precision is a defect regardless.

Second, it attributes to the panel, at "App. 10a n.2", a note that Nexstar never argued Oakwood Healthcare was unlawful under Loper Bright. I could not locate that footnote in the provisioned petition appendix; the appendix applies Oakwood without any such remark that I found. The claim is load-bearing for its "nothing turned on statutory interpretation" point, so I treat it as unsupported rather than false.

Sound judgment on the merits of the cert question, undercut by figures and a citation that do not check out.

## Predicted reasoning: 0.75

Central claims: denial on the order list immediately after the Nov 13 conference; zero further distributions; no CVSG; no separate writing; a conditional GVR route. All four unconditional claims were borne out, and this document committed to them most flatly of the three ("expect zero further distributions", "no CVSG will issue", "expect no dissent"). The path it called was still the base-rate-dominant one for a waived, amicus-free petition, which keeps it off the top of the scale; the conditional grant-branch content earns nothing either way.

## Leakage

Forward cell: prediction created 2026-10-30 from the 2026-10-30 snapshot (last entry the Oct 28 distribution); the petition was denied 2026-11-16. Scanned the captured log and prose for this case's disposition surfacing as decided: no retrieved_doc_date on or after 2026-11-16, no query for a disposing order, no read under data/qp-topics/, and the reasoning treats the conference as pending. The log's results are outcome_only throughout (coverage 0.0), so calls are graded on their queries: CourtListener searches for Hospital Menonita, Siren Retail and the Second Circuit Nexstar decision below, and a corpus query on this docket number (26-435) made while the case was open. None reaches for a disposition, and none existed. Graded `not_applicable`; `leakage_suspected` false.

## Big case: 0.15

A narrow, fact-bound labor dispute from an unpublished order, denied without comment. The Loper Bright question it invoked has broader reach than this vehicle did.
