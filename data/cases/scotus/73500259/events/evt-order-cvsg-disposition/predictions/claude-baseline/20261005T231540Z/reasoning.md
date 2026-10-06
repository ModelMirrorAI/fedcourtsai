# Why 0.36

## Inputs read

- `record/snapshots/2026-10-05.json` (the provisioned baseline; the dated file
  `context.json` names). Eleven docket entries through the CVSG of
  October 5, 2026.
- `record/context.json`: mode `forward`, band `high` under `sal-v4`,
  `distribution_count` 2, `cvsg_date` 2026-10-05, Term 2025, cutoff 2026-10-06
  under a `date` cut.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (38 pp., full
  text), `brief-in-opposition.txt` (36 pp., full text). Neither document was
  `empty_text` or truncated. I read the petition's QP, introduction, and the
  three reasons-for-granting sections, and the BIO's introduction, statement,
  and all four reasons for denying, with particular attention to the vehicle
  section.
- `metrics/statpack.md`: the modern discretionary-cert base rate, the relist and
  CVSG cuts, and the `sal-v4` segment table.

## Anchor

The context's band is `high` under `sal-v4`, which matches the statpack's
segment table heading, so that table is the anchor. Pooling the `high` band's
bracketed `reached` figure over the rendered Term rows strictly before this
case's own Term (2017 through 2024; the 2025 row is this petition's own Term and
is excluded) gives 313.9 weighted grants over n = 898, a pooled reached rate of
about 35.0%. The CVSG cut on the paid scored segment says the same thing from a
different direction: petitions with a CVSG resolve granted 29.4%, GVR 5.5%,
dismissed 3.1%, denied 62.0%, so a grant-family rate of roughly 35%. The
two-distribution relist bucket (27.8% granted, 13.1% GVR) is less apt here,
because the first distribution was pre-empted by the Court's request for a
response and never saw a conference with a BIO on file. I start at 0.35.

## Adjustments up

- The Court asked for a response at the first distribution, after respondents
  had waived. That is an early, affirmative signal of interest from at least one
  chambers, and the CVSG after the long conference confirms the petition cleared
  the first screen.
- The split is real in result if not in framing. Motorola held that foreign
  affiliates' foreign component purchases at U.S.-approved prices did not satisfy
  § 6a(2); the Ninth Circuit let materially similar claims proceed and said so
  while criticizing Motorola's reasoning. The BIO's distinctions (direction of
  causation, Motorola's standing holding) are arguable but do not erase the
  tension.
- Experienced Supreme Court counsel on both sides, a published opinion, and a
  business-side amicus already on file. The question's practical reach for
  multinational procurement is large, and the petition says so credibly.

## Adjustments down

- Vehicle problems are substantial and the BIO documents them well: the case is
  interlocutory at summary judgment; the Ninth Circuit remanded the very causal
  question the petition says is dispositive; the domestic plaintiff's Illinois
  Brick control-exception claim, untouched by the FTAIA, is unresolved; the
  import-effects exception was never reached; and the panel repeatedly called
  the record "unique." The Court usually prefers a cleaner FTAIA vehicle, and
  it has passed on FTAIA petitions before (Motorola itself was denied).
- The SG's recommendation is the pivot after a CVSG, and I put the chance of a
  recommendation to grant at about 0.40. The Antitrust Division prosecuted NHK,
  relied on the availability of civil remedies in its plea, and its own
  guidelines read § 6a through domestic effects plus proximate cause, which
  favors the Ninth Circuit's result even if not all of its comity language. The
  Court follows the SG's cert recommendation most of the time, so a deny
  recommendation would pull this well below the band rate and a grant
  recommendation would push it well above.
- Petitioner is an admitted criminal price-fixer whose plea stipulated a direct,
  substantial, and reasonably foreseeable effect on U.S. commerce. That cuts
  against the "floodgates" framing and gives both the SG and the Court an easy
  reason to let the fact-bound judgment stand.

Net: the upward and downward adjustments roughly cancel, and I land one point
above the anchor at 0.36. `predicted_disposition` is `denied` because that is
the modal outcome; `granted` is 0 for the same reason.

## The other claims

- `relist-increment` 0.96: a CVSG petition is necessarily redistributed once
  the SG files; the residual is settlement or withdrawal before then.
- `cvsg-increment` 0.02: a CVSG is already on the docket, so the harness masks
  this claim; the number is nominal.
- `summary-disposition-route` 0.04 conditional on a grant: no intervening
  decision supports a GVR and the opinion below is not a candidate for summary
  reversal.
- `dissent-from-denial` 0.10 conditional on a denial: statements after a
  CVSG-and-deny sequence are uncommon, though an extraterritoriality-minded
  Justice could write briefly.

## Uncertainty and where to discount me

The single largest uncertainty is the SG's position, which I cannot observe and
which the forecast treats as a coin weighted slightly toward denial. I also could
not identify the Ninth Circuit panel or whether there was a separate writing
below; CourtListener's cluster carried no judge metadata, and neither filing
names the panel in the text I read, so I have treated the opinion as a unanimous
published panel decision. Retrieval was light (two corpus queries, four
CourtListener calls); the corpus queries returned recency-ranked priors without
a CVSG filter and did not materially inform the number, so the anchor rests on
the committed statpack rather than retrieved priors. No material about this
petition's own disposition surfaced; the cell is a genuine forward cell.

`big_case_score` 0.45: important to antitrust practitioners and multinational
businesses, modest general-public salience, interlocutory posture.
