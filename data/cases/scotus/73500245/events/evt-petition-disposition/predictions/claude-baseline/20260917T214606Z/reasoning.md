# Rationale — claude-baseline on scotus/73500245 (evt-petition-disposition), run 20260917T214606Z

**P(grant) = 0.008. Predicted disposition: denied.**

## What I read

- Stable inputs: `AGENTS.md`, `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and the committed `metrics/statpack.md` (with `metrics/statpack.json` for one originating-court bucket).
- Event: `event.yaml` (kind `petition`, no `stage` recorded, so it reads as **cert**, moment distribution; opened 2026-06-02).
- Snapshot: `record/snapshots/2026-09-17.json` (the file `context.json`'s `snapshot_date` names). Three docket entries: petition filed May 25, 2026 (paid); respondent Alabama State Bar waived its right to respond July 1, 2026; distributed July 8, 2026 for the conference of September 28, 2026. No relist, no CVSG, no amici, no related cases.
- Context: mode `forward`, `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, `cutoff: null`. No `DECIDED_BEFORE` clock in the environment.
- Documents: `petition.txt` (12 pages, `empty_text: false`, not OCR-derived) and `questions-presented.txt` (one QP, cleanly cut). No brief in opposition exists because the respondent waived.

## The case

The petitioner is an Alabama attorney, representing himself, who was publicly reprimanded and suspended for 180 days for violating Alabama's communication (Rule 1.4) and excessive-fee (Rule 1.5) rules after he tried, post-settlement, to raise his contingent fee from about $31,000 to about $120,000 and held the client's settlement funds pending her agreement. The Alabama Supreme Court affirmed per curiam on December 19, 2025 and denied rehearing February 27, 2026. The petition's single question asserts that the state court's interpretation of Ala. Code § 34-3-62 (a court-supervised fee-dispute procedure that shields an attorney from discipline "therefor") and its application to him violated procedural due process, relying on *Marks v. United States*, 430 U.S. 188 (1977), and an Alabama case, *Brooks v. Alabama State Bar*, that applied *Marks* to bar discipline.

I read the Alabama Supreme Court opinion on CourtListener (cluster 10761703, published). It matters in three ways. First, the court held § 34-3-62 inapplicable because the Bar prosecuted communication and fee violations, not wrongful retention of funds, so the statute never promised the petitioner what he says he relied on. Second, the court treated the reliance argument entirely as a *Brooks* question under state law and found *Brooks* distinguishable because the petitioner had relied on no caselaw and had not actually invoked the statute at the time; the opinion never analyzes the Fourteenth Amendment as such, and the petition itself says the federal due-process theory first appeared in the petitioner's reply brief below. Preservation of a federal question is therefore doubtful. Third, five of the seven participating justices concurred only in the result, which signals disagreement about reasoning but nothing that helps a cert petition.

Substantively, the *Marks*/*Bouie* fair-notice doctrine concerns unforeseeable judicial enlargement of a criminal statute; extending it to a first-time interpretation of a civil fee-dispute procedure in a lawyer-discipline case, where the state court also found no actual reliance, has no support in this Court's cases and no split behind it. The petition's argument section runs roughly two pages and cites two cases. There are no amici, and the respondent waived.

## Anchor and adjustments

The cert-stage anchor for a `baseline`-band cell is the "Segment base rate by salience band (sal-v4)" table's bracketed **reached** rate for `baseline`, pooled over Terms strictly before this case's Term (2025), which is the eight rendered rows OT2017–OT2024. Pooling the weighted counts gives about 593 grants over n = 11,580, roughly **5.1%**. That figure is the yardstick the evaluator scores my skill against, and it is the rate for every private paid petition that ever sat in `baseline`, most of which have far more going for them than this one.

Adjustments, all downward:

- **No federal question cleanly presented, and preservation doubtful.** The QP asks the Court to review a state court's reading of a state statute; the federal hook is a reply-brief afterthought the state court did not address as federal law.
- **No split, no importance, no institutional stakes.** Nothing in the petition claims a conflict among courts; the issue is one attorney's discipline.
- **Self-represented petitioner, waived response.** The Bar did not think the petition worth answering, and the absence of a BIO removes the one channel through which the Court usually learns a petition is serious. A call for a response is possible but rare for petitions of this shape.
- **Originating court.** The statpack's originating-court cut records 29 resolved petitions from the Supreme Court of Alabama with one grant (about 3.4%, a thin bucket, and the single grant is not from the discipline context). It neither adds nor subtracts much beyond the band anchor.
- **Doctrinal weakness.** The state court's alternative holding (statute inapplicable to these charges) means even a favorable *Marks* ruling would not necessarily disturb the discipline, so the vehicle is poor even on its own terms.

The relist-count cut (paid scored segment, relist bucket 0: granted 1.2%, gvr 0.5%) describes petitions that ended undistributed a second time; my cell is forward from a single distribution, so I read it for shape only. I land at **0.8%**, about a sixth of the band anchor and roughly the `baseline` terminal rate (0.6%–1.8% across Terms), because this petition sits at the very bottom of the baseline population: it is the kind of paid petition that is denied on the first order list. I do not go lower because the Court occasionally takes an interest in lawyer-discipline due-process claims, and a paid petition from an attorney is not quite an IFP prisoner filing.

## The other declared claims

- **relist-increment 0.12.** Distributed once, for the long conference. Roughly a quarter of `baseline` petitions eventually leave the band (the reached-minus-terminal gap in the sal-v4 table), but that gap is driven by petitions with responses filed, amici, or a serious QP, and the `dist-v2` count also picks up reschedules before first consideration. For a waived, self-represented petition at the long conference, I put one further distribution at 12%: mostly the chance of a reschedule or of a Justice requesting a response.
- **cvsg-increment 0.003.** No federal interest of any kind. Essentially zero.
- **summary-disposition-route 0.6.** Conditional on a grant. The prior-Term cert-order share of the grant family runs roughly 37%–59% in the Terms where the gvr label is populated (OT2017–OT2022; OT2023–OT2024 carry zero GVRs as an ingestion artifact). For this petition there is no split to argue, so if the Court ever granted it would more likely be a summary per curiam or a GVR than plenary review. I put it above the population share.
- **dissent-from-denial 0.01.** No Justice has a stake in this issue; no amici; no response. A statement respecting denial in a self-represented attorney-discipline petition is close to unheard of.

## big_case_score

0.03. The stakes are one lawyer's six-month suspension. Whatever the disposition, the case has no reach.

## Uncertainty and where to discount me

- The band anchor is a population rate; my adjustment below it rests on a qualitative read of a short petition and the opinion below, not on a measured cut for "self-represented attorney, response waived." If the Court is more generous to weak paid petitions than I think, 0.8% is too low, but the proper-scoring cost of that error is small against the cost of writing 5% on a petition I believe has almost no chance.
- I did not run a `--full` corpus hydrate on any prior; the one `fedcourts query` I ran returned recent denials for context and did not shape the number.
- Mode is `forward`; nothing I retrieved postdates the snapshot or concerns this petition's disposition, which cannot exist before September 28, 2026. The CourtListener docket search for 25-1344 returned nothing, so CourtListener does not yet carry this SCOTUS docket. I also confirmed the petitioner's related § 1983 suit against the Alabama justices and bar officials (M.D. Ala. 2:26-cv-00133, filed March 1, 2026, still open); I read it only as posture, not as evidence about cert.
- The petition's jurisdiction section misdates the state decision as December 19, 2026; the docket and the opinion confirm 2025. Harmless, but of a piece with the petition's overall quality.
