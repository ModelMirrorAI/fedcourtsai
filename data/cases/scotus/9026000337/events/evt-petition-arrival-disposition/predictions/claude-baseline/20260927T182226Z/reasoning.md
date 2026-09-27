# Rationale for P(grant) = 0.015

## What I read

- `record/context.json`: forward mode, `band: baseline` under `sal-v4`, `distribution_count: 0`, no CVSG, Term 2026, `cutoff` 2026-09-15 under a `date` cut. This is an arrival-moment cell: the absence of any conference signal is the moment's definition.
- `record/snapshots/2026-09-15.json`: paid petition, docketed September 14, 2026, from the Eighth Circuit (No. 24-2347, decided May 11, 2026; rehearing denied June 17, 2026). One docket entry: petition filed September 9, 2026, response due October 14, 2026. Counsel of record for the petitioner is a solo practitioner in Miami with Iowa co-counsel; Unum is represented by a Des Moines firm. Not a capital case.
- `record/documents/questions-presented.txt` and `petition.txt` (99 pages, not truncated, text extracted). The appendix includes the full Eighth Circuit panel opinion (Judge Stras, joined by Judges Benton and Grasz) and the district court opinion. No brief in opposition exists yet.
- `metrics/statpack.md`: the modern discretionary-cert section, the circuit cut, the relist and CVSG cuts, and the sal-v4 segment table.

## Anchor

The context's `salience_version` (`sal-v4`) matches the segment table's heading and `baseline` is one of its columns, so the table is a valid anchor. The petitioner is a private individual, so the class floor is `baseline`'s bracketed `reached` rate. Pooling the nine rendered Terms strictly before OT2026 (2017 through 2025) by the weighted `n` beside each figure gives about 5.0% (roughly 637 grants over a weighted 12,720 petitions). That pooled rate is a grant-family rate that includes GVRs. The terminal baseline row of the "Cert petitions by salience band" cut (granted 0.8%, gvr 0.4%) suggests about a third of baseline-band grants are GVRs.

I did not use the relist-0 figure (1.2% granted) as an anchor, per the prompt: it is the rate among petitions that ended undistributed and understates an arrival's prospects.

For shape only: the Eighth Circuit cut sits slightly below the pooled circuit average (granted 1.2%, gvr 1.4%, denied 95.4%), and the CVSG-none cut shows a 4.0% grant / 2.3% GVR rate over the paid scored segment.

## Adjustments from the anchor

Down, substantially, from 5% to 1.5%:

1. **No split, and the petition says so.** Part III of the petition argues that no court has ever applied the known-loss doctrine to guaranteed-issue coverage. That is a concession that there is no conflict of authority. A CourtListener opinion search on the relevant phrases returned only the Eighth Circuit's own opinion among on-point results, and a search for Iowa authority construing § 514G's preexisting-condition provision returned nothing. The Court's cert criteria (Rule 10) put a lone circuit decision on a state-law question near the bottom of its priorities.
2. **The Erie framing does not match the opinion.** The panel's holding is that the policy's plain terms excluded losses existing on the effective date, that Iowa Code § 514G.7(3)(b) does not require coverage of pre-effective-date losses, and that the reasonable-expectations doctrine does not apply. "Known losses" is one supporting citation. This is ordinary diversity adjudication of state contract and statutory law, which the Court treats as error correction, not an Erie methodology question.
3. **Vehicle and advocacy.** A single insured, a private insurer, no amici at filing, no Supreme Court specialist as counsel, and an unanimous published panel opinion with rehearing en banc denied without dissent. None of these features is fatal on its own; together they describe the modal baseline-band denial.
4. **The certification GVR is a thin route.** McKesson v. Doe involved a novel state tort theory with First Amendment consequences and a constitutional-avoidance rationale for certification. Nothing federal turns on the Iowa question here, so the Court has little institutional reason to send the case back for certification.

Up, slightly (holding the number at 1.5% rather than lower):

- The facts are sympathetic and the national-framework argument (every surveyed jurisdiction adopts the NAIC two-track scheme) gives the issue more reach than a purely Iowa-specific reading suggests. Consumer or disability-rights amici are possible once the petition is distributed, which could marginally raise the chance of a look.

## Claim-by-claim

- `disposition` 0.015, equal to `probability`.
- `relist-increment` 0.96. From zero distributions, this resolves true if the petition is distributed even once. Nearly every paid petition that is not withdrawn or dismissed under Rule 46 before conference is distributed; I reserve about 4% for a pre-distribution dismissal, a settlement, or a docketing defect.
- `cvsg-increment` 0.005. No federal interest of any kind; the paid-segment CVSG rate is about 1.2% overall and this case sits far below the population average.
- `summary-disposition-route` 0.5, conditional on a grant. The baseline-band terminal cut puts GVRs at about a third of grants; I raise that here because the only realistic grant is a per curiam vacatur for certification, which is a cert-order disposition, while plenary review of a no-split state-law question is the less likely of two unlikely paths. There is no intervening decision to GVR in light of, which keeps the number from going higher.
- `dissent-from-denial` 0.02, conditional on denial. Sympathetic facts and an occasional judicial interest in certification practice, but no federal hook and no dissent below.

## big_case_score

0.08. The stakes for the petitioner are total, but the decision's reach is one State's guaranteed-issue long-term-care market and, persuasively, other NAIC-model States; it has no public profile and no federal-law consequence.

## Where to discount me

- I have no brief in opposition; my read of Unum's likely position comes from the Eighth Circuit opinion and the district court opinion in the appendix.
- The band anchor is a nine-Term pool over a denial-reweighted segment; the per-Term rates run 3.9% to 5.9%, so the anchor itself carries roughly a two-point spread.
- The `fedcourts query` corpus pull (2020s, granted, SCOTUS) returned mostly substantive interim applications and two high-salience cert grants, none comparable to this petition; it informed nothing beyond confirming the corpus was reachable.
- My knowledge of the Court's treatment of certification GVRs outside the constitutional-avoidance setting is general rather than corpus-derived.

## Provenance

Forward cell. A CourtListener docket search for No. 26-337 returned no results, so no disposition of this petition surfaced. I did not read anything under `data/qp-topics/`.
