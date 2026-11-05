# Reasoning — Mitchell v. Mississippi, No. 26-526 (P(grant) = 0.025)

**Inputs read.** Snapshot `record/snapshots/2026-11-05.json`; `record/context.json`
(forward mode, band `baseline` under `sal-v6`, `distribution_count` 1, no CVSG,
`cert_anchor.rate` 0.0519); `record/documents/questions-presented.txt` and
`petition.txt` (93 pp., not truncated, not OCR); `record/same-question.json`
(empty list — no other pending petition scored above the 0.5 threshold). No BIO:
Mississippi waived its right to respond (Oct 21, 2026), and the petition was
distributed Oct 28 for the Nov 13, 2026 conference. No amicus briefs on the docket.

**Anchor.** The frozen cert anchor for the `baseline` band is 5.2% (risk-set
`reached` rate pooled over prior Terms). That figure already includes petitions
that later relist or draw a CVSG; a petition that sits at its first conference
with a waiver and no call for response is in the low end of that population (the
relist-0 bucket resolves ~1.8% grant-family, though it understates for a petition
not yet at conference).

**Adjustments down.**
- *Waiver, no amici.* The State did not think the petition worth answering, and no
  outside group has filed. A grant without first calling for a response is very rare,
  so a grant requires at minimum a call for response at or after Nov 13.
- *Weak split.* The cited "conflict" is a set of state cases applying the same
  Martin Linen / Scott / Evans framework to different facts (statute of limitations in
  Kruelski, jurisdiction-as-element in Karpov, etc.). That is application, not a
  doctrinal split over the governing test.
- *Merits look Scott-side.* By the petition's own account the trial judge terminated
  the case because the complaining witness's absence violated compulsory process —
  a ground unrelated to factual guilt, which Scott and Evans (568 U.S. at 319) treat as
  a procedural dismissal permitting retrial. The petition's reliance on Oregon v.
  Kennedy (a mistrial-provocation rule) is a poor fit. Error correction is unlikely.
- *Interlocutory posture.* Retrial is set for March 2027; though § 1257 finality for
  double-jeopardy claims is established (Abney-type reasoning applies to state cases),
  the Court often prefers to wait.
- *Counsel* are local practitioners, not repeat Supreme Court advocates.

**Adjustments up.** A 4-judge en banc dissent in the Mississippi Court of Appeals,
four votes for rehearing, and the Mississippi Supreme Court granting and then
dismissing its own writ suggest the question is genuinely contestable; acquittal
classification is a recurring area the Court revisited in Evans and McElrath.
Double-jeopardy acquittal cases occasionally draw a call for response.

Net: ~2.5%, about half the band anchor.

**Increments.** One distribution on the docket (Nov 13 conference). Relist-increment
0.12 — mainly the chance (~10%) that a Justice calls for a response, which forces
redistribution, plus a small chance of a straight relist/reschedule. CVSG 0.003: a
state criminal case with no federal interest. Summary route given grant 0.25: a
grant here could take the form of a summary reversal à la Fong Foo/Smith if the Court
thought the acquittal plain, though plenary review (as in Evans, McElrath) is likelier.
Dissent from denial 0.03 — little sign any Justice would write; Gorsuch and Sotomayor
are the likeliest if anyone does.

**Uncertainties / discount.** I have not read the Court of Appeals opinion
(appendix is in the petition PDF but I relied on the petition's characterization);
if the trial court's order made explicit evidentiary-insufficiency findings, the
Evans argument strengthens. Corpus queries returned nothing case-specific; the
estimate rests on the statpack and the petition text. Retrieval budget was not an
issue; no MCP calls were made.
