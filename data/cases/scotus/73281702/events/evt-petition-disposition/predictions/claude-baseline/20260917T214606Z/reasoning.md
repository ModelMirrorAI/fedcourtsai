# Why P(grant) = 0.10

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names), `context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025), `event.yaml` (a `petition` kind with no stage, so cert), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (57 pages, including the published Eleventh Court of Appeals opinion), and `brief-in-opposition.txt` (32 pages), none flagged `empty_text` or truncated. Beyond the record I fetched the September 15, 2026 reply brief from the docket link on the snapshot (it postdates the provisioning of documents but sits on the snapshot itself), one corpus priors query, and three CourtListener searches, all listed in `retrieval.md`.

## The posture

Paid petition, private petitioner (a Texas state prisoner serving 40 years), state respondent. Filed April 15, 2026; Texas waived; distributed for the May 28 conference; the Court called for a response on May 26; Texas took an extension and filed its brief in opposition on July 24; distributed for the September 28, 2026 long conference; reply filed September 15. Two distributions, no CVSG, no amici. Counsel of record is a solo Fort Worth practitioner, not a repeat Supreme Court advocate.

## Anchor

`context.json` carries band `elevated` under `sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" table is the same version, so the table is my anchor. Pooling the bracketed `reached` figures for `elevated` over the Terms strictly before OT2025 that the table renders (OT2017 through OT2024, n from 300 to 400 each) gives about 17 percent (484 of 2810 weighted). The single-Term figures run 13.8 to 20.5 percent, so the anchor is stable. That figure already prices the call for a response and the second distribution, which is what put the petition in the band.

For shape only: the paid-segment relist cut shows petitions ending at one relist granted at about 8 percent and at two relists at about 28 percent, but those bucket by terminal count and are not the forward hazard from my state.

## Adjustments down from the anchor

- **No split, and the petition does not claim one.** The petition's Rule 10 hook is that the question is important and unsettled after Ramos. The BIO answers that no appellate court anywhere has struck a continuous-sexual-abuse statute on this ground, cites the Hawaii Supreme Court's 2024 decision in State v. Tran collecting post-Ramos cases the other way, and quotes LaFave for the proposition that Ramos did not change which findings must be unanimous. The reply does not dispute the absence of a split.
- **Richardson itself distinguishes these statutes.** The majority in Richardson noted that state course-of-conduct statutes for child abuse "may well respond to special difficulties of proving individual underlying criminal acts," and the dissent agreed. The petitioner's best argument is that Richardson added that the Court had not then held unanimity binding on the states, which Ramos changed. That is a real point, but it asks the Court to convert a dictum-plus-incorporation inference into a grant against uniform lower-court authority.
- **The Schad framework favors the State.** Whether a fact is an element or a means is treated primarily as legislative choice, and § 21.02(d) states that choice expressly. Mathis in 2016 relied on the same means/elements distinction without qualm.
- **Thin petition, no amici.** Fourteen pages of argument, no survey of how the other eight or so states with similar statutes have handled the question, no amicus support from defender organizations. The reply is better written but still cites nothing new beyond Timbs, McDonald and the Apodaca-era cases.
- **Vehicle and optics.** A facial challenge on grim facts, with concurrent 10 to 20 year sentences on six other counts that would stand regardless, and a second, unrelated unanimity claim (a juror's next-day reservations) that the petition folds into its argument as showing the harm. None of that is fatal, but none of it makes the case attractive.
- **Prior denials.** I believe the Court has denied comparable post-Ramos petitions from Texas and California continuous-abuse defendants without noted dissent. I could not confirm that through CourtListener (its SCOTUS docket coverage returned nothing for the phrase, and denials leave no opinion), so I weight it lightly.

## Adjustments up from the anchor

- **The call for a response came after a waiver.** That is the clearest signal on the docket: a chambers looked at a waived petition and wanted the State's answer. It is already inside the band's rate, so I do not double count it, but it keeps me from discounting far below the anchor.
- **The question is genuinely open at this Court.** Ramos incorporated the unanimity right while Schad and Richardson predate incorporation; Justice Gorsuch's history-and-tradition approach in Ramos gives a coherent path to the petitioner's reading of Richardson. If a Justice wants to develop the content of the incorporated right, this is a clean, preserved, published-opinion vehicle from the largest state using such a statute.
- **Stakes.** The statute carries 25 to 99 years or life without parole eligibility, and many states have analogues, so a grant would not be trivial error correction.

## Net

I land at 0.10, below the roughly 17 percent band anchor, because the splitless, uniformly-rejected, thinly-briefed posture is the kind the Court usually clears off the long conference even after a CFR, and the up-adjustments are mostly already inside the band figure. My main uncertainty is whether the chambers that called for the response is a Gorsuch-style unanimity interest strong enough to build four votes, versus a routine clerk-pool CFR on a waived petition with a published opinion; the former would put this near 0.25, the latter near 0.05.

## Other claims

- `relist-increment` 0.35: CFR'd petitions are relisted more than ordinary ones, and a dissent-writing relist is possible, but the modal path from a long conference is a straight denial.
- `cvsg-increment` 0.02: no federal interest.
- `summary-disposition-route` 0.10 (conditional on grant): no intervening decision to GVR on, no basis for summary reversal against uniform authority.
- `dissent-from-denial` 0.15: Justice Gorsuch is the plausible author; most such denials are silent.
- `big_case_score` 0.5: a decision would govern continuous-sexual-abuse statutes in Texas and roughly nine other states and reach thousands of sentences, but the question is specialist criminal procedure rather than front-page news.

## Where to discount me

Everything about prior denials on this question is from memory rather than retrieval. The corpus query has no topic filter on SCOTUS rows, so the priors it returned were generic recent dispositions and did not inform the number. No amicus or press signal exists yet, so the stakes score is my own read of the QP and statute.
