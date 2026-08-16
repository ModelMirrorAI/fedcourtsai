# Rationale for the numbers

**P(grant family) = 0.20.** Anchor first: this is an arrival-moment cert cell
(`moment: arrival`, distribution count 0, no CVSG), frozen band `baseline`
under `sal-v3`, which matches the committed statpack's band-table version.
Per the arrival rule I anchor on the weakest band's bracketed `reached` rate —
the whole paid scored segment, unconditional on trajectory. Pooling the
baseline column's bracketed figures over Terms strictly before 2026
(2017–2025): weighted grants ≈ 862 over n ≈ 13,163, i.e. **~6.6%**. The
petitioner is private (insurers), so the federal-band arrival note does not
apply.

I adjust up to 0.20 — a large move, driven by one structural fact: this is a
paid, expertly-counseled companion petition whose only ask is a hold pending
*Town of Vinton* (No. 25-1383), which presents an entrenched, acknowledged,
outcome-determinative 4–1 circuit split (CA1/CA2/CA4/CA9 vs. CA5) on a
question *GE Energy* (590 U.S. 432, 445) expressly reserved, in a
high-frequency litigation line (Louisiana hurricane surplus-lines coverage).
The decision below rests entirely on *Vinton* ("no meaningful difference"),
so this docket's fate is a near-deterministic function of *Vinton*'s. My
decomposition: P(*Vinton* grant family) ≈ 0.30 × P(CA5 judgment disturbed |
grant) ≈ 0.75 (the split runs 4–1 against CA5; the statpack merits disturbed
rate pooled over recent Terms is ~70%, and I nudge up for the split's
direction) × P(GVR here | that) ≈ 0.95, plus ~0.01 for a grant-and-consolidate
route ≈ **0.22**; I commit 0.20, shading toward the anchor because the chain
multiplies three uncertain estimates. Corpus priors confirm the channel: the
top-ranked GVR priors retrieved were the *Monsanto v. Salas* and *Monsanto v.
Johnson* companion petitions, GVR'd 2026-06-30 after their lead case — the
very practice this petition cites.

The 0.30 for *Vinton* is my largest uncertainty and a reader should discount
here first. It has no frozen band I can read, its docket (checked via
CourtListener, pending and unterminated as of 2026-08-16, no conference
action visible) shows no signal yet, and the BIO in this case raises
antecedent vehicle problems that infect the whole family — the Contract
Allocation Endorsement creating separate all-domestic contracts, the argument
that the Convention does not reach domestic parties at all, and the Service
of Suit endorsements — any of which could persuade the Court the question is
not cleanly presented, in which case both petitions are denied and my number
is too high. Against that, the en banc concurrence (per the petition)
disclaiming any interest in resolving the split, and the recurring nature of
the issue, argue the split will not heal itself.

**predicted_disposition `denied`, granted 0.** Denial is the modal single
outcome (~0.78); the grant-family mass is almost entirely `gvr`, not a
plenary grant.

**relist-increment 0.97.** From a zero-distribution state, this resolves as
P(ever distributed). A paid, fully-briefed petition (BIO filed 2026-08-12) is
distributed essentially always; the residual is withdrawal/settlement/
dismissal before conference.

**cvsg-increment 0.01.** Below the ~1.3% paid-segment CVSG base rate
(173/13,596): any CVSG in this family would issue in the lead case.

**summary-disposition-route 0.93.** Conditional on a grant, disposition in
the cert order (GVR) dominates; the small residual is grant-and-consolidate
with *Vinton*.

**dissent-from-denial 0.04.** Slightly above the low unconditional rate for
separate writings on denial, reflecting the live split — but a writing would
most likely attach to *Vinton*, not this companion. No published baseline;
banked.

**Inputs.** All three provisioned documents carried extractable text
(`documents.json`: no `empty_text`, no truncation); I read the QP, the
petition in full, and the BIO's structure and introduction. Snapshot is the
current forward docket through the 2026-08-12 BIO, no disposition shown — no
mis-provisioning. Retrieval was light (3 MCP/CLI lookups; one `fedcourts
query` flag error corrected); the CourtListener check of the lead case's
status is disclosed in `flags.json` as decisive forward signal.
