# Predictor Rationale (`scotus/9526000560` / `evt-motion-disposition`)

## Summary of Forecast

- **`granted`**: `1` (`predicted_disposition`: `"granted"`)
- **`probability` (`interim-disposition`)**: `0.82`
- **`response-requested-increment`**: `0.99`
- **`referral-increment`**: `0.96`
- **`amicus-increment`**: `0.85`
- **`big_case_score`**: `0.78`

## 1. Provisioned Inputs and Conditioning State

I read the provisioned snapshot `data/cases/scotus/9526000560/record/snapshots/2026-10-21.json` (`input_snapshot: "2026-10-21.json"`), `record/context.json`, `record/documents/documents.json`, and the full text of the Solicitor General's emergency stay application in `record/documents/application.txt` (39 pages, `ocr_derived: false`, `truncated: false`).

Per `record/context.json`, this is a `forward`-mode interim cell at `moment: arrival` (`cut_kind: "arrival-position"`, `cut_anchor_index: 0`, `cutoff: "2026-10-22"`, `term: 2026`). At the arrival snapshot (`2026-10-21`), `signals_observable` is `true`, `band` is `null` (normal for an interim application), `response_requested` is `false`, `referred_to_court` is `false`, and `amicus_briefs` is `0`.

Because this cell runs in `forward` mode, I also queried the corpus for the open application row (`scotus/9526000560`) and retrieved the underlying Western District of Texas docket (`3:26-cv-01099-KC`) via the CourtListener MCP server, reading Judge Kathleen Cardone's October 14, 2026 Memorandum Opinion (ECF No. 75), Plaintiffs' October 20, 2026 Opposition to Defendants' Motion to Stay (ECF No. 77 & 77-1), and Judge Cardone's October 20/21, 2026 Order Denying Motion to Stay Preliminary Injunction (ECF No. 78).

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

Following the interim-stage anchoring rules, I anchored on **"The interim docket (applications)"** section of `metrics/statpack.md`, pooling `substantive_granted` over `substantive_resolved` across the ten application-Terms strictly preceding `term: 2026` (`2016 <= T < 2026`):

