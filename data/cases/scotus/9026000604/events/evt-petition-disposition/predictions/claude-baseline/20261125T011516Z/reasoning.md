# Reasoning — Eta v. United States, No. 26-604 (cert, distribution moment)

**P(any grant) = 0.11; label `denied`.**

## What I read
- Snapshot `2026-11-25.json`: petition filed Nov 4, 2026 (Jones Day); the United States waived its response Nov 17; distributed once, for the Conference of Dec 11, 2026. No amicus briefs, no CVSG, no call for a response yet.
- `questions-presented.txt`, `petition.txt` (full, not truncated) and `appendix.txt` (the Seventh Circuit opinion, St. Eve, J., joined by Scudder and Kolar). No brief in opposition exists (waiver), so I have only the petitioner's account of the split.
- `context.json`: band `baseline` (sal-v9), `cert_anchor.rate` 0.0518, amicus line (arm `none`) 0.0269. `same-question.json` lists no matches.
- Beyond the record (forward mode): the corpus row and the Court's live docket page for *Anibowei v. Blanche*, No. 26-208, which the petition itself names as a pending petition on the same issue.

## Anchor and adjustments
Anchor: the frozen `cert_anchor.rate` of about 5.2% (baseline band, reached, ten prior Terms). The statpack's band table is headed sal-v8 while my context is sal-v9; the fallback for a private petitioner is the baseline floor anyway, which is the same column, so the anchor is unaffected (flagged as info). The no-amicus line (2.7%) and the relist-0 terminal figure are floors, not my state.

Upward:
- The question (what, if anything, must justify a warrantless phone search at the border) is a real, acknowledged, multi-circuit conflict. The petition cites the Solicitor General's own 2021 description of it as an entrenched conflict (the government's petition in *Cano*), and a September 2026 Second Circuit decision adds to it.
- The Court has already shown interest in the issue this Term: in *Anibowei* (No. 26-208, CA5, a civil facial challenge to the CBP/ICE directives, ten cert-stage amicus briefs) the government waived, the petition was distributed for Oct 9, and the Court requested a response on Sept 29; that response is now due Nov 30. This is the decisive fact for my relist number and the main reason I sit above the anchor.
- Experienced Supreme Court counsel; a clean concession below that the search served no customs, contraband or admissibility purpose.

Downward:
- The Court denied this question repeatedly in 2021 (*Cano*, *Merchant*, and others), including when the government itself asked. A call for a response is a low bar and most such petitions are still denied.
- Vehicle: the Seventh Circuit held in the alternative that the good-faith exception bars suppression, and added that the petitioner would lose even under case-by-case review because the crime was transnational. The district court also found reasonable suspicion and inevitable discovery. The petition's answer (the Court granted in *Chatrie* despite a good-faith holding) is fair but does not remove the problem; *Anibowei*, being civil, has no exclusionary-rule obstacle and is the more natural lead vehicle. I did not verify the petition's description of *Chatrie*.
- No amicus support on this docket, and the government thought it not worth a response.

## How the number is built
Roughly: P(the Court takes the border phone-search question this Term via either petition) about 0.22. Given that, Eta is either granted alongside (about 0.3) or held and later GVR'd if the petitioner side prevails in the lead case and the Court does not treat the good-faith holding as independently dispositive (about 0.6 held x 0.5 x 0.6). That gives about 0.10, plus a small chance Eta is taken alone, for 0.11. A GVR counts as a grant, which is why the summary-route share conditional on a grant is high (0.40).

## Other claims
- `relist-increment` 0.82: with a response already requested in *Anibowei*, I expect the Court either to call for a response here (which forces a later redistribution) or to hold this petition for *Anibowei* (redistributed once the lead is resolved). The residual is an outright denial on the Dec 14 order list.
- `cvsg-increment` 0.01: the United States is the respondent.
- `dissent-from-denial` 0.06 conditional on denial: Justices Gorsuch and Sotomayor are the plausible writers on digital-privacy denials, but any writing would more likely attach to the lead petition.

## Where to discount me
My estimate of the Court's appetite for the issue is judgement, not a committed rate. I have not seen the government's *Anibowei* response (not yet filed). If the Court denies *Anibowei*, this petition almost certainly falls with it.
