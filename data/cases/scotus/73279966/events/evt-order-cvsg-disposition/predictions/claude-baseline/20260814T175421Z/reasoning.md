# Rationale — P(grant family) = 0.55

## The cell

CVSG-moment cert cell (`moment: cvsg`), forward mode, snapshot of 2026-08-14.
Frozen conditioning from `record/context.json`: band `high` under `sal-v2`,
`distribution_count` 1, CVSG dated 2026-05-18, Term 2025, paid docket
(No. 25-828, `sJsonCaseType: Paid`).

## Anchors (committed statpack)

- **Salience band**: the band is frozen at prediction, so the scored yardstick
  is the bracketed `reached` rate. Pooling the `high` band's reached rates over
  the Terms strictly before 2025 that the sal-v2 table renders (2017–2024)
  gives roughly 40% (≈427 grants over n=1,059); the 2025 row's own reached
  figure is 44.8% (n=87).
- **CVSG cut (paid scored segment)**: granted 30.1% + gvr 5.5% ≈ **35.6% grant
  family** among resolved CVSG'd petitions (n=163). This cut conditions on
  exactly my state — the CVSG is monotone and already on the docket, so the
  terminal-bucket caveat does not bite here.
- Background: CA9 modern-cert grant family ≈ 3.3%; the relist-count cut is not
  directly usable because a CVSG'd petition's distribution count is dominated
  by the CVSG pause, not by relist momentum.

## Adjustments from ~0.36–0.45 up to 0.55

Up:
- **The SG's likely recommendation.** The petition states (and the docket
  posture corroborates) that the last three administrations endorsed GEO's
  intergovernmental-immunity/preemption position, and the judgment forced
  suspension of the federal voluntary work program at a federal detention
  facility — a concrete, operational federal interest. I put roughly 0.6–0.7
  on an SG grant recommendation, and grant rates conditional on that are well
  above the pooled CVSG rate.
- **Petition strength and vehicle.** Paul Clement is counsel of record; the
  judgment below is final (~$37M after a jury trial, certified questions
  answered by the Washington Supreme Court, rehearing denied Aug 13, 2025);
  the petition claims support from three other circuits (CoreCivic v. Governor
  of N.J. (CA3 2025), GEO v. Newsom (CA9 2022, distinguishing), CA5/CAFC
  detainee-work cases) plus alignment with successive administrations.
- **Demonstrated attention.** The Court granted and decided GEO Group v.
  Menocal (Feb. 25, 2026, Kagan, J.) on the appealability of
  derivative-sovereign-immunity denials — the Court is already engaged with
  this litigation ecosystem — and the CVSG here is itself the Court's signal
  that the petition cleared the first cut.

Down:
- **The BIO's splitless argument has force.** Both BIOs argue the claimed
  conflict is over state *bans* on private detention facilities and TVPA
  forced-labor claims, not minimum-wage coverage of detainee work programs;
  a state-specific wage question after certified state-law proceedings is
  narrower than the petition's framing. If the SG sees it that way, a deny
  recommendation drops P(grant) sharply — 62% of CVSG'd paid petitions still
  end denied.
- The Washington Supreme Court's answer that the MWA covers detainees is a
  settled state-law premise, so the federal question is cleanly presented but
  the practical sweep arguments cut both ways.

Net: 0.55, above both statpack anchors on the strength of the likely SG
alignment and the vehicle, but well short of the ~0.8 I would hold conditional
on a favorable SG brief, because that brief is not yet on the docket.

## Claims

- `disposition` 0.55 — restates the top-level probability.
- `relist-increment` 0.97 — the docket shows one distribution; after the SG
  files the invited brief the petition is redistributed essentially
  mechanically, so the only paths to no further distribution are settlement,
  withdrawal, or dismissal before the SG files.
- `cvsg-increment` 0.02 — the CVSG is already on the docket; the claim is
  vacuous for this cell and the harness masks it. Stated per the contract.

## Uncertainty and discounts

- The largest uncertainty is the **SG's bottom line**, which does not exist
  yet; my number is a mixture over it. A reader who learns the SG's
  recommendation should move well off 0.55 in its direction.
- My read of the *Menocal* holding (appealability only, not merits) rests on
  the decision date and authorship confirmed via CourtListener plus background
  knowledge; the opinion text itself was mislinked on CourtListener (the
  linked document was an unrelated Pennsylvania case), so I could not verify
  the holding's text directly. It is a minor input — either way Menocal does
  not resolve this QP.
- Both provisioned document texts are marked `truncated` in `documents.json`
  (petition 250 pp., combined BIOs 133 pp.); I read the QP, the petition's
  table of contents/argument headings, and the BIOs' headings, so my weighing
  of petition against BIO is at the level of argument structure, not every
  record detail.
- The corpus `fedcourts query` pull surfaced mostly extension applications
  labeled `granted` rather than informative cert priors, so the quantitative
  anchoring is entirely from the committed statpack.
