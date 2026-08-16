# Rationale for the numbers

**P(grant family) = 0.003, predicted disposition `denied`.**

**Anchor.** This is an arrival-moment cert cell (`moment: arrival`): forecast at
docketing, zero distributions, no docket-acquired signal by construction. The
frozen context carries `band: baseline` under `sal-v3`, which matches the
statpack's band table version, and baseline is the weakest band — so the two
anchoring rules the prompt gives (the frozen band's bracketed `reached` rate,
and the arrival population's whole-paid-segment rate) coincide here. Pooling
the baseline band's bracketed `reached` figures over the nine Term rows
strictly before this case's OT2026 (OT2017–OT2025, the full rendered window)
gives **6.55% (n≈13,163)** — the paid scored segment's unconditional grant rate,
and the yardstick this cell is scored against. The petitioner is pro se, not
federal, so the far-higher `federal` arrival-class segment is irrelevant.

**Adjustments down, and why they are large.** Nearly everything observable
about this petition sits in the weak tail of that 6.55% population:

- **Pro se, 9-page petition.** The petition (provisioned text, read in full)
  cites three cases (Murchison, Caperton, Williams) plus Tumey, and never
  states *what facts* allegedly created the intolerable risk of bias — the
  central premise of its own QP is asserted, not shown. There is nothing for a
  clerk to build a grant memo from.
- **No conflict.** The "important, recurring, national" section asserts that
  state procedures "vary widely" without citing a single conflicting decision.
  No circuit or state-high-court split is developed.
- **Vehicle and jurisdictional defects.** The posture is a summarily denied
  writ of mandate in a *pending* state civil enforcement action; § 1257
  finality is doubtful (the petition's one-sentence finality argument — that
  the California Supreme Court's denial of review "renders the judgment
  final" — does not engage the ongoing proceedings below). The named
  respondents are the Superior Court and the assigned judge, and the state
  courts below wrote no opinions, so there is no reasoned decision to review.
- **Docket texture.** The linked stay application (26A145) was denied by
  Justice Kagan on August 3, 2026 and refiled to the Chief Justice — a pattern
  overwhelmingly associated with petitions that are denied without comment. I
  treat the single-Justice stay denial as a weak negative signal on the
  underlying petition (it predates my snapshot and is on this docket; it is
  not leakage — the petition's disposition remains open).

Paid pro se petitions with no developed split and a defective posture grant at
a rate well under 1%; conditioning on all of the above I put the grant family
(any grant, GVR included) at **0.3%** — a ~20× reduction from the segment
anchor, which the specifics comfortably support. I stop short of a smaller
number only because the grant family includes GVR, and an unforeseen
intervening decision on judicial-disqualification procedure is the one
residual route.

**Claims.**
- `disposition` 0.003 — restates the top-level probability.
- `relist-increment` 0.96 — the frozen state is 0 distributions; virtually
  every docketed paid petition not dismissed or withdrawn pre-conference is
  distributed at least once, and the response date (Aug 20, 2026) puts a first
  conference in early OT2026. The 4% residual covers pre-conference dismissal
  or withdrawal. (The statpack's relist-0 terminal share is not this claim's
  complement — it buckets petitions by *terminal* relist count after at least
  one distribution.)
- `cvsg-increment` 0.002 — no federal interest exists; CVSGs run ~1.3% even
  across the whole paid scored segment and concentrate in cases with a federal
  statutory or governmental dimension this case lacks entirely.
- `summary-disposition-route` 0.7 — conditional on any grant. A plenary grant
  of this petition is close to inconceivable; if the family fires it is most
  plausibly a GVR in light of an intervening decision. Statpack-wide the GVR
  share of the grant family runs near half, and this case's specifics push the
  conditional share of cert-order disposition higher.
- `dissent-from-denial` 0.008 — noted dissents/statements attach to a small
  share of denials and concentrate in developed, counseled petitions on live
  doctrinal disputes; nothing here invites a writing.

**Uncertainty and discounts.** The main uncertainty is that an arrival-moment
forecast sees no trajectory at all — a response, if one is filed, and any
distribution behavior could move the picture, and none of that exists yet. My
read of the merits weakness rests on the petition's own text (provisioned,
complete, 9 pages, `empty_text: false`); there is no BIO to weigh, which for a
petition this weak I read as neutral-to-negative (a waiver is likely, and
waived petitions grant rarely). Retrieval was minimal by choice: the
`fedcourts query` surface matches structured filters only (court / topic /
judge / citation), none of which discriminates for a state-court
recusal-procedure petition, so I anchored on the committed statpack instead;
no CourtListener MCP lookups were needed because the provisioned record and
petition text already carry the load-bearing facts. A reader should discount
my 0.7 summary-route conditional most — it is a judgment about a
counterfactual grant with no published baseline.