- **OT2025**: `25` granted / `148` resolved (`16.9%`, `1` unparsed)
- **OT2024**: `23` granted / `113` resolved (`20.4%`, `0` unparsed)
- **Strictly-prior pooled substantive base rate**: `48 / 261 = 18.39%` (`0.184`). This clears the pre-registered `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor (`261 >= 50`). (The section caption in `metrics/statpack.md` still refers to the table as "descriptive only — no skill score is computed against it," predating the caption rewrite noted in the prompt instructions; the strictly-prior pool arithmetic is identical.)

Two structural cautions apply to this `18.4%` raw substantive base rate:
1. The raw substantive slice (`n=315` total across the pack, `265` resolved) is dominated by private and pro se emergency applications that are summarily denied without a response request (`response_requested` fires on `118 / 315 = 37.5%`, `referred_to_court` on `81 / 315 = 25.7%`, and `amicus_briefs >= 1` on `55 / 315 = 17.5%`).
2. When the **Solicitor General** seeks an emergency stay of a lower-court injunction blocking an Executive Branch policy or federal construction project, the grant rate is severalfold higher than the unconditioned pool. Across the six resolved OT2026 Solicitor General substantive stay applications retrieved from the corpus (`26A124` *Trump v. California*, `26A203` *National Park Service v. National Trust for Historic Preservation*, `26A308` *DHS v. League of Women Voters*, `26A406` *DHS v. D.V.D.*, `26A416` *Trump v. Kingdom*, and `26A476` *FCC v. Brown*), **5 of 6 (`83.3%`)** resolved as unqualified `granted` (`26A416` was denied on October 21, 2026).

## 3. Case-Specific Adjustments (`P(unqualified grant) = 0.82`)

Starting from the `18.4%` overall substantive interim base rate and the `~83%` empirical OT2026 Solicitor General substantive stay rate, several features strongly support an unqualified stay grant here:

1. **Direct and Exclusive Certiorari Jurisdiction (`IIRIRA § 102(c)(2)(C)`)**:
   Unlike ordinary preliminary injunctions reviewable as of right in a court of appeals under 28 U.S.C. § 1292(a)(1), IIRIRA § 102(c)(2)(C) strips the courts of appeals of jurisdiction and provides that an interlocutory or final district court order or decree may be reviewed *only* by writ of certiorari in the Supreme Court. If the Supreme Court were to deny review, a single district judge's preliminary injunction halting $2.6 billion in border-wall contracts across a 510-mile sector would evade appellate review entirely. That posture makes the "fair prospect of certiorari" prong exceptionally strong.

2. **Substantial Likelihood of Reversal on the Threshold Statutory/Constitutional Question (`IIRIRA § 102(c)(2)(A)`)**:
   IIRIRA § 102(c)(2)(A) bars any cause of action or claim challenging a waiver determination unless it alleges "a violation of the Constitution." In her October 14, 2026 Memorandum Opinion (ECF No. 75), Judge Cardone declined to reach Plaintiffs' Article I nondelegation claim and instead rested the preliminary injunction exclusively on the ground that the "major questions doctrine" is a standalone constitutional cause of action and that IIRIRA § 102(a) does not clearly authorize waiving laws across the Big Bend Sector because that sector has lower illegal-entry apprehension counts (`~3,600–6,500/year`) than neighboring sectors.
   - A majority of the Court is very likely to reject the characterization of the major questions doctrine as an independent constitutional cause of action that circumvents § 102(c)(2)(A)'s bar on statutory/ultra vires claims. Even Justice Gorsuch's concurrence in *Learning Resources, Inc. v. Trump*, 607 U.S. 229 (2026), describes the major questions doctrine as a clear-statement rule of statutory interpretation serving Article I values, and here § 102(c)(2)(A) forecloses statutory-authority challenges.
   - Even if the Court reaches the underlying statutory or nondelegation question, IIRIRA § 102(a)–(c) (as amended by the Secure Fence Act of 2006 and the Consolidated Appropriations Act of 2008) expressly authorizes the Secretary to construct physical barriers and roads in the vicinity of the border to achieve "operational control" (defined in § 102(b)(1)(B) as the prevention of *all* unlawful entries into the United States) and commits waiver determinations to the Secretary's "sole discretion," backed by Congress's July 2025 appropriation of $46.5 billion in the One Big Beautiful Bill Act for border-barrier construction.

3. **Remedial Overbreadth (`Trump v. CASA, Inc.`) and Balance of Equities (`Trump v. Sierra Club`)**:
   Judge Cardone's injunction bars all border-barrier construction and ground-disturbing activities across the entire 510-mile Big Bend Sector, even though Plaintiffs' concrete property, historical, and recreational interests (such as the adobe Ruidosa Church near FM 170, Chinati Hot Springs, Guerra-Addington's property in Hudspeth County, and discrete stretches of the Rio Grande in Big Bend National Park) span only parts of the sector. Under *Trump v. CASA, Inc.*, 606 U.S. 831 (2025), preliminary injunctive relief cannot sweep beyond what is necessary to remedy the specific injuries of the plaintiffs with standing. Moreover, in both *Trump v. Sierra Club*, 588 U.S. 930 (2019), and *National Park Service v. National Trust for Historic Preservation*, No. 26A203 (Aug. 31, 2026), the Court stayed injunctions against federal construction projects after concluding that government operational and contract-suspension harms outweighed aesthetic and environmental harms during litigation.

4. **Downward Adjustments and Unqualified-Grant Resolution Risk (`0.18` complement)**:
   I temper the probability at `0.82` (rather than `>0.90`) for two reasons:
   - **Pre-registered mixed-order collapse**: The interim outcome resolver matches denial language first, so any order that reads "granted in part and denied in part" — for instance, if the Court were to stay the sector-wide injunction except as applied to construction immediately adjacent to the historic Ruidosa Church or specific plaintiff properties — resolves as `denied` (`granted = 0`).
   - **Evidentiary record friction below**: As Judge Cardone highlighted in her October 20/21 Order Denying Stay (ECF No. 78) and Plaintiffs detailed in their opposition (ECF No. 77), the government called zero witnesses at the five-hour October 2 evidentiary hearing, attempted to introduce new contract-cost declarations (`$850,000/day`) only on its stay motion while refusing to produce the underlying contracts, and had previously paused construction voluntarily in Big Bend National Park (`BBT-2` and `BBT-4`). While these record defects are unlikely to prevent a stay given IIRIRA § 102(c)'s jurisdictional bar and *CASA*, they create a modest (`~15–18%`) combined chance of either an outright stay denial (as in `26A416` *Trump v. Kingdom*) or a tailored partial stay that resolves as `denied` under the binary collapse rule.

## 4. Rationale for the Escalation-Ladder Claims (`interim-v1`)

- **`response-requested-increment` (`0.99`)**: At the provisioned arrival baseline (`2026-10-21.json`), `response_requested` is `false`. Live forward corpus retrieval (`scotus/9526000560`, polled `2026-10-23`) shows that the Court/Circuit Justice requested a response on `2026-10-22` (`response_requested: true`). Because the escalation signals are monotone and `Outcome.interim_signals` resolves against the frozen arrival context (`false`), this increment is virtually certain (`0.99`) to resolve true.
- **`referral-increment` (`0.96`)**: Major Solicitor General stay applications on the emergency docket are routinely referred by the Circuit Justice to the full Court once the response is in (`6/6` resolved OT2026 SG substantive stay applications in the corpus had `referred_to_court: true`).
- **`amicus-increment` (`0.85`)**: All six resolved OT2026 SG substantive stay applications in the corpus drew at least one amicus brief (`1` to `13` briefs). Given the salience of border-wall construction in Big Bend National Park and the major questions doctrine, at least one amicus submission (`amicus curiae` or "Amicus brief of X submitted.") is very likely (`0.85`) to be docketed before disposition.
