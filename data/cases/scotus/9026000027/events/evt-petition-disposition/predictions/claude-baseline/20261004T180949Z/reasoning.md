# Rationale for the numbers

**P(grant) = 0.006; predicted disposition `denied`.**

## What I read

- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, snapshot date 2026-10-04, no cutoff.
- `record/snapshots/2026-10-04.json`: paid docket 26-27, petition filed June 30, 2026, docketed July 8; respondents moved for and received an extension of the response date to September 8; brief in opposition filed September 8; distributed September 23 for the conference of October 9, 2026. Five docket entries in all. Petitioner appears pro se (she is listed as her own attorney); respondents are represented by New Orleans insurance-defense counsel.
- `record/documents/questions-presented.txt`, `petition.txt` (38 pages, text extracted cleanly), and `brief-in-opposition.txt` (20 pages, extracted cleanly). `documents.json` shows none truncated and none with `empty_text`.
- `event.yaml`: stage `cert`, moment `distribution`, so the ordinary cert cell and the `cert-v2` five-claim set.

## Anchor

The band table's heading names `sal-v4`, which matches the context's `salience_version`, and `baseline` is a rendered column, so the table is a valid anchor. Pooling the bracketed `reached` figures for `baseline` over the nine rendered Terms strictly before 2026 (OT2017 through OT2025, weighted by their `n`) gives a pooled risk-set grant-family rate of roughly 5.0% (about 637 weighted grants over about 12,720 weighted petitions that ever reached the band). That is the yardstick my skill is scored against.

## Adjustments, all downward

The "reached" denominator includes every paid private petition that later climbed to `elevated` or `high` through relists or a CVSG; the 5% is mostly carried by petitions that acquire those signals. This petition has none and I see no mechanism by which it acquires one:

1. **No federal question preserved.** The petition's only cert-worthy framing (QP 2: a State may not treat a federal employee performing official duties as the statutory employee of the regulated entity, with a FECA / Supremacy Clause gloss) was, per the BIO's account of the opinion below, raised first in a motion for reconsideration and then for the first time on appeal; the Fifth Circuit declined to reach it. The petition itself does not dispute that procedural history. The Court does not grant to decide questions the court below never passed on.
2. **QP 1 is pure state law.** Whether rice inspection is part of a mill's "principal trade and business" is a Louisiana question, and the BIO is right that it is not even the test the courts below applied (they applied the distinct two-contract defense, under which the trade-or-business inquiry is irrelevant per the Louisiana Supreme Court's decision in *Allen*). Most of the petition's argument section is standard-of-review and manifest-error argument on state law.
3. **No split.** The petition cites no conflicting court of appeals or state high court decision; the closest thing is a 1994 Eastern District of Virginia decision under a different State's law, which the Fifth Circuit distinguished and which no court of last resort has adopted.
4. **Unpublished, expressly narrow opinion below.** The panel disclaimed any general rule about regulated entities and federal inspectors and held "only" that on this arrangement no genuine dispute of material fact existed. That is the opposite of a vehicle.
5. **Pro se petitioner.** The brief is professionally printed but the argument structure (lengthy Ninth Circuit summary-judgment boilerplate, Louisiana intermediate appellate authority, a conclusory preemption section) reads as a pro se filing, and the Court almost never grants paid pro se petitions.

The one mildly positive signal is that respondents filed a BIO without being asked, after taking an extension. That is consistent with cautious insurance-defense practice rather than with respondents perceiving a real grant risk, and the BIO itself is short and rests on Rule 10.

Against the relist-count cut, this petition sits in the relist-0 bucket today; that bucket's terminal grant family is under 2%, and it is populated by many petitions far stronger than this one. I place the grant probability well below the baseline-band anchor and near the floor the paid pro se population occupies: 0.006. I do not go lower because a grant family includes GVRs and because the Court occasionally surprises on a federal-employee angle, but I would be surprised by anything but a denial.

## The other claims

- **relist-increment 0.10.** One distribution on the docket. Low-salience paid petitions are occasionally rescheduled or held over one conference, which counts as a further distribution under the harness's reading, so this is not zero, but no feature of this docket invites it.
- **cvsg-increment 0.01.** No federal party, no preserved federal question, pro se. Near the floor.
- **summary-disposition-route 0.30** (conditional on a grant). No intervening decision supports a GVR, and a summary reversal of a fact-bound unpublished state-law opinion is implausible, so I sit below the typical cert-order share of grants, but the only grant I can picture is a remand for a first look at the preemption question rather than plenary review.
- **dissent-from-denial 0.01** (conditional on denial). No Justice writes on petitions of this kind.
- **big_case_score 0.05.** The stakes are confined to the parties; the conceptual interest of QP 2 does not survive its waiver and the narrowness of the ruling below.

## Retrieval and its limits

I ran one corpus query for priors (`fedcourts query --court scotus --era 2020s --limit 6`); it returned a ranked set of recent SCOTUS rows that were not topically similar (the query surface takes no free-text or topic filter on SCOTUS rows), so it informed nothing beyond confirming the tooling works. Two CourtListener MCP searches for the Fifth Circuit opinion and docket (No. 25-30509) returned zero results, so my characterization of the opinion below rests on the petition's and BIO's quotations of it, which agree with each other on the points I rely on. I did not search for and did not encounter any disposition of this petition; the forward cell appears correctly provisioned (the October 9 conference postdates the snapshot).

## Where to discount me

My number is far below the band anchor, so if the Court does anything other than deny, my Brier loss is large. The main way I am wrong is a hold or reschedule that I am not seeing a reason for, which would move the relist claim rather than the disposition. I have not read the Fifth Circuit opinion itself, only the parties' accounts of it.
