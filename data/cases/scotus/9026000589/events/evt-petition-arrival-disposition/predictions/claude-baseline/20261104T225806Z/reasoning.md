# Reasoning — Zeldin v. Climate United Fund, No. 26-589 (arrival moment)

**P(grant family) = 0.85.**

## Inputs read
- Snapshot `record/snapshots/2026-11-05.json`: a paid petition docketed Nov 4, 2026, filed Nov 2 by the Solicitor General (D. John Sauer) for the EPA Administrator. Response due Dec 4, 2026. No distributions yet (count 0), no CVSG. Those absences are what an arrival cell is.
- `record/context.json`: forward mode, band `federal` (sal-v6), `cert_anchor.rate` = 0.734 pooled over 10 prior Terms.
- `questions-presented.txt`: (1) whether the Tucker Act keeps respondents from challenging EPA's grant terminations in district court; (2) whether a claim under the now-repealed GGRF statute (42 U.S.C. 7434) can support the injunction.
- `decision-below.txt`: the en banc D.C. Circuit's per curiam judgment of Aug 4, 2026 (Henderson not participating). Six judges voted to affirm paragraph two of the PI on the IRA §60103 theory; four (Srinivasan, Katsas, Rao, Walker) would vacate it in light of the OBBBA repeal. The rest of the PI was affirmed by an equally divided court. The panel (Rao, Katsas; Pillard dissenting) had reversed. `lower-court-docket.txt` matches this.
- `petition.txt` (truncated at cap; I read the introduction and the reasons for granting). The SG argues the case is the merits-docket vehicle for the Tucker Act question the Court addressed on stay applications in *Department of Education v. California* and *NIH v. APHA*. It cites a division among lower courts (Fourth Circuit *Solutions in Hometown Connections*, First and Ninth Circuit decisions on one side; the D.C. Circuit and several district courts on the other) and $16B at stake. It notes respondents consented to an administrative stay pending this Court's disposition.
- `same-question.json`: empty list (nothing over the 0.5 threshold).

## Anchor and adjustments
- Anchor: the federal-class reached rate, 0.734, from the frozen `cert_anchor`. Per-Term rows run from 47.6% to 96.2%, with n between 12 and 41 per Term.
- Up: an SG petition with very high fiscal stakes ($16B, "the largest pending grant-termination case"). The en banc court split sharply and affirmed in large part by an equally divided vote, so there is no controlling rationale below. The issue is one this Court has already engaged twice on its interim docket and on which lower courts have pushed back. The second QP, on the effect of the repeal, reaches dozens of repealed programs.
- Down: the posture is interlocutory (a preliminary injunction). The SG also has a parallel Tucker Act petition, *Trump v. Thakur*, No. 26-210, distributed for the Nov 13, 2026 conference. The Court could take Thakur and hold this case, then GVR it. That still counts as a grant, but it is why `summary-disposition-route` is 0.15. A hold followed by a denial is also possible if Thakur resolves the issue for respondents. Some respondent-side mootness or settlement risk.
- Net: 0.85.

## Claims
- relist-increment 0.97: the petition will almost certainly be distributed at least once (the response or waiver comes Dec 4 or after an extension). The remaining risk is withdrawal or settlement.
- cvsg-increment 0.01: the United States is the petitioner.
- dissent-from-denial 0.5 (conditional on denial): a denial of an SG petition this large, after *California* and *NIH*, would likely draw a writing from Alito, Thomas or Gorsuch.

## Uncertainty
The petition text was truncated, and I did not read the respondents' side, since no BIO exists yet. Thakur's fate is the main unknown.
