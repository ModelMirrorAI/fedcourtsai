# Chaganti v. Cincinnati Insurance Company, No. 25-1291 — cert disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.003.**

## The case

Petitioner Naren Chaganti, an attorney proceeding pro se, held a property and
business-interruption policy from Cincinnati Insurance; the insured property was
damaged in 2010. He sued for breach of contract in March 2024 — roughly fourteen
years after accrual. Ohio's 2012 amendment to O.R.C. § 2305.06 (S.B. 224)
shortened the contract limitations period from fifteen years to eight, and an
uncodified section of S.B. 224 gave pre-2012 accrued claims eight years from the
act's effective date (i.e., until September 2020). The trial court dismissed the
suit as time-barred, the Ohio Tenth District affirmed (2025-Ohio-1982), and the
Supreme Court of Ohio declined discretionary review on September 30, 2025.

The single question presented: whether a state may rely on an *uncodified*
session-law provision to apply a shortened limitations period retroactively,
consistent with due-process notice requirements.

## Why this petition fails every cert-worthiness screen

1. **No split of authority.** The petition alleges no conflict among federal
   circuits or state courts of last resort on the federal question. The only
   "confusion" cited is intra-Ohio: one Eighth District intermediate decision
   (*Tabbaa*) and a footnote in an S.D. Ohio case. An intra-state conflict over
   the meaning of a state session law is for the Supreme Court of Ohio — which
   declined the case — not for certiorari.

2. **The merits theory runs into the petitioner's own concessions and settled
   precedent.** The petition concedes S.B. 224 shows clear retroactive intent
   and concedes the eight-year grace period satisfies the "reasonable time"
   requirement of *Terry v. Anderson* and *Wilson v. Iseminger*. What remains is
   the claim that *codification* — not enactment and publication — is what due
   process requires. *Texaco, Inc. v. Short*, 454 U.S. 516, 532 (1982), which
   the petition itself quotes, says the opposite: "generally, a legislature need
   do nothing more than enact and publish the law, and afford the citizenry a
   reasonable opportunity to familiarize itself with its terms." A duly enacted
   session law is published law; no authority holds the Due Process Clause
   requires placement in a compiled code. The claim is at bottom a disagreement
   with how Ohio courts read Ohio's own publication and retroactivity statutes —
   a state-law question dressed in due-process language.

3. **Vehicle and posture.** Pro se paid petition from a state *intermediate*
   appellate court (the Ohio Supreme Court's discretionary decline leaves the
   Tenth District as the final merits word); a 16-page petition; no amici; a
   fact-bound application to one litigant's fourteen-year-old insurance claim.
   CourtListener shows the petitioner is a frequent litigant across many federal
   fora, which is consistent with the serial-petition profile the Court denies
   without comment.

4. **Docket signals.** Docketed May 19, 2026; distributed July 1, 2026 for the
   September 28, 2026 conference — the summer "long conference," where the grant
   rate is at its annual low. No response on file as of the snapshot (response
   was due June 18, 2026, so respondent has evidently waived), no CVSG, no
   relists, no amicus support. Petitions denied out of the long conference
   without a requested response are the modal outcome for filings like this one.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted): modern
discretionary-cert petitions run ~3% granted overall; paid petitions ~5.4%
(Term 2025) to ~6.9% (Term 2024); the 0-relist bucket runs 0.8% granted; no
CVSG ~3.0%. State intermediate-court petitions in the corpus slice are
essentially never granted (e.g., Court of Appeals of Michigan 12/12 denied,
Illinois First District 10/10 denied). This petition sits in the worst cell of
every cut: paid but pro se, state intermediate court, zero relists so far, no
CVSG, no split, weak merits theory contradicted by the petitioner's own leading
authority. Starting from the 0-relist base (~0.8%) and adjusting down for the
state-court origin, pro se status, and absence of any split or amicus interest,
I set **P(grant) = 0.003**, which still leaves room for the tail scenario of a
relist-driven surprise. A GVR is implausible — no intervening decision of this
Court touches the question — so the 0.003 is nearly all plenary-grant tail.

**Disposition: denied** (dismissal/withdrawal is rarer still for a completed,
distributed paid petition). No vote prediction: a denial produces no recorded
votes, and nothing here suggests a dissent from denial.

## Big-case score

0.03. A one-party insurance limitations dispute; even if granted, the resulting
rule (codification vs. session-law publication for notice) would be narrow.
Denial will be noticed by no one beyond the parties.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket entries, fee class,
  distribution).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (full 16-page petition text; the QP and the concessions in Parts D–E drive the
  merits assessment). No brief in opposition was provisioned — consistent with
  the docket showing no response filed; treated as a likely waiver, not missing
  data.
- `metrics/statpack.md` / `statpack.json` base rates; one `fedcourts query` for
  recent resolved SCOTUS priors; two CourtListener MCP searches (petitioner's
  litigation history; no outcome-revealing material for this case was sought or
  surfaced — the case is pending, mode `forward`).
