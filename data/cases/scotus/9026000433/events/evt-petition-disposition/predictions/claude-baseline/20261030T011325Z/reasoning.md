# Rationale for P(grant) = 0.05

## Anchor
- `context.json`: forward cell, `band: baseline` under `sal-v4`, one
  distribution, no CVSG, Term 2026. The statpack's sal-v4 band table carries a
  `baseline` column, so I anchor on it directly. The caption-class fallback is
  not needed. (The petitioner is a private party, so the baseline floor would
  apply anyway.)
- I pooled the `baseline` **reached** rate over Terms 2017–2025, which are
  strictly before OT2026: about 660 grants on a weighted n of about 12,900,
  or **≈5.1%**. The OT2026 row (1.8%, n=169) contains this case and is
  immature, so I did not anchor on it.
- Cross-checks: the amicus-count bucket `1` is 10.3% grant-family plus 4.8%
  GVR (n=1162). It is read at disposition and is marginal, not conditional
  on the band. The relist-0 bucket is 1.3% plus 0.5% GVR, but it is the
  terminal state and too pessimistic for a petition that may still be called
  for a response. CA3 as originating circuit is about 1.5% granted.

## Adjustments
Up:
- The petition alleges a concrete 3–3 circuit split (CA7/CA10/CA11 against
  CA1/CA3/CA6) over the role of conscience-shocking conduct after
  *County of Sacramento v. Lewis*. I read this from the petition and QP. I did
  not independently verify the split's depth.
- The panel split 2-1, the facts are egregious, and the panel accepted that
  the conduct shocks the conscience.
- Counsel are experienced appellate advocates (Tutt / R. Stanton Jones), and a
  scholars' amicus brief was filed by Kellogg Hansen.

Down:
- **Vehicle.** The ruling below is a qualified-immunity affirmance on
  "clearly established" grounds, and the Third Circuit opinion is unpublished
  (2026 WL 1507402). Even if petitioner wins the QP, the officer may keep
  immunity, and the Court routinely declines to resolve a constitutional
  question that would not change the judgment.
- Respondents waived, so no opposition has framed the split yet. A grant
  would at minimum require a call for response first, which takes this past
  the first conference.
- The current Court is generally skeptical of expanding substantive due
  process (*Dobbs*, *Glucksberg* framing). A grant is more plausible to
  narrow the doctrine than to adopt petitioner's one-element rule, but this
  vehicle does not present it well for that purpose either.

Net: about the pooled anchor, so 0.05. The amicus signal is offset by the
QI and unpublished-opinion vehicle problems.

## Claims
- relist-increment 0.42: driven mostly by P(call for response) ≈ 0.40, which
  would produce a re-distribution, plus a small chance of a relist without
  one.
- cvsg-increment 0.01: no federal interest.
- summary-disposition-route 0.10 (conditional on grant).
- dissent-from-denial 0.05 (conditional on denial). The order-writers
  numbers are consistent with it (they sum to about 0.09 counting joint
  writers, and are concentrated on Sotomayor and Jackson).

## Inputs and caveats
- I read the snapshot `2026-10-30.json`, the QP, and the front matter and
  argument outline of the petition. I did not read the 116-page appendix
  (truncated) closely, so I relied on the petition's characterization of the
  panel majority and dissent. No BIO exists (waived).
- I did not use the CourtListener MCP or web search. The corpus queries
  returned no comparable SDP priors (the citation filter is sparse).
- I do not know this case's outcome.
