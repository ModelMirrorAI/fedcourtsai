# Rationale

## Information set and scope

I read event.yaml, the case-level record/snapshots/2026-09-17.json, and record/context.json. This is a forward cell with an as-stored snapshot and no cutoff. The source payload reports a creation date of September 16, 2026; its last listed proceeding is July 2, 2026. These are snapshot provenance markers, not a claim of a live docket refresh or a corpus-wide last-pull date. I did not query the live docket, retrieve this case's disposition, or consult other predictions or outcomes. I have no known outcome for this petition.

The event has petition kind and no explicit stage, so I preserve the contract's default cert-stage vocabulary and all five declared claims. However, the May 20 filing entry expressly identifies a petition for a writ of mandamus, and the caption is In Re Joan Farr. This is a meaningful scope mismatch, recorded in flags.json. I interpret the binary as whether this petition obtains a grant, rather than silently substituting an ordinary certiorari case or an interim application. The conditional summary-route claim is particularly imperfect for this posture and should be read with that qualification.

The snapshot marks a paid filing, lists the petitioner as her own attorney, and supplies neither a lower court nor lower-court case numbers. Those missing fields do not establish that no lower proceedings occurred. The United States and the listed private respondents waived responses. There is one distribution and no recorded CVSG or subsequent request for a response. The frozen salience class is baseline under sal-v4, and the docket-number Term is 2025. A federal respondent does not turn a private petitioner into the federal-petitioner class.

## Empirical starting point

I used the committed metrics/statpack.md and statpack.json, last changed together at commit 55121cdb8, dated September 14, 2026. I did not pull the corpus or verify its underlying refresh stamps, so these are committed-pack statistics, not independently verified current corpus counts.

For the required sal-v4 baseline comparison, I pooled the bracketed reached rates for every displayed Term strictly before 2025: 2017 through 2024. Using the JSON's unrounded prefix rates and weighted denominators gives 593 grant-family outcomes over 11,580 weighted resolved petitions, or 5.1209%. I did not use the lower terminal-baseline rate, the current Term, or a federal-petitioner rate. This is the pipeline's ordinary private-petition benchmark, not an empirical mandamus success rate.

As broader context, the modern-cert disposition section implies 1,232 grant-family outcomes over 43,700 resolved petitions, or 2.8192%. That whole-docket figure is not my selected-band anchor. The paid-segment terminal relist buckets show roughly 1.7% grant-family probability at zero relists and 13.3% at one; the no-CVSG and CVSG cuts show approximately 6.3% and 34.9%, respectively. These cuts describe terminal groups, not the prospective chance of this petition's next distribution or CVSG. I used their shape only, and none is a matched extraordinary-writ cohort.

## Why 0.5%, rather than 5.1%

The strongest adjustment is the nature of the requested writ. I retrieved the Court's current rules from its official rules page. Rule 20.1 requires an appellate-jurisdiction connection, exceptional circumstances, and no adequate avenue of relief elsewhere, and describes the power as sparingly exercised [R1 in retrieval.md, printed page 24]. Rule 20.3 allows respondents to notify the Clerk that they will not respond [R1, printed page 25]. Thus the waivers are neither admissions nor defaults entitling petitioner to relief.

I place the petition well below the ordinary baseline cert risk set because it seeks exceptional original relief, has no affirmative Court-attention signal beyond routine distribution, and presents no readable showing overcoming the extraordinary-writ hurdles. This is a judgmental adjustment, not a measured likelihood ratio. The multiple response waivers are modest negative posture evidence, not proof that the petition is meritless. Likewise, self-representation and missing metadata cannot by themselves establish a defective claim.

The 0.5% probability retains a small chance that the unreadable filing contains an exceptional basis for intervention. A lower number would overstate what can be established from the docket skeleton; retaining the full ordinary-cert benchmark would ignore the different remedy. The prediction should be discounted for the unmatched reference population and missing substantive content.

The 3% additional-distribution forecast and 0.1% CVSG forecast are judgmental hazards from one recorded distribution and no CVSG, not rates copied from terminal buckets. The 85% conditional summary-route probability reflects my expectation that any extraordinary relief would more likely be handled by an order than by an ordinary cert-to-plenary-review sequence. It is conditional, not multiplied by 0.5%. The 0.3% conditional separate-writing probability reflects the absence of a visible basis for an unusually salient denial, subject to the unreadable petition. None of these ancillary probabilities has been estimated from a matched mandamus sample.

## Missing substance and retrieval limitations

No record/documents directory or document manifest was provisioned. I attempted to retrieve the pre-decision petition at the exact PDF URL in the snapshot, never by searching for this case's current status. The web tool returned no usable content. An in-memory HTTP fetch and pypdf inspection succeeded, but all 22 pages yielded zero extracted characters. I did not visually inspect or OCR the pages. I therefore have not read the questions presented, legal arguments, allegations, or prayer for relief. I did not infer the absence of any legal issue from this extraction failure, and I did not fabricate a question presented.

The docket records response waivers, not a substantive opposition brief; I have no readable opposition. Big-case significance is null for that reason: procedural rarity, party names, and a federal respondent do not establish the dispute's substantive stakes. The durable data-quality note requests readable petition material, while the scope note identifies the original-writ classification issue.

Only official generic rules and the exact historical filing URL were fetched externally. No outcome-revealing material was returned. No CourtListener or corpus-prior lookup was performed. The ordinary uv invocation initially failed because its default cache directory was read-only; using a temporary cache location allowed the paths command to run without changing pipeline code.
