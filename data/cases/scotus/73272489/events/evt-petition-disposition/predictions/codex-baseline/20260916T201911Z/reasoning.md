# Rationale for the probabilities

## Information set and target

This is a forward cert-stage prediction for Leslie Sanders v. City of Long Beach, California, Supreme Court docket 25-1235. The petition-kind event has no explicit stage or moment field; I apply the prompt's cert default and the five-claim contract for `evt-petition-disposition`. I read the case-level `record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/documents.json`, `petition.txt`, and `questions-presented.txt`.

The frozen context supplies `baseline`, salience version `sal-v4`, Term 2025, one distribution, no CVSG, observable proceedings, and no cutoff. The snapshot is dated September 16, 2026; its last listed proceeding is the June 17 distribution for September 28. That is the vintage of the case material used, not proof of a fresh external docket check. The petition text was fetched July 17, is reported as 24 pages, and is neither empty nor truncated. The questions-presented extraction includes the start of the parties section, but the actual question remains legible.

No brief in opposition or separate lower-court opinion/appendix text was provisioned. The snapshot does not list a response, response request, or waiver. I do not equate those omissions with a waiver or concession. The appendix is linked in the snapshot but was not fetched. Descriptions of the trial evidence, misconduct, and appellate reasoning below are the petitioner's account, not independently established facts. I neither know nor retrieved this petition's eventual disposition, and encountered no outcome-revealing material.

## Base-rate anchor

I used the committed `metrics/statpack.md` as a frozen aggregate, not a freshly pulled corpus. Its `sal-v4` table matches the context. The petitioner is a private individual; the municipal respondent does not put the petition in the state-petitioner class. I therefore pool the **bracketed reached baseline** figures over every displayed Term strictly before 2025: 2017 through 2024. Their weighted resolved denominators total 11,580. Multiplying each denominator by its displayed rate and pooling gives approximately **5.12%** P(any grant). This executed calculation uses rounded published percentages, so it is an approximate anchor rather than an exact reconstruction of underlying weighted grant counts. Terms 2025 and 2026 are excluded.

The modern-cert disposition section supplies the population context; the relist and CVSG cuts reinforce that a single distribution is different from a mature repeated-distribution or CVSG posture. Those cuts group terminal states, however, and contain Terms outside the eligible anchor window. I do not substitute their terminal rates for the reached rate or treat them as measured forward hazards. The case arose in a California state appellate court, not the Ninth Circuit, so I do not apply the Ninth Circuit bucket. No corpus-wide freshness claim or case-specific current-status claim is made from the committed pack.

## Why the grant estimate is much lower

I reduce the approximately 5.12% class anchor to **0.3% P(any grant)** principally for the petition's substance and vehicle quality, not simply because its author is self-represented:

- The question presented and petition pages 3–16 largely ask for correction of the handling of documentary evidence, depositions, hearsay, witness credibility, and notice of a dangerous pump condition in a municipal flooding suit. They do not identify opposing appellate holdings on a precisely framed federal question.
- The petition's repeated appeals to uniformity combine California tort authorities, federal evidentiary and procedural rules, constitutional guarantees, and criminal impeachment authorities. Those citations and assertions do not themselves demonstrate a controlling federal conflict in this state civil proceeding. This is an assessment of the petition's showing, not a finding that the alleged unfairness did not occur.
- The petition describes the appellate opinion as unpublished (page 1). On page 15 it acknowledges that the appellate court faulted the absence of record citations or legal authority supporting misconduct allegations, while disputing that criticism. Without the opinion or appendix I cannot determine the exact preservation or record-support ruling, but the acknowledged dispute is a meaningful vehicle risk. I do not assert an established independent state ground.
- The supplied record contains no visible escalation beyond the first routine distribution and identifies no companion case, intervening ruling, or federal governmental interest likely to produce a hold, GVR, or CVSG.

I retain a small positive probability because a serious denial of a fair opportunity to present evidence could matter if supported by the actual record, which I have not independently examined. The 0.3% estimate is a judgmental adjustment, not a fitted empirical rate for comparable pro se petitions. Missing opposition and lower-court text limit confidence in the vehicle assessment.

## Other claims and stakes

The 2.5% additional-distribution forecast leaves room for administrative rescheduling or closer inspection; the modal outcome is no increment from the supplied count of one. The 0.1% CVSG estimate reflects the localized dispute and lack of an identified federal institutional interest. Neither number is claimed to be an empirically estimated hazard from the statpack. The 15% summary-route estimate is conditional on a grant, not an unconditional 15% chance of relief. The 0.3% writing estimate is conditional on denial and concerns aggregate existence only. No cert vote block is supplied because individual votes are not observable here.

A stakes score of 0.15 recognizes consequential home damage and fair-hearing interests while distinguishing those local interests from demonstrated nationwide doctrinal significance. It is not another grant probability.

## Retrieval limitations

General-source verification was attempted without searching for this case: a web search concerning Supreme Court Rule 10 and an opening of an official rules PDF returned no usable material. A shell attempt to fetch the same PDF returned HTTP 404, and the PDF-to-text executable was absent. No retrieved legal text from these attempts informed the forecast. The forecast instead rests on the provisioned advocacy and docket, the prompt's cert framework, and the committed aggregate rates. No CourtListener or live corpus query was needed or made. The initial path command encountered a read-only default uv cache; redirecting the cache to temporary storage and using the existing environment resolved it.
