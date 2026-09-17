# Why 0.20, and not something else

## Mode and inputs

Forward cell (`context.json`: `mode: forward`, `cutoff: null`, `snapshot_provenance: as-stored`). I read the provisioned snapshot `record/snapshots/2026-09-15.json`, `context.json`, `documents.json`, and all three provisioned documents: `questions-presented.txt`, `petition.txt` (39 pp., FIRE, filed March 26, 2026) and `brief-in-opposition.txt` (31 pp., Williams & Connolly, Lisa Blatt counsel of record, filed June 17, 2026). None was flagged `empty_text` or `truncated`. I did not read the reply brief, which is not provisioned. The conference this petition awaits (September 28, 2026) is after today, so no disposition exists and nothing I retrieved could leak one.

## Anchor

`context.json` freezes `band: elevated` under `sal-v4`, Term 2025, `distribution_count: 2`, no CVSG. The statpack's "Segment base rate by salience band (sal-v4)" table heading matches the context's version, so the band is my anchor. Pooling the bracketed **reached** `elevated` figure over the eight rendered Terms strictly before OT2025 (OT2017 through OT2024, n = 400, 347, 334, 397, 342, 300, 354, 336) gives roughly 484 grants over 2,810 risk-set petitions, about **17%**. That is the yardstick the evaluator will score this cell against.

Shape checks beside it: the relist-count cut puts a paid petition with one relist at about 13% grant family (8.2% granted plus 5.1% GVR); the CVSG cut's `none` row sits near 6%; the CA6 originating-circuit row is about 2.8% grant family over all modern paid and IFP cert petitions. All are consistent with an elevated-band petition sitting in the mid-teens before case specifics.

## What the scorer already prices, and what it does not

The salience scorer's lattice is relist count, CVSG status, originating circuit, and petitioner caption class. So the band already reflects "two distributions, no CVSG, CA6, private petitioner." Two things in this record are **not** in that lattice and are my main upward adjustments:

1. **The Court called for a response** (May 18, 2026) after respondents waived. That is an affirmative act by at least one chambers, and the Court then redistributed the fully briefed petition to the long conference.
2. **Four amicus briefs at the cert stage**, from repeat players (Buckeye, Defending Education, NCAC) and a scholars' brief, on a petition filed by a well-known First Amendment litigator.

Also upward: a **published, divided Sixth Circuit opinion** with a long dissent by Judge Bush that expressly says the Supreme Court must clarify Fraser, an **en banc denial with a noted dissent**, an admittedly nondisruptive and concededly political message (both sides and both panel opinions agree on those facts), and a doctrinal question this Court itself called unclear in Morse v. Frederick. The current Court's speech docket has been receptive to student and religious speech claims, and the slogan's political valence runs in the direction of the Justices most likely to be interested.

## Why I did not go higher

- **The relist signal is weaker than the count suggests.** `distribution_count: 2` reads as one relist, but the first distribution was superseded by the response request before any conference and the second is the first distribution of the briefed petition. The Court has not yet voted on this case even once. The elevated band therefore slightly overstates the trajectory evidence.
- **The split is thin.** The BIO's strongest section argues, credibly, that only the en banc Third Circuit (B.H. v. Easton) has adopted a "plainly lewd versus ambiguously lewd" framework, that the Ninth Circuit's Chandler language was a pleading-stage aside, and that the Second Circuit has not adopted the petitioners' test. A one-circuit split on the framing question is at the low end of what draws a grant.
- **Vehicle problems.** The Sixth Circuit found "Let's Go Brandon" carries a "plainly vulgar meaning," and the students admitted below that they understood it that way. That makes the QP's premise ("not plainly profane or lewd") contestable on this record, and the Court dislikes granting to fight over an antecedent factual characterization. The older student has almost certainly graduated, narrowing prospective relief to the younger one, and the damages claims face qualified immunity. The injunctive claim keeps the case live, so this is a discount, not a bar.
- **Recent revealed preference.** In May 2025 the Court denied review in L.M. v. Town of Middleborough (No. 24-410), a First Circuit student-shirt case, over a dissent by Justice Alito joined by Justice Thomas. That is public information predating my snapshot and legitimate forward signal: a comparable student-speech vehicle recently drew two, not four, votes. Mahanoy was the Court's first student-speech merits case in fourteen years, and it is not eager for more.
- **Expert opposition.** The BIO is a strong, vivid Williams & Connolly brief that gives a denial-minded clerk everything needed.

Netting these, I land a few points above the pooled anchor: **P(grant) = 0.20**, `predicted_disposition: denied`, `granted: 0`.

## The other claims

- **relist-increment 0.42.** Nearly all of the 0.20 grant mass requires a relist first; add relists ending in denial with a separate writing, and the occasional reschedule that the harness counts as a distribution. I do not expect a long relist string because nothing is pending to hold this for.
- **cvsg-increment 0.02.** No federal interest; the CVSG cut is essentially irrelevant here.
- **summary-disposition-route 0.05.** Conditional on grant. No intervening decision, a published reasoned opinion below, and a doctrinal question that wants argument.
- **dissent-from-denial 0.30.** Conditional on denial. Alito and Thomas wrote on a comparable case sixteen months ago; the topic and the FIRE petition make a repeat plausible, but the coded-profanity facts are a less attractive platform than the "Two Genders" shirt was, and most CFR denials draw no writing.

## Big case score

0.55. If decided, the case would set the scope of Fraser for roughly fifty million public-school students on a nationally recognizable slogan and would be widely covered. It is not a structural or separation-of-powers case, so it sits above the median grant but well short of the Term's headline cases.

## Uncertainties and where to discount me

- I have not read the reply brief or the amicus briefs, only the docket entries for them.
- I cannot see internal Court signals; the response request is the only observed indication of interest, and I may be over-reading it.
- The pooled `elevated` anchor is a whole-band average; within that band this petition has more positive signal than typical (CFR plus four amici), which is why I sit above it, but I cannot quantify how far the un-modeled features move the rate.
- Corpus retrieval: my topic-filtered `fedcourts query` returned nothing because SCOTUS rows carry no topic strings (a known coverage gap, per the tool's own note), so my priors come from the statpack tables and general knowledge rather than a corpus neighbor set.
