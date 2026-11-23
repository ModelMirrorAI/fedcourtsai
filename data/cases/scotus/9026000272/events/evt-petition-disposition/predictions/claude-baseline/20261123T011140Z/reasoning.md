# Reasoning for my numbers

**P(grant) = 0.86.**

## Inputs read
- Snapshot `2026-11-23.json`: petition filed Aug 27, 2026; two amicus briefs in support (22 States led by West Virginia; Flynn et al.) on Oct 1; brief in opposition Nov 2; reply Nov 16; distributed Nov 17 for the Dec 4 conference. One distribution, no CVSG.
- `questions-presented.txt`, `petition.txt` (table of contents and structure; truncated around the appendix), `brief-in-opposition.txt` (question presented, introduction, Parts I and II in full), `cert-reply.txt` (introduction, Part A opening, Part B in full), `decision-below.txt` (caption and opening of the Wilkins opinion; I confirmed it is the June 1, 2026 D.C. Circuit judgment the petition describes), `lower-court-docket.txt`.
- `context.json`: band `federal` (sal-v8), `cert_anchor.rate` 0.731, `cert_amicus_line` 0.836 (arm `some`, n=61), forward mode, no cutoff.
- `same-question.json` lists no matching petitions, and there is no `record/related/`.
- I did not open the `summaries/` files in the case directory, since the contract does not name them as inputs.

## Anchor
The frozen anchor for the `federal` band is 0.731 (reached rate, ten prior Terms). The statpack table agrees: federal-petitioner grant rates of 48% to 96% per Term, e.g. 57.1% (n=28) in OT2025 and 62.5% (n=16) in OT2024. The amicus-arm reference is 0.836. The relist-count cut (bucket 0–1) is not the right reference for a federal petitioner and I did not anchor on it.

## Adjustments up
- The D.C. Circuit held a military personnel policy likely unconstitutional on an animus theory under rational-basis review. A lower court blocking a significant federal policy on constitutional grounds, with the Solicitor General petitioning, is close to the strongest category of petition.
- The Court already stayed a universal injunction against this same policy in full in United States v. Shilling (2025), including as to the individual plaintiffs there, and stayed injunctions against the predecessor Mattis policy in 2019. A stay grant implies a majority thought certiorari reasonably probable and the government likely to prevail.
- Walker dissented below, and the two judges affirming wrote separately, so the judgment rests on a fractured rationale.
- The brief in opposition does not claim the standard of review is anything but Trump v. Hawaii rational basis and leans mostly on vehicle arguments, not on the absence of importance.
- 22 States filed in support at the cert stage.

## Adjustments down
- Vehicle: an interlocutory preliminary injunction narrowed to 28 named servicemembers; a trial is set for January 4, 2027, and a final judgment could moot the appeal; the Ninth Circuit's Shilling appeal is still pending, so there is no split and no second appellate ruling.
- The government concessions and forfeitures the opposition stresses could make the Court prefer to wait for final judgment.
- These points are real, but the Court has repeatedly granted in preliminary-injunction postures in this area (the reply cites Skrmetti, Chiles and B.P.J.), and a grant would likely cause the trial to be stayed.

Net: modestly above both the band anchor and the amicus-arm rate. I count a summary reversal or GVR as a grant.

## Other claims
- `relist-increment` 0.82: the Court almost always relists once before a plenary grant, and a summary reversal or a denial with a writing also requires relists. The only no-further-distribution paths are a straight grant on Dec 4 (uncommon) or a straight denial (unlikely here).
- `cvsg-increment` 0.01: the United States is the petitioner.
- `summary-disposition-route` 0.15 given a grant: the Court's emergency-docket history with this policy makes a summary reversal plausible, but the government asks for plenary review and the question is weighty. The statpack federal band shows roughly 21% GVR among resolved federal petitions, but most of those are holds for other cases, and nothing here is being held.
- `dissent-from-denial` 0.60 given a denial: three or more Justices have voted for the government in every related interim matter, and a denial would likely draw at least a noted dissent.
- `order-writers`: small numbers throughout, since a plain grant order carries no writing. The mass sits on Alito and Thomas (denial scenario) and Sotomayor and Jackson (summary-reversal scenario).

## Uncertainty and where to discount me
- I do not know whether the injunction is currently in effect as to the 28 respondents or whether the mandate has issued. The absence of a stay application on this record suggests the government is not treating the interim status as an emergency, which slightly supports the respondents' narrow-stakes framing.
- Several cases cited in the briefs (B.P.J., Mullin v. Doe, Chiles) were decided after my training data ends. I rely on the parties' characterizations of them.
- I did not read the full Wilkins, Rogers or Walker opinions, only the opening and the parties' descriptions.
- The CourtListener MCP server was not used. The provisioned record was sufficient.
