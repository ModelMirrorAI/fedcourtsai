# Gasper v. Wisconsin, No. 25-1191 — cert disposition prediction

**Prediction: deny. P(any grant, GVR included) ≈ 0.06.**

## The case

Michael Gasper uploaded a 16-second video to his Snapchat account. Snapchat's
PhotoDNA hash-matching flagged it as CSAM and — without any human at Snapchat
viewing it — reported it to NCMEC, which forwarded a CyberTip to the Wisconsin
DOJ. A state analyst and later a county detective each opened and viewed the
video without a warrant; a search warrant for Gasper's home and devices
followed, yielding ten CSAM files on his phone and charges. The trial court
suppressed everything; the Wisconsin Court of Appeals reversed; the Wisconsin
Supreme Court (2026 WI 3, Jan. 14, 2026) vacated the court of appeals' reasoning
but affirmed on the private-search doctrine: under *Jacobsen*, the hash match
made it a "virtual certainty" the officer would see nothing beyond what
Snapchat's own scan had revealed, so the warrantless viewing did not expand the
private search. It remanded for further proceedings; Gasper has not been tried,
convicted, or sentenced.

The petition (QP2 is the core) asks whether warrantless police viewing of a
previously-unviewed hash-match CyberTip falls within the private-search
exception — an acknowledged split: the Fifth (*Reddick*), Sixth (*Miller*), and
several state high courts (now including Wisconsin) say yes; the Ninth
(*Wilson*), Second (*Maher*), and — one month before this petition — the Fourth
(*Lowers*, 170 F.4th 134 (4th Cir. 2026)) say no. QP1 (reasonable expectation of
privacy in cloud-stored cellphone data) and QP3 (good-faith exception) were not
decided by the Wisconsin Supreme Court.

## Docket signals (pro-grant)

- **Call for response.** Wisconsin waived (Apr 21); the case was distributed for
  the 5/21/2026 conference; on May 8 the Court **requested a response** — a CFR
  means at least one chambers looked and wanted the state's answer. CFR'd paid
  petitions grant at roughly an order of magnitude above the paid base rate.
- **Cert-stage amicus** from the Project for Privacy & Surveillance
  Accountability (Gene Schaerr as counsel) — organized-bar interest.
- **A real, deepening, well-percolated split** on a recurring question of
  enormous operational scale (NCMEC processes tens of millions of CyberTips a
  year), squarely in the Court's post-*Riley*/*Carpenter* digital-privacy lane.
- Paid petition, counseled, from a state court of last resort; now distributed
  for the 9/28/2026 long conference (first post-BIO distribution — no relists
  yet, and none possible yet).

## Why deny anyway (the weight of the evidence)

1. **A likely-fatal jurisdictional defect.** The Wisconsin Supreme Court's
   decision is interlocutory: Gasper is unconvicted and the case was remanded
   with multiple suppression theories still pending (the administrative-subpoena
   challenge, the scope-of-warrant challenge to the phone search, the statements
   motion). Under 28 U.S.C. § 1257(a) and *Cox Broadcasting*, finality in a
   criminal case means conviction and sentence, and the BIO's mapping of this
   case onto *Florida v. Thomas*, 532 U.S. 774 (2001) — where the Court
   unanimously found no jurisdiction over a state interlocutory suppression
   ruling in materially identical posture — is close to airtight. None of the
   four *Cox* exceptions plausibly applies; Gasper can simply re-petition after
   final judgment. The Court very rarely grants over a genuine finality problem.
2. **Vehicle problems even past jurisdiction.** (a) Two of the three QPs were
   never decided below — the court decided only the private-search question —
   and the Court is "a court of review, not of first view." (b) An alternative
   ground for affirmance: the court of appeals held Gasper failed to prove even
   a subjective expectation of privacy (his affidavit was excluded and he
   abandoned reliance on it), and he asserts no property interest. (c) No
   practical effect: all seven Wisconsin justices — including the two who
   rejected the private-search rationale — concluded the ten phone-derived CSAM
   files that actually support the charges need not be suppressed, so a
   petitioner win here approaches an advisory opinion.
3. **Better vehicles are arriving.** *Lowers* (4th Cir. 2026, government lost —
   a potential SG petition on a final federal judgment), *Braun* pending in the
   Seventh Circuit (No. 25-2740), and an Eleventh Circuit decision this month
   (*Brillhart*, July 9, 2026) all present the same question in cleaner postures.
   The Court has already let this split percolate past *Reddick*, *Miller*, and
   *Wilson*; when it resolves it, a final-judgment federal case is the natural
   vessel.
4. **Petition quality.** Non-specialist counsel, citation typos
   ("Schneckbloth," "Gideon v. Wainright"), sweeping political rhetoric, three
   QPs where only one is preserved, and no engagement with *Lowers* (decided a
   month before filing). The BIO, by contrast, is disciplined and leads with the
   jurisdictional kill-shot.

## Base rates and the arithmetic

From the committed statpack (live/historical slice, denial-reweighted): modern
discretionary cert petitions grant ≈ 3.1% overall; Term-2025 estimated grant
rate 2.5%; zero-relist petitions grant 0.8% while CVSG'd petitions grant 27%
and 2-relist petitions 34%. (The statpack version in the repo carries no
salience-band table, so I anchored on these cuts.) A paid petition + CFR +
cert-stage amicus + acknowledged split would normally put this in roughly the
8–15% band. The finality defect is the dominant discounter — it is not a
discretionary factor but a jurisdictional bar the BIO has argued convincingly —
and the no-practical-effect/alternative-grounds problems stack on top. I
discount the signal-band estimate by ~60% for jurisdiction and vehicle,
landing at **P(grant incl. GVR) ≈ 0.06**, which also folds in a small (~2%)
chance of a later hold-and-GVR if the Court grants a companion vehicle this
Term and rules for the defendant side.

Likeliest path: considered at the 9/28/2026 long conference; possibly relisted
once or held briefly against a companion petition; **denied**.

## What I used

Provisioned snapshot (`record/snapshots/2026-07-17.json`), questions-presented,
petition text (truncated at ~172pp incl. appendix; QPs, statement, and reasons
sections all read), and the full 34-page BIO; the committed
`metrics/statpack.md`; two `fedcourts query` prior pulls (both returned zero
matching rows); one CourtListener opinion search confirming the split's recent
development (*Lowers*, 4th Cir., Mar. 10, 2026; *Brillhart*, 11th Cir., Jul. 9,
2026). Forward-mode cell: the conference date (9/28/2026) post-dates today, so
no outcome exists to leak; I did not search for this case's disposition.
