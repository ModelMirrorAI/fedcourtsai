# Rationale — P(any grant) = 0.42

## Anchors

- **Salience band (the scored yardstick).** `record/context.json` freezes
  `band: high` under `sal-v3`, matching the statpack band table's version. As a
  band frozen at prediction, the scored baseline is the bracketed **`reached`**
  rate. Pooling the high band's reached figures over the rendered Terms strictly
  before this case's own (2017–2024, n=1074 weighted resolved) gives **≈40.9%**.
- **CVSG cut.** The statpack's "Cert petitions by CVSG status (paid scored
  segment)": granted 29.4% + gvr 5.5% = **≈34.9% grant family** (n=163
  resolved), against ~6% for non-CVSG petitions. This is a terminal-status cut,
  but this cell's moment *is* the CVSG, so the conditioning matches.
- **Relist cut, for shape only.** At two distributions (relist 1) the terminal
  bucket reads ≈12.7% grant family — but that bucket is dominated by petitions
  whose story ended there, and this one's has not: the CVSG guarantees further
  distributions, so the CVSG and band anchors dominate.
- **Circuit.** CA10 origin is roughly at the modern-cert average (grant family
  ≈4.0% unconditional) — no adjustment.

## Adjustments from the record

**Up from the ~35–41% anchor range:**
- Full escalation ladder in eleven weeks: respondents waived, the Court
  *requested* a response (Aug 14), distributed twice, then CVSG'd on the second
  conference. That is faster and cleaner than the typical CVSG'd petition.
- Four QPs sit in an actively policed area: three on Smith
  neutrality/general-applicability (the petition leans on the Court's 2025
  Catholic Charities decision) plus a novel ACA-preemption question with a
  direct federal statutory interest — the natural CVSG target.
- A Tenth Circuit dissent (Judge Carson) on the neutrality/gerrymander point.
- Cert-stage amicus support, and respondents retained Erwin Chemerinsky — a
  signal respondents price the grant risk as real.
- The current Solicitor General's office has been favorable to free-exercise
  claimants; a petitioner-side SG brief is more likely than not, and an SG
  grant recommendation is historically followed at a high rate.

**Down:**
- **Vehicle.** The BIO's strongest material is not the split denial but the
  record: this is review of a preliminary-injunction denial with no factfinding;
  the Tenth Circuit itself noted (Pet. App. 23a n.9, 27a n.11) that the
  secular-comparator record was undeveloped and the substantial-burden theory
  unpreserved. The SG often recommends denial on exactly these grounds even
  when sympathetic on the merits.
- The claimed neutrality split (subjective animus vs. objective gerrymander
  inquiry) is contested; the BIO plausibly answers that few HCSM cases exist
  anywhere and the circuits apply one test. The Court has repeatedly denied
  Smith-clarification vehicles in recent Terms.
- Only 490 of Gospel Light's ~131k members are in New Mexico — the BIO uses
  this to shrink the stakes and the equities.

Net: the up-signals are largely the *same* signals that put the petition in the
high band and the CVSG cut, so I resist double-counting them; the vehicle
problems are real and specific. I land at **0.42**, slightly above the pooled
band-reached anchor (40.9%), below where a clean-vehicle CVSG'd petition of
this profile would sit (~0.5+).

With P(grant family) below 0.5, the modal single outcome is a denial:
`granted: 0`, `predicted_disposition: denied`.

## Other claims

- `relist-increment` 0.96: mechanical redistribution after the SG files;
  discount is the small pre-filing dismissal/withdrawal/settlement hazard.
- `cvsg-increment` 0.02: vacuous here (CVSG already on the docket at the
  freeze); stated for completeness, the harness masks it.
- `summary-disposition-route` 0.10: post-CVSG grants are almost always plenary;
  residual covers a GVR in light of an intervening free-exercise decision.
- `dissent-from-denial` 0.35: a CVSG'd Smith-standards petition denied on
  vehicle grounds is a likely candidate for a Thomas/Alito/Gorsuch statement,
  but most denials — even of CVSG'd cases — are silent.

## Uncertainty and candor

- The dominant uncertainty is the **SG's recommendation**, which is close to
  outcome-determinative in both directions and genuinely uncertain between
  "grant" and "deny on vehicle / await a final judgment".
- **Corpus freshness:** `fedcourts corpus-info` is not runnable in this cell
  (no locally pulled blob, and the ranged backend's remote URL is not in the
  shell environment — `query` reads through the cell's corpus service instead),
  so I cannot quote the blob-wide vintage. The rows my one `query` returned
  carried `last_live_polled: 2026-08-16`, so the blob is at least that fresh.
  All base rates above are from the repo's committed `metrics/statpack.md`, not
  from live corpus aggregation.
- This forward cell runs ~10 months after its 2025-10-15 snapshot cutoff. Per
  the contract I did not retrieve this case's subsequent history or disposition;
  nothing I retrieved surfaced it (my one corpus query returned other cases).
  The forecast is from the frozen record.
- One corpus query (recent granted SCOTUS petitions) showed the Court granted
  cert on 2026-06-30 in *Grand v. City of University Heights* (25-965), a
  free-exercise case from CA6. I could not verify from the corpus row whether
  its QPs overlap Smith's neutrality standards, so I used it only as weak
  support for the possibility of a hold/GVR interaction, not as a driver of the
  headline number.
- Provisioned documents: `questions-presented.txt`, `petition.txt` (217 pages,
  truncated — the appendix tail is cut; the body I relied on is intact), and
  `brief-in-opposition.txt` (32 pages, complete) all carried text; my read of
  both sides is from the filings themselves, not inferred from the docket.
