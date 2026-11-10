# Reasoning — City of North Las Vegas v. Jones, No. 25-1355 (relist moment)

**P(any grant) = 0.46; predicted label `denied` (just under even).**

## Record read
- Snapshot `2026-11-09.json`: petition filed Jun 2 2026; respondents waived; an amicus
  brief (City of Henderson, LVMPD, Clark County School District, Nevada Sheriffs' and
  Chiefs' Ass'n, IMLA et al.) filed Jul 6; distributed for 9/28; **Court requested a
  response Jul 21**; BIO Oct 5; reply Oct 19; distributed for the 11/6 conference;
  **Nov 9 redistributed for 11/13** — the first real relist, which opens this cell.
  `distribution_count` = 3, but the first (9/28) distribution was overtaken by the response
  request, so in substance this is one conference followed by one relist.
- Documents: QPs, petition, appendix, BIO, cert reply, decision below (CA9 No. 24-3374, published),
  lower-court docket record. The appendix (which I prefer over the CourtListener copy) shows the
  opinion was **amended Mar 6 2026 with rehearing en banc denied over a dissent by Judge Collins
  joined by Callahan, Bennett, R. Nelson, Lee, Bress, Bumatay and Tung** — eight judges — calling the
  case another in an "unending string" of CA9 decisions ignoring the Court's qualified-immunity precedent.
- Questions: (1) hot pursuit survives an 18-minute loss of the suspect's trail inside a perimeter;
  (2) qualified immunity because no clearly established law (panel relied on a single, factually
  distinct CA9 case); (3) clearly established law should mean only Supreme Court decisions.
  The petition (Pt. V) and reply ask in the alternative for summary reversal. The BIO argues no split,
  a fact-bound case, an alternative ground for the judgment, and that summary reversal is "strong medicine".

## Anchors
- `cert_anchor.rate` (band `elevated`, sal-v8, 10-Term lookback): **0.251**.
- Relist-count cut (paid scored segment), pooling buckets 1+: grant family (granted+gvr)
  ≈ 13.5% of 2,532 (bucket 1), 41.2% of 495 (bucket 2), 37.3% of 483 (3+) → ≈ 0.21 pooled.
  Both read low for a true post-conference relist, as the prompt notes (reschedules count as relists).
- Amicus cut: bucket 1 (n=1,159 resolved) grant family 14.9%.

## Adjustments (upward)
- This is the textbook profile for a per curiam summary reversal in a qualified-immunity case:
  CA9 denial of QI to officers, a published opinion resting on one circuit case at a high level of
  generality, a large en banc dissent invoking the Court's own QI summary reversals, government-side
  amici, a called-for response, and now a relist after the first conference at which the case was
  actually considered. The Court relists before nearly every grant and summary disposition, and the
  response request shows at least one Justice's interest.
- So I move well above the 0.25 anchor, to just under even.

## Adjustments (downward) / uncertainty
- The Court has issued fewer QI summary reversals in recent Terms than in the 2015–2021 period, and
  hot pursuit after an 18-minute gap within a perimeter is fact-bound; the backyard entry is a
  core curtilage intrusion, which may make some Justices reluctant to reverse summarily.
- A single relist often ends in denial, sometimes with a separate writing; Relist Watch–style
  experience is that one relist is a much weaker signal than two or three.
- QP 3 is a non-starter; plenary grant is unlikely — most of my grant mass is a summary reversal.
- Petitioners' counsel is not regular Supreme Court bar, which matters less for summary disposition.
- Main uncertainty: whether the relist is a summary-reversal draft (→ grant family) or a
  dissent/statement being written on a denial. I hold these at roughly 46/54.

## Inputs and degradation
No MCP or web retrieval used; one corpus query (generic, not very informative). Forecast rests on the
provisioned record and the committed statpack.
