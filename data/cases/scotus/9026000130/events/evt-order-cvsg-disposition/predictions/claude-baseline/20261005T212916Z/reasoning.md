# Reasoning for my numbers

**P(grant) = 0.40**, predicted disposition `denied` (the modal outcome), confidence 0.55.

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-10-05.json` (named by `context.json`), `record/context.json` (mode `forward`, band `high` under `sal-v4`, distribution_count 1, cvsg_date 2026-10-05, term 2026, cut_kind `date`, cutoff 2026-10-06), `event.yaml` (stage cert, moment cvsg, opened 2026-10-05), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (49 pages, full text) and `brief-in-opposition.txt` (43 pages, full text). No document had `empty_text`. Beyond those: the committed `metrics/statpack.md`, two `fedcourts query` calls, and three CourtListener MCP lookups (see `retrieval.md`).

## Anchors

- **Salience band.** `context.band` is `high` under `sal-v4`, and the statpack's "Segment base rate by salience band" table is also `sal-v4`, so it is the anchor. Pooling the bracketed `reached` figures for `high` over every Term row strictly before 2026 (2017–2025, nine rows; the 2026 row is blank) gives a grant-family rate of **35.5% (n=966)**. That is the yardstick the evaluator scores this cell against.
- **CVSG cut.** The paid scored segment's CVSG bucket: denied 62.0%, granted 29.4%, gvr 5.5%, dismissed 3.1% (n=163 resolved), a grant family of about **34.9%**. The two anchors agree at roughly 35%.
- The modern discretionary-cert overall rate (a few percent) is the wrong population here and I did not use it. The relist cut is also not the right anchor: the one distribution on this docket is the ordinary pre-CVSG state, not a relist.

## Adjustments from 35% up to 40%

Up:
- **The Court acted at the first conference.** The CVSG issued the week after the September 28 conference, with no relist first. That is the Court's own signal that at least some Justices see a real question.
- **Petitioner and amici.** Counsel of record is a former Acting Solicitor General at Gibson Dunn; five cert-stage amicus briefs support the petition, including the Chamber of Commerce and National Mining Association, the Canadian and British Columbia mining associations, Pacific Legal Foundation, Washington Legal Foundation, and, unusually, a foreign sovereign (the Province of British Columbia). That is a strong business-amicus profile the current Court tends to respond to.
- **The question suits this Court's method.** The petition's core argument (the Ninth Circuit rested an expansive damages rule on a "Reports and studies" provision in a "Miscellaneous" subchapter rather than on the liability section) is a Sackett-style textual point, and the Court has repeatedly granted CERCLA-scope cases (Atlantic Richfield, Guam, CTS, Burlington Northern).
- **Stakes.** Over $500 million in tribal-specific claims on top of $177 million in joint claims; the petition credibly argues the issue rarely reaches a final judgment because NRD claims settle.

Down:
- **The split is thin.** The BIO is persuasive that neither Ohio v. Department of the Interior (D.C. Cir. 1989) nor New Mexico v. General Electric (10th Cir. 2006) addressed cultural-use damages, and that Ohio in fact supports counting nonuse/existence values. The "three-way split" is really one circuit decision plus two arguable tensions. The Court denies many high-stakes petitions with no square conflict.
- **Interlocutory posture.** The order came up under § 1292(b); no damages have been awarded; the Ninth Circuit held only that cultural-component damages are not categorically excluded and left methodology for trial. The SG often recommends denial in exactly this posture, and the Court often agrees.
- **A real vehicle problem.** The BIO points out that § 9607(f)(1)'s "use only to restore, replace, or acquire" sentence, on which Teck's merits argument leans, textually applies to the United States and States and not to Tribes (the 1986 amendment restructured the sentence). Teck's footnote answer depends on a Statutes-at-Large argument no court has passed on. That makes this case a less clean vehicle than the petition claims.
- **The United States' prior position.** The United States filed a panel-stage amicus brief supporting the Tribes, and Interior's own regulations (43 C.F.R. § 11.83(c)) expressly count nonuse values and, in the 2008 preamble, cultural and ceremonial losses. Even a differently inclined Administration has institutional reasons (trustee recoveries such as Deepwater Horizon) not to argue that nonuse values are unrecoverable. I weight the SG recommending denial at roughly 60%.
- **Litigation history.** This Court has twice denied certiorari in this same case (552 U.S. 1095 (2008); 587 U.S. 1051 (2019)); my recollection, which I could not verify on CourtListener because the Supreme Court dockets are not indexed there, is that the 2008 denial followed a CVSG in which the SG recommended denial. Treat that as unverified background rather than evidence.

Netting: roughly 0.4 × 0.75 (grant given an SG grant recommendation) + 0.6 × 0.22 (grant given a denial recommendation) ≈ 0.43; I shade to 0.40 for the vehicle and posture issues. The honest range is 0.33–0.48.

## The other claims

- **relist-increment 0.96.** After the SG files, the petition is redistributed; the count rises unless the case settles or is withdrawn first. Dismissal/withdrawal risk is a few percent given the litigation's history.
- **cvsg-increment 0.01.** A CVSG is already on the docket; the harness masks this claim as vacuous for a CVSG-moment cell.
- **summary-disposition-route 0.04.** Conditional on a grant, no intervening decision supports a GVR and the question is contested, so plenary review is the route.
- **dissent-from-denial 0.20.** Conditional on denial. A CVSG'd business case with heavy amicus support draws a written dissent more often than the docket at large, but most post-CVSG denials are silent; Justice Gorsuch is the most plausible writer.
- **big_case_score 0.55.** Significant for CERCLA practice, tribal trustees and cross-border industry; not a marquee case for the general public.

## Where to discount me

The SG's likely recommendation is the single largest uncertainty and I have no direct evidence of the current Administration's view; the petition itself notes the government sought time to file at the rehearing stage and then did not. I could not verify the prior petitions' CVSG history on CourtListener. I have not read the Ninth Circuit opinion itself (153 F.4th 947) beyond the parties' characterizations and the petition appendix excerpts quoted in the briefs. I did not read any amicus brief text. This is a forward cell; no post-snapshot material about this docket was consulted or surfaced.
