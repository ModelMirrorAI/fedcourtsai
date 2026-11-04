# Reasoning — Jack v. Whateley, No. 26-584 (arrival moment)

**P(grant) = 0.20.**

## Inputs read
- Snapshot `record/snapshots/2026-11-04.json`: paid petition docketed Nov. 3, 2026 (filed Oct. 29), response due Dec. 3, 2026; zero distributions, no CVSG. Petitioner is the Virginia DMV Commissioner, represented by the Virginia Solicitor General's office.
- `record/context.json`: forward mode, band `state` (sal-v6), `cert_anchor.rate` = 0.235 (state class's reached rate pooled over the 10 prior Terms).
- `questions-presented.txt`, `petition.txt`, `decision-below.txt` (CA4, published, Harris J. for a unanimous panel with Agee and Keenan; vacated and remanded), `lower-court-docket.txt` (no rehearing en banc petition), `appendix.txt` (listed; not read in full — it reproduces the opinions).
- `same-question.json`: no petition above threshold.

## Anchor
State-petitioner arrival floor: 0.235 (cert_anchor). Per-Term state reached rates over OT2017–OT2025 range ~14–39%.

## Adjustments
Up:
- A genuine, acknowledged split: CA4 (and Maryland's high court in *Mitchell*) hold personalized plate characters are private speech; Tennessee (*Gilliam*, 2025) and Indiana (*Vawter*) supreme courts hold they are government speech. *Walker* expressly reserved the question. A federal court of appeals now conflicts with state courts of last resort — a classic Rule 10(a) posture.
- State petitioner with SG-office counsel; the Court tends to take states' petitions where a federal court has constrained a statewide program.

Down:
- **Interlocutory posture.** CA4 vacated a Rule 12 dismissal and remanded for forum analysis. The petition argues hard that the question is fully resolved (citing *Hosanna-Tabor*, *Mount Lemmon*), but the Court frequently denies non-final petitions, and the petition's own anticipation of *Abbott v. Veasey* / *VMI* statements shows the risk.
- **The Court denied the same question last Term**: *Gilliam v. Gerregano*, No. 25-107, denied Dec. 8, 2025 (corpus row: 2 distributions, five amicus filers), apparently without noted dissent. The difference now is the federal-circuit side of the split, which the Tennessee BIO had emphasized was missing — a real change, but the Court passed on a well-supported vehicle a year ago.
- **Seventh Circuit pending** (*M J Nichols Co. v. Boardman*, argued Sept. 17, 2026): the Court may prefer to wait for it, or for a final judgment here.
- Practical stakes are modest (offensive vanity-plate screening).

Net: roughly at or slightly under the state anchor — 0.20.

## Claims
- relist-increment 0.96: from zero distributions, the petition will almost certainly be distributed at least once (only withdrawal/dismissal avoids it).
- cvsg-increment 0.04: the government is the petitioner (a state), and no federal program is implicated; CVSGs in state-petitioner cases are uncommon.
- summary-disposition-route 0.06 (conditional on grant): no intervening decision suggests a GVR; a grant would be plenary.
- dissent-from-denial 0.10 (conditional on denial): *Gilliam* drew no noted writing; Alito (author of the *Walker* dissent) or Thomas are the plausible writers, but a denial on interlocutory grounds rarely draws one.

## Uncertainty
The main uncertainty is whether the Court treats the interlocutory posture as disqualifying, and whether it waits for CA7. I did not use the CourtListener MCP or web search; the forecast rests on the provisioned record, the statpack and two corpus queries.
