# Rationale — P(grant family) = 0.78

## Anchor

This is an arrival-moment cert cell with a frozen `band: federal` under
`sal-v3`, which matches the committed statpack's segment table version, so the
published anchor for the class applies. Pooling the federal band's bracketed
`reached` rates over the Term rows strictly before this case's own (2017–2025;
the 2026 row is empty), the pooled grant-family rate is **≈ 71.2%**
(143.0/201 weighted resolved). The federal band's leading and bracketed figures
coincide (strongest band), and the band-cut section's disposition mix
(granted 48.8%, gvr 22.4%) confirms the segment rate counts the whole grant
family — the same binary axis my `probability` is scored on.

## Adjustments

**Up from 71% because this petition is stronger than the average federal-band
petition.** The decision below (*Barbosa da Cunha v. Freden*, 175 F.4th 61 (2d
Cir. Apr. 28, 2026)) sits on an explicit, mature circuit split — CA5
(*Buenrostro-Mendez*, 166 F.4th 494) and CA8 (*Avila*, 170 F.4th 1128) for the
government's reading of § 1225(b)(2)(A); CA2, CA6, CA11, CA10, CA7, CA9, and
CA1 against it, several over dissents — on a question controlling a nationwide
detention policy. The Solicitor General has already filed a parallel petition
from the Sixth Circuit (*Raycraft v. Lopez-Campos*, No. 25-1415, filed June
2026, still pending per a docket-metadata check). Seven circuits invalidating a
flagship federal policy on a percolated split is a near-certain grant *of the
issue*.

**Down because the event resolves on this docket, not the issue.** The
companion 25-1415 was filed a month earlier and is an equally plausible lead
vehicle. My decomposition: P(this petition granted outright or consolidated)
≈ 0.60; P(held while another vehicle is granted) ≈ 0.35, which then splits into
GVR if the government wins the merits (≈ 0.45 conditional → ≈ 0.16
unconditional, still grant family) or denial if it loses (≈ 0.19); P(no grant
anywhere) ≈ 0.03; P(dismissal/mootness — the individual habeas petitioner is
released or removed) ≈ 0.02. Grant family ≈ 0.60 + 0.16 ≈ **0.76–0.78**. I
commit to **0.78**, modestly above the pooled anchor.

## Claim rationale

- `disposition` 0.78 — restates the top-level probability, as required.
- `relist-increment` 0.97 — the count frozen in my context is **0**
  distributions; any first distribution resolves this true. A paid SG petition
  with a BIO due August 24 will be distributed for an early-OT2026 conference
  unless dismissed or withdrawn first, which is the only realistic miss.
- `cvsg-increment` 0.01 — the United States is the petitioner; a CVSG is
  effectively impossible.
- `summary-disposition-route` 0.20 — conditional on a grant: the plausible
  cert-order disposition is a GVR after the companion vehicle is decided for
  the government (≈ 0.16 of the ≈ 0.76 grant mass); a summary reversal on a
  contested split is implausible.
- `dissent-from-denial` 0.10 — the dominant denial scenario is housekeeping
  after the split is resolved against the government elsewhere, which draws no
  writing; only the tiny outright-denial branch would.

## Uncertainties and discounts

- **Vehicle selection is the main uncertainty.** I cannot observe how the SG
  ranks the vehicles or whether the Court will consolidate; the 0.60/0.35
  split between "granted/consolidated" and "held" is judgment, not a published
  cut.
- **Merits odds drive the held branch.** My ≈ 0.45 P(government wins merits |
  granted elsewhere) is soft; a more government-favorable read pushes the GVR
  share (and the grant family) up, a less favorable one pushes denial up.
- **No provisioned document text.** `record/documents/` was not provisioned
  for this cell — no `questions-presented.txt` or petition text — so my
  characterization of the QP comes from the snapshot caption and from the
  sister-circuit opinions' descriptions of the Second Circuit's holding and the
  SG's filings, retrieved via the CourtListener MCP server, not from the
  petition itself.
- **Timing note.** The event records `opened_at` 2026-07-23 (the docketing
  date); sister-circuit opinions describe the petition as filed July 24, 2026.
  Immaterial to the forecast.
- Forward cell: retrieval was unrestricted; I did not seek this petition's own
  disposition, and the companion-docket check showed 25-1415 pending
  (`date_terminated: null`), so no outcome-revealing material surfaced.
