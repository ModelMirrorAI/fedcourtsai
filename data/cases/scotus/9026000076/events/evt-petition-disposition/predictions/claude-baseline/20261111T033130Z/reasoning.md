# Reasoning — Jackson v. Florida, No. 26-76 (capital)

**P(grant) = 0.16; predicted disposition: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-11-11.json`, `record/context.json` (mode `forward`, band `baseline`, `distribution_count` 1, no CVSG, `cert_anchor.rate` 0.0516 under sal-v8).
- `record/documents/`: the questions presented, petition, appendix, brief in opposition and cert reply. None was truncated or OCR-derived.
- `record/related/26-78.json` (Hunt v. Florida). Its relation is `vided-amicus` with one shared brief, from the Legal Scholars and Historians, marked VIDED on both dockets.
- The live supremecourt.gov docket for 26-76: no entries after Aug 28, 2026, which matches the snapshot.

## Anchor
The baseline band's pooled reached rate is **5.2%** (`cert_anchor`). That is consistent with the statpack's baseline-band reached rates of 4–6% across OT2017–OT2025. As a shape check, the capital-case cut is 8.6% granted and 5.2% GVR (n=174 resolved). The cut for 2+ amicus briefs is 18.2% granted (n=1446).

## Adjustments up
- **The docket's posture.** The petition was distributed on Aug 26 for the long conference (9/28) and **rescheduled two days later**, before the conference sat. It has not been redistributed in the ten weeks since. The likeliest reading is that the Court is holding it to be considered alongside the companion petition, Hunt v. Florida (26-78). Hunt has the same counsel (Fisher) and the same 8-4 issue. Florida's opposition there was filed Oct 29 after three extensions. Even a hold-for-companion reschedule shows the Court means to treat the two together rather than deny Jackson at the long conference by routine. Reschedules before a first conference also correlate with closer interest. The relist cut's 1+ buckets (8–28% granted) overstate this, because they include true relists.
- **The question.** This is the first petition against Florida's 2023 statute, which allows a death sentence on an 8-4 jury recommendation, the lowest threshold in the nation. The question runs through Ramos (unanimity), Hurst and Erlinger. Ramos's Sixth Amendment majority included Gorsuch, Kavanaugh and Thomas, so four votes to grant are plausible: Sotomayor, Kagan and Jackson, plus Gorsuch. The case is recurring and high-volume in Florida.
- **Counsel and amici.** Petitioner is represented by the Stanford clinic (Fisher, Fletcher) and the ACLU. Three amicus briefs were filed, including one by Waxman.

## Adjustments down
- **No live split.** The split is 2-2 at most, and Florida's opposition is right that both conflicting states (Delaware and Connecticut) have since abolished the death penalty, and that their decisions predate McKinney.
- **Prior denials.** The Court has denied a long line of "death recommendation is an element" petitions, including Alabama's 10-2 cases and McKenzie in 2022.
- **The merits.** Under McKinney and Spaziano the current majority is unlikely to hold that the weighing or selection step is an element. Florida's argument that a win would be pyrrhic (the legislature could remove the jury's role altogether) gives the Court a further reason not to take the case.
- **The disposition.** The likeliest outcome is a denial with a written dissent.

On balance I move from 5% to about 16%. My main uncertainty is what the reschedule means. If it reflects a Justice's interest in granting rather than coordination with Hunt, the number should be higher. If it is clerical, it is too high.

## Claims
- **relist-increment 0.97.** The snapshot shows one distribution, followed by a reschedule. The petition cannot be disposed of without a new distribution, which is expected once Hunt's reply is in (around mid-November).
- **cvsg-increment 0.01.** This is a state criminal case with no federal interest.
- **summary-disposition-route 0.04.** No intervening decision would support a GVR.
- **dissent-from-denial 0.5.** Sotomayor and Jackson have written on capital jury issues before, and a capital denial after a reschedule often carries a writing.

## Retrieval
The corpus query and the 26-78 lookup were used only for context. One web search confirmed the Florida Supreme Court's decision of Dec 18, 2025 below. No search reported this petition as decided.
