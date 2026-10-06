# Why 0.18

## Inputs read

- Snapshot `record/snapshots/2026-10-05.json` (11 docket entries; paid docket 25-1199, Term 2025, CA11, linked with extension application 25A824).
- `record/context.json`: forward mode, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, `signals_observable` true.
- Provisioned documents: `questions-presented.txt`, `petition.txt` (38 pp), `brief-in-opposition.txt` (19 pp, SG). None flagged `empty_text`; none truncated.
- `metrics/statpack.md`: modern-cert disposition, relist-count, CVSG, and per-Term salience-band tables.
- Retrieved (forward cell, unrestricted): the companion *Berry v. United States* docket (No. 25-7026) and three of its filings (petition, SG's BIO, petitioner's 8/5/2026 supplemental brief), plus the *Young v. United States* (No. 24-571) docket. Details in `retrieval.md`.

## Anchor

Context band is `elevated` under `sal-v4`, which matches the statpack table's version, so the band table is the anchor. Pooling the bracketed `reached` rate for `elevated` over Term rows strictly before this case's Term (2017 through 2024; the 2025 row contains this case and the 2026 row is empty) gives roughly 484 grants over 2,810 reached petitions, about **17%**. For shape, the relist-count cut (terminal counts, denial-reweighted, paid scored segment) puts the grant family (granted plus GVR) at about 13% for petitions ending at one relist and about 41% at two; the CA11 circuit cut is unremarkable (about 3.6% grant family); the CVSG cut is irrelevant because the SG is a party.

## What moves the number

**Up: the companion case.** This petition's single relist is not an isolated signal. *Berry* (same question, same circuit, Federal Public Defender counsel) drew a call for a response after the SG waived, two amicus briefs (NACDL, former federal judges), relists on 6/18 and 6/25, a carry-over past the summer, and then distribution with *Clark* for 9/28 and a joint relist to 10/9. *Berry*'s supplemental brief says in terms that the Court appears to have held *Berry* to consider it with *Clark*, and asks the Court to grant *Berry* and hold *Clark*. The SG's *Clark* BIO itself incorporates the *Berry* opposition. So the Court is deciding the two together, and I put the chance it grants *Berry* at roughly 40-45%.

**Down: this petition's own vehicle.** Everything specific to *Clark* argues against a grant of this petition on its own merits:
- The CA11 COA orders are one-line denials that do not state a ground, so it is unclear whether the "foreclosed by precedent" rule was even applied; *Berry*'s own counsel makes this point against *Clark*.
- The SG's reading of the restitution/forfeiture circuits is more careful than the petition's 5-2 count: the Second Circuit has only reserved the question while continuing to reject such challenges, and the Sixth Circuit's *Ratliff*/*Weinberger* line is unreasoned, confined to ineffective-assistance claims, and distinguished by that court in *Amaya* (2023). If there is no underlying split, QP1's predicate is missing here.
- Procedural default: petitioner deliberately abandoned his direct appeal rather than brief restitution and forfeiture.
- Petitioner is no longer in custody at all (supervised release ended January 2026), and CA11 precedent lets him pursue coram nobis, which undercuts the practical stakes.
- The Court denied *Young v. United States* (No. 24-571), a CA11 restitution/forfeiture-adjacent petition, in April 2025 after a call for a response.
- Petitioner's own reply (as characterized by *Berry*'s supplemental brief) does not argue that *Clark* is the better vehicle; it asks for consolidation or, at minimum, a hold.

**The arithmetic.** The grant-side outcomes for *this* docket are (a) a consolidated grant with *Berry*, which I put near 4%, and (b) a hold followed by a GVR after a petitioner-favorable *Berry* decision: about 0.42 (Berry granted) x 0.8 (Clark held rather than denied outright) x 0.65 (petitioner prevails in Berry) x 0.7 (Court GVRs rather than denies, given the unclear basis of the CA11 order) = roughly 14%. Together about 18%. That lands essentially on the band anchor: the companion signal and the vehicle weakness roughly cancel. GVR counts as a grant on the binary axis, which is why the number is not lower.

## Claims

- `disposition` 0.18, as above.
- `relist-increment` 0.62: a hold-then-dispose path and a dissent-writing path both add distributions; only a prompt denial of both petitions does not.
- `cvsg-increment` 0.01: the United States is the respondent.
- `summary-disposition-route` 0.75 (conditional on a grant): the dominant grant path is a GVR.
- `dissent-from-denial` 0.25 (conditional on a denial): a Sotomayor dissent in the paired denial is plausible but would more naturally be captioned in *Berry*; a denial after a hold would draw no writing.

## Uncertainty and where to discount me

- The biggest uncertainty is *Berry*'s fate. Four distributions with a CFR and amici is a strong pattern, but the SG raises real vehicle problems there too (procedural default, a Davis claim filed years after the one-year deadline) and argues the COA question has no practical effect. If *Berry* is granted, almost all of this cell's probability mass is a derivative GVR well into 2027.
- The joint 10/9 relist is equally consistent with a dissent from denial being drafted; I weight the "waiting for Clark" explanation more heavily because the timing matches the SG's extended *Clark* BIO deadline and because *Berry*'s counsel reads it the same way, but that reading is an inference, not a docket fact.
- I did not read *Clark*'s reply brief directly; its content is known to me only through *Berry*'s characterization of it.
- The *Berry* petition and BIO texts came from supremecourt.gov PDFs extracted locally; CourtListener's MCP server carried the docket shell but no entries or documents for that docket.
- Big-case score of 0.3 reflects a technical but recurring habeas-procedure question; the petition's financial-penalty narrative does not change what a decision would actually do.
