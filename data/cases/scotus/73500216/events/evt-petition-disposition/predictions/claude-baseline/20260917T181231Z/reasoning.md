# Why P(grant) = 0.02

## What I read

Provisioned inputs: `record/snapshots/2026-09-17.json`, `record/context.json` (mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2025), `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (89 pages, not truncated, including the Fifth Circuit's unpublished per curiam opinion as Appendix A). `documents.json` lists no brief in opposition, and the docket confirms none exists. I also read the committed `metrics/statpack.md` cert sections and confirmed the live docket on supremecourt.gov (see `retrieval.md`); it matches the snapshot entry for entry.

## The docket state

Paid petition, docketed May 28, 2026 after one 30-day extension, from an unpublished Fifth Circuit per curiam (Elrod, C.J., Clement, Haynes) affirming denial of § 2254 relief. Response was due June 29, 2026; no waiver and no brief in opposition appear, no respondent counsel is listed, and the petition was distributed July 15 for the September 28, 2026 long conference. No response has been called for. The band is `baseline` and the salience version matches the statpack table, so the band table is my anchor.

## Anchor

Band `baseline`, bracketed `reached` rate, pooled over the Term rows strictly before 2025 that the table renders (OT2017 through OT2024): grants ≈ 593 over n ≈ 11,580, about **5.1%**. The relist-count cut's relist-0 bucket (denied 97.0%, granted 1.2%, gvr 0.5%) describes the terminal population most single-distribution paid petitions end in, and the CA5 originating-circuit cut (granted 1.6%, gvr 2.1%) is in the same neighborhood; both are shape, not the anchor.

## Adjustments from the anchor

Down, substantially:

1. **AEDPA vehicle defect.** The claim reaches the Court through § 2254(d)(1). The Fifth Circuit expressly assumed arguendo that implied bias is clearly established law and held the facts outside the "extreme" genre. The petition asks the Court to "announce a uniform standard," which is exactly what a federal habeas court cannot do under § 2254(d): relief requires an unreasonable application of law this Court has already clearly established, and the petition itself concedes the doctrine rests on a concurrence (Smith v. Phillips, O'Connor, J.) and that no court adopts the rule petitioner needs. The petition never engages AEDPA. This is the dominant factor.
2. **No response, no CFR.** The Court almost never grants without a response on file; a grant path requires a call for a response first, and the state's silence signals it saw no risk. The base-rate anchor pools petitions with and without responses, so this cuts below it.
3. **Split quality.** The asserted split is a disagreement over applying a totality standard, built largely on 1957–2007 decisions on direct review or pre-AEDPA habeas, with the petitioner conceding no per se rule anywhere. The Fifth Circuit's own precedent (Buckner, 2019) is consistent with the outcome, so the "internal inconsistency" claim is thin.
4. **Facts.** The juror volunteered her history and said she thought she could be fair; counsel did not hear the note; the claim is framed as Strickland prejudice, adding a second layer of deference. These are not the concealment-or-lying facts of the cases petitioner relies on.
5. Unpublished opinion below, single private counsel, no amici.

Up, modestly: the facts are sympathetic (same-type-crime victim, life without parole), the QP is cleanly stated, and a hold-and-GVR would become possible if the Court took an implied-bias case on direct review this Term, which I cannot rule out.

Net: about 0.02. That sits between the relist-0 terminal grant family (~1.7%) and a small allowance for a CFR-then-grant or hold-then-GVR path. Most of the residual mass is the GVR branch, which is why the conditional summary-disposition claim is 0.3 rather than lower.

## The other claims

- `relist-increment` 0.12: roughly 0.08–0.10 for a CFR (which produces a re-distribution once the BIO arrives) plus a few percent for a relist or reschedule from the long conference. The relist-count cut shows about a quarter of paid scored petitions ever see a second distribution, but that population includes petitions with responses on file; a no-response petition sits well below it.
- `cvsg-increment` 0.005: state criminal habeas, no federal party or federal statute.
- `summary-disposition-route` 0.3 (conditional on grant): no intervening decision exists today; the figure is the share of my grant mass that runs through a hold for a hypothetical other grant.
- `dissent-from-denial` 0.03 (conditional on denial): sympathetic facts, but AEDPA-bound with no response; written dissents from denial in this posture are uncommon.
- `big_case_score` 0.3: a decision setting the crime-victim implied-bias standard would matter across criminal trials, but the case is otherwise low-profile.

## Uncertainty and where to discount me

- I have not seen a brief in opposition because none exists; my read of the state's position is inference from its silence.
- I cannot see the Court's OT2026 grant list for any implied-bias case that would make a hold likely; if one is granted, the GVR branch is under-weighted here.
- The `fedcourts query` priors surfaced recency-ranked applications and unrelated cert dockets rather than juror-bias habeas priors, so the corpus pull contributed nothing case-specific; the anchor rests on the statpack alone.
- I did not read the prior claude-baseline run's output for this event, so this forecast is independent of it.
