# Reasoning — claude-baseline, run 20260917T181231Z

**P(grant) = 0.003; predicted disposition `denied`; confidence 0.97.**

## What the record shows

I read the provisioned snapshot `record/snapshots/2026-09-17.json` (the file `context.json`'s `snapshot_date` names) and `record/context.json`. Mode is `forward`; the conference is September 28, 2026, eleven days after the snapshot, so the outcome does not yet exist and no leakage question arises. Context freezes `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG, Term 2025, `signals_observable: true`.

The docket (No. 25-1315, paid) is a **petition for a writ of mandamus** filed pro se by Joan Farr of Webb City, Missouri, docketed May 27, 2026 (dated May 20). The docketed PDFs are all scans (`scan_ajimenez_...`), which is why no `record/documents/` directory exists: the pipeline had no extractable text, so I could not read the questions presented or the relief sought. The respondents are Alexandra Grant and grantLove LLC, Scott Sims and Ziffren Brittenham LLP, WME IMG LLC, and the United States (Solicitor General as counsel of record). **Every respondent waived** the right to respond (June 2, June 22 twice, July 2). The petition was distributed once, on July 1, 2026, for the September 28, 2026 long conference. There are no related case numbers and no lower-court entry on the docket.

Web search (forward mode, unrestricted) identified the underlying litigation: *Farr v. Grant et al.*, W.D. Mo. No. 4:24-cv-00439, filed July 1, 2024 pro se, dismissed and appealed; Eighth Circuit No. 25-1525, judgment dated October 10, 2025. I could not read the Eighth Circuit opinion itself (Justia and CourtListener returned HTTP 403 to the fetcher and govinfo returned an empty page), so the characterization of the suit as a dismissed private civil action rests on the docket caption, the party list, and the search-result metadata, not on the opinion's text. That is enough for this call: the shape of the case, not its content, drives the number.

## Anchor

Cert-stage cell, `moment: distribution`, declared claim set `cert-v2` (confirmed via `fedcourtsai.pipeline.claims.declared_claim_set`). The context's `salience_version` is `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table, so the band table is the anchor. Pooling the **baseline** band's bracketed `reached` figures over the rendered Terms strictly before 2025 (2017 through 2024, eight rows, all that the table shows):

| pooled | grants (weighted) | n | reached rate |
| --- | --: | --: | --- |
| baseline, OT2017–OT2024 | 592.9 | 11580 | 5.1% |

The evaluator scores my skill against that risk-set figure. Shape cuts for context (paid scored segment, terminal buckets): relist bucket 0 grants 1.2% plus 0.5% GVR; CVSG `none` grants 4.0% plus 2.3% GVR. The modern discretionary-cert grant family overall is about 3%.

## Adjustments, and why the number sits far below the anchor

1. **This is a Rule 20 extraordinary-writ petition, not a cert petition.** The band anchor is a cert-petition population. The Court grants mandamus petitions essentially never (Rule 20.1 requires exceptional circumstances and the absence of any other adequate remedy); the realistic modern rate is well under one in a thousand, and the GVR route that supplies a third to a half of the cert grant family does not exist for mandamus. This alone takes the number from ~5% to well under 1%.
2. **Pro se petitioner, private dispute, ordinary appeal already taken.** The underlying suit was dismissed and the Eighth Circuit affirmed, so the mandamus standard's "no other adequate remedy" element is facially unmet. Baseline band already reflects a private petitioner with no signals; a pro se filer against a celebrity-adjacent set of private respondents is the weakest stratum inside it.
3. **Universal waiver, including by the Solicitor General.** Four waivers and no response requested is the docket signature of a petition the Court will deny without discussion.
4. **Single distribution to the long conference.** No relist, no CVSG, no hold candidate.

The residual 0.3% is not a belief that the Court might grant on the merits. It covers resolution noise: an unusual order the harness's terminal-text reader might score as a grant (for example, a grant of some ancillary motion recorded in the same entry), or a docket-parse edge case. I would not put it lower than 0.002 because the scoring harness, not the Court, is the source of the tail.

## The other four claims

- **relist-increment 0.07.** From one distribution. The paid scored segment's terminal share with at least one relist is about 25%, but that pools salience-selected petitions with real grant prospects; the statpack also notes its count is an upper bound because a reschedule adds a distribution entry. For a pro se mandamus petition at the long conference, the hazard is mostly clerical reschedules and a Justice's brief hold. I put it at 7%.
- **cvsg-increment 0.002.** The United States is a party and has waived; a CVSG is for a non-party government. Effectively zero.
- **summary-disposition-route 0.75.** Conditional on a grant. If the Court did anything other than deny, it would dispose of the matter in the order (a summary vacatur or a grant of the writ) rather than set a pro se mandamus for argument. The baseline for this claim is the prior Terms' cert-order share of grants (30–59% depending on Term, per the statpack's caveat on the granted/GVR split); this petition's shape pushes well above that.
- **dissent-from-denial 0.005.** Conditional on denial. No Justice writes on a pro se mandamus of this shape. The one plausible separate text, a Rule 8 sanction order for a repeat filer, is not a dissent and is unlikely on a paid petition.

## Big case score

0.02. Stakes, not odds: a private dispute with no doctrinal question and no government interest.

## Where to discount me

- I did not read the petition or the Eighth Circuit opinion; the mandamus characterization comes from the docket text ("Petition for a writ of mandamus filed"), and the underlying-case characterization from search metadata.
- The CourtListener MCP server was rate-limited (HTTP 429, 300/hour, ~15 minutes to reset) on my first two calls, so I fell back to the corpus query sidecar and web search as the prompt directs. The one `fedcourts query` I ran (`--court scotus --era 2020s`) returned recent stay applications rather than mandamus-alike priors, because the query surface has no petition-type filter; it informed nothing beyond confirming the corpus service was reachable.
- No filed-document text was provisioned. On this cell that is harmless; on a closer case it would matter.
- A prior claude-baseline run on this same event (run 20260718T064904Z, a different snapshot) exists on disk. I did not read its reasoning; I noticed its `prediction.json` while checking the output format. My forecast is formed from the September 17 snapshot alone.
