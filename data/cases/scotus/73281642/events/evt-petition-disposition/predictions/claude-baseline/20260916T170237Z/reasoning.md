# Rationale for the numbers

## Inputs read

Snapshot `record/snapshots/2026-09-15.json` (the file `context.json` names),
`record/context.json` (mode `forward`, band `baseline` under `sal-v4`,
distribution_count 1, no CVSG, Term 2025), `event.yaml` (petition kind, no
stage recorded, so a cert cell at the distribution moment), and all three
provisioned documents: `questions-presented.txt`, `petition.txt` (43 pages,
full text), and `brief-in-opposition.txt` (51 pages, full text). None was
flagged `empty_text` or truncated. Beyond those I read the Seventh Circuit
opinion (Kolar, J., joined by Rovner and Scudder, published, 154 F.4th 549)
through the CourtListener MCP server; see `retrieval.md`.

## Anchor

The cell is cert stage with a frozen band, so the anchor is the salience band
table's bracketed `reached` rate for `baseline`, pooled over the Terms the
table renders strictly before OT2025 (OT2017 through OT2024). Weighting each
Term's rate by its `n` gives 5.1% over about 11,600 weighted petitions. The
Seventh Circuit cut (grant 1.1%, GVR 1.4% among resolved CA7 petitions) and the
relist-0 cut (1.2% granted) sit lower but describe terminal states, not the
position of a petition at its first conference. The modern-cert headline rate
is a few percent. So the starting point is roughly 0.05.

## Adjustments up

- **Cert-stage amicus support.** Five briefs (Pacific Legal Foundation, Small
  Property Owners of San Francisco Institute and Owners Counsel of America, the
  Lech family through the Jenner & Block clinic, a police chief, and property
  law professors Ely, Mahoney, and Saxer). Most paid petitions draw none; five
  puts this in a small, high-grant tail.
- **An acknowledged, outcome-relevant split on QP1.** The Fifth and Sixth
  Circuits have expressly rejected the police-power exception the Seventh
  Circuit applied; the Seventh Circuit's opinion itself catalogs the disagreement
  and concedes "difficult questions." Unlike Baker, where the Fifth Circuit
  rejected the exception and the petitioner lost anyway, here the exception was
  the sole ground of decision, so it is arguably dispositive.
- **Two Justices on record.** The Baker statement (Sotomayor, joined by
  Gorsuch) called the question important and asked for percolation. Since then
  the Ninth (Pena), Eleventh (Alford), and Seventh (this case) Circuits have
  weighed in, which removes the stated reason to wait.
- **Vehicle quality.** Published opinion, en banc denied, Rule 12(b)(6) posture
  with facts taken as pleaded, a $16,000 concrete injury, repeat Supreme Court
  counsel, and a companion petition from another circuit filed the same week
  so the Court can choose or pair vehicles.

## Adjustments down

- **Outcome convergence.** The BIO's strongest point: every circuit, under
  whatever label, has denied compensation for reasonable damage during a
  lawful search, and petitioner conceded the search's lawfulness. The Court
  can read the split as one of reasoning rather than result, and that reading
  is exactly what produced denials in Lech (2020), Baker (2024), and Slaybaugh
  (2025) on materially the same question from the same counsel.
- **Revealed reluctance.** Three denials in six years, one after a statement
  by two Justices, and Slaybaugh denied without a noted writing. Four votes
  have not been there before; the marginal votes would have to come from
  Justices who are pro-property but cautious about new liability for police.
- **Rule-shape problems on QP2.** The Seventh Circuit's administrability
  concerns about "innocent" owners, and petitioner's own carve-outs recited in
  the BIO, make QP2 unattractive; that caps the upside but does not much affect
  QP1.
- **Cedar Point language.** The Court's own dictum that lawful searches do not
  take a property right gives the current majority a ready reason to think the
  Seventh Circuit reached the right result.

Net: roughly a fourfold lift from the anchor, to P(grant) = 0.22. I hold this
with moderate confidence (0.6); the honest range is 0.12 to 0.35.

## Claim-by-claim

- **disposition 0.22** restates the top-line number.
- **relist-increment 0.55.** From one distribution. The statpack's relist cut
  shows most petitions never relist, but Baker was carried over more than
  once before its denial-with-statement, and five amici plus a companion
  petition make a second look likely. I would not go higher because the Court
  also clears many well-supported petitions at the long conference.
- **cvsg-increment 0.07.** No federal party; no CVSG in Baker or Slaybaugh.
  Slightly above the population rate because law-enforcement takings liability
  does touch the United States through the Federal Circuit line.
- **summary-disposition-route 0.2** (conditional on a grant). Below the
  population share of GVRs among grants because no intervening decision exists.
  The residual mass is the hold-and-GVR path if Pena is granted alone and
  decided for the property owner.
- **dissent-from-denial 0.5** (conditional on denial). Two Justices already
  wrote once; percolation is done; but Slaybaugh drew nothing.

## Big case score

0.55. If decided, the case would settle a seven-circuit conflict on a
constitutional question that recurs with every SWAT deployment and has a
sympathetic, widely reported fact pattern. It is not a term-defining case.

## Where to discount me

- The pooled anchor spans Terms with uneven `gvr` labeling (OT2023 and OT2024
  carry zero GVRs by ingestion history), but the `reached` figures are grant
  family rates, so this should not bias the anchor.
- I could not locate the companion Pena petition (No. 25-1163) on
  CourtListener, so its docket state (distribution date, amici, whether it is
  paired for the same conference) is inferred only from the petition's
  footnote and an amicus filename in this docket; if Pena is not before the
  Court at the same conference, the hold-and-GVR share of the summary claim
  drops and the plenary share rises.
- The corpus `--citation` lookup for the Baker denial returned nothing (the
  citation column is sparse), so my knowledge of Baker's and Slaybaugh's
  relist histories is from general knowledge, not a corpus row.
- I carry no knowledge of this petition's outcome; the conference is
  September 28, 2026, after this run. The CourtListener docket record for this
  case showed no entries newer than the snapshot.
