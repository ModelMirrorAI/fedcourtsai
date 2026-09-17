# Why 0.005

## What I read

- Snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names). Paid docket No. 25-1301, Term 2025, docketed May 22, 2026, from the Supreme Court of California (S287041, review denied November 13, 2024). Two proceedings entries: the petition (response due June 22, 2026) and a single distribution on July 8, 2026 for the conference of September 28, 2026. No waiver, no brief in opposition, no amicus, no CVSG.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, `cvsg_date` null, `signals_observable` true, term 2025.
- `record/documents/petition.txt` (17 pages, text extracted, not truncated) and `questions-presented.txt`. No BIO was provisioned because none exists on the docket.
- `metrics/statpack.md`: the modern discretionary-cert section, the relist-count and CVSG cuts for the paid scored segment, and the per-Term "Segment base rate by salience band (sal-v4)" table.

## The anchor

The context freezes my band as `baseline` under `sal-v4`, which matches the table's version, so the yardstick is the baseline column's bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling OT2017 through OT2024 (all eight prior rows the table renders):

| pooled | grants (weighted) | n | reached rate |
| --- | --: | --: | --- |
| baseline, OT2017-OT2024 | 593 | 11580 | 5.1% |

That 5.1% is the rate for the whole private-petitioner paid class that ever sat in the baseline band. The relist-count cut says a paid scored-segment petition that ends at zero relists resolves granted 1.2% plus GVR 0.5%, and the CVSG-none bucket runs about 6% grant family, but both are terminal-state cuts and I read them for shape only.

## Adjustments, all downward

Nearly everything about this petition sits at the weak tail of the baseline population, and the anchor's 5.1% is dominated by counseled petitions with real federal questions.

1. **No federal question was decided below.** The California Court of Appeal dismissed the appeal because the record was not procured, and the California Supreme Court denied review without comment. The judgment rests on an independent state procedural ground, which by itself would defeat review under 28 U.S.C. 1257 even for a well-drafted petition.
2. **The questions presented are not justiciable questions.** They quote Article III and assert a Commerce Clause right of licensed physicians to treat tribal members, then ask whether this Court "has the right to intervene" in a state medical-board revocation. There is no circuit or state-court split, no statute construed, and no lower-court holding on the theory.
3. **Pro se, self-represented petitioner, improper respondent.** The named respondent is the Court of Appeal itself. The petition is largely a narrative defense of the petitioner's cancer therapy and his record-keeping, with a one-page "Reasons for Granting" that argues the state acted from financial motive.
4. **No response and no waiver.** The state parties did not even file a waiver; the Clerk distributed after the response date passed. Silence from the respondent side is typical of petitions the respondent expects to be denied without a call for a response.
5. **No GVR path.** I know of no intervening decision of this Court that bears on the petition, so the one route by which weak petitions sometimes register as grants in the statpack is closed.

Petitions with this profile are denied essentially without exception. My honest estimate of a grant is well under 1 percent. I write 0.005 rather than something smaller for two reasons: the scoring rule punishes overconfidence at the extremes more than it rewards it, and there is a small identity question about the record (below) that argues for a sliver of mass on "this cell is not the case I think it is."

## The increments

- **Relist (0.06).** From one distribution for the long conference, the ordinary path is disposition on first consideration. The relist-count cut's own caption notes that a rescheduling before first consideration adds a distribution entry, and long-conference petitions are occasionally rescheduled, so I do not go lower than a few percent.
- **CVSG (0.002).** No federal interest, no federal party, pro se. Effectively nil.
- **Summary route conditional on grant (0.6).** Plenary review here is not a coherent world; a grant would almost have to be a GVR or other cert-order disposition. I stop at 0.6 rather than higher because conditioning on such an improbable event mostly conditions on my being wrong about the case, and in that world I know little about the route.
- **Dissent from denial (0.01).** No Justice has an evident stake and the petition offers no vehicle.

## Stakes

`big_case_score` 0.03. One physician's license revocation, decided below on a procedural default. No doctrine or class of litigants turns on it, whatever the petition says about Medicare savings.

## Retrieval and what it told me

- One `fedcourts query --court scotus --era 2020s --limit 8` pulled eight recent SCOTUS rows, ranked by recency; they were mostly September 2026 emergency applications and gave me no comparable pro se cert priors. The query surface has no filter for pro se status or state-court origin, so I did not burn further turns on it and relied on the statpack cuts instead.
- One CourtListener MCP lookup of docket id 73374809. CourtListener's record for this id carries case name "Walter A. Bernard v. Philip Ignelzi" with docket number 25-1301, last modified May 21, 2026, and no termination date. The provisioned snapshot, the petition text, and the supremecourt.gov PDF URL all agree that 25-1301 is Matsumura v. Court of Appeal of California, so I treat the snapshot as authoritative and CourtListener's caption as stale metadata. I flagged it in `flags.json` as a data-quality note. The lookup also confirmed the docket is not terminated, consistent with the forward mode.
- I did not search for this case's disposition and did not encounter one. I have no prior knowledge of this case.

## Where to discount me

The prediction rests almost entirely on the petition text and the docket posture, which are unambiguous. The main residual risk is not legal but clerical: if the provisioned record were somehow attached to the wrong case, my number would be far too low. I could not find evidence of that in the provisioned files, only the CourtListener caption mismatch noted above.
