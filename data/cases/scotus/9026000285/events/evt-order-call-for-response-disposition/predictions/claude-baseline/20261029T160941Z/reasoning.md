# Reasoning — P(grant family) = 0.10

**Inputs read:** the snapshot `2026-09-18.json` (six entries: the extension
application, the petition filed 31 Aug, the United States' waiver on 14 Sep, the
distribution for 10/9 on 16 Sep, and the response request on 17 Sep), `context.json`
(forward mode, band `baseline` under sal-v4, distribution_count 1, no CVSG, term
2026), `questions-presented.txt`, and `petition.txt` (89 pages, not truncated; I read
the introduction and the reasons for granting). No brief in opposition exists yet. The
live supremecourt.gov docket shows the response deadline extended to 18 Nov 2026 and
no disposition entered.

**Anchor:** the sal-v4 "Segment base rate by salience band" table, baseline column,
bracketed `reached` figure. I pooled OT2017–OT2025, which are the Terms strictly before
OT2026: about 660 weighted grants over n≈12,900, or about **5.1%**. The per-Term
figures run 4.0–5.9%. The OT2026 row (1.8%, n=169) is my own Term, so I excluded it.
The First Circuit's rate on the circuit cut (2.6% granted plus 0.6% GVR, all fee
classes) does not move the anchor.

**Adjustments up:**
- *The call for response.* The Court requested a response after the government waived.
  That means at least one chambers (often through a clerk's pool memo) saw something
  worth a second look. No committed table conditions on a called-for response. I treat
  the call as roughly doubling the paid-baseline rate. My reason is general knowledge
  that most CFR petitions are still denied, but they are granted several times more
  often than ordinary paid petitions. This is my judgement, not a committed figure.
- *A reserved question.* *McIntosh* (2024) n.5 expressly left open the Rule
  32.2(b)(4)(B) issue, and the government there called it "a harder set of issues."
  The petition cites a published Sixth Circuit decision (*Harrell*, 2026) recognizing a
  split, plus published Seventh Circuit (*Lee*), Fifth Circuit (*Brooks*), Ninth Circuit
  (*Montoya*) and Third Circuit authority.
- Experienced appellate counsel, and a large forfeiture ($13.2M).

**Adjustments down:**
- Several cited split authorities are unpublished (*Petix*, *Cereceres*, *Berry*,
  *Mincey*). Some of the claimed "five circuits" may be overstated.
- The question presented is fact-laden (five sub-parts), and the First Circuit found the
  errors harmless on its record. The government will press the harmless-error and
  vehicle points.
- It is a guilty-plea case, and the question is a rules question that the Advisory
  Committee could also address.

Net: about 0.10, which counts a possible GVR (for example, after the Court takes another
32.2(b)(4)(B) vehicle) inside the grant family.

**Claims:** relist-increment is 0.97 (redistribution after the response is near-certain,
and the harness masks this claim anyway). cvsg-increment is 0.005 (the United States is
the respondent). summary-disposition-route is 0.30, because conditional on any favourable
action a hold-and-GVR is a substantial share. dissent-from-denial is 0.04, because a
separate writing is rare on a federal criminal-procedure denial even after a CFR.
order-writers is consistent with that.

**Uncertainty:** the conditional effect of a CFR is the biggest unknown; a reader should
treat the doubling as soft. I have not verified the petition's characterization of
*Harrell* or the other circuits independently. Corpus queries returned general priors
only, with nothing on point.
