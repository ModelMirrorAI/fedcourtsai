# Williams v. Pennsylvania, No. 25-1277 — cert petition disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.03.**

## The case

Scott R. Williams was convicted of a 1995 rape and aggravated assault in Centre
County, Pennsylvania, after a 2019–2021 investigative genetic genealogy effort:
Parabon/GEDmatch analysis of the 1995 crime-scene DNA, a buccal sample
volunteered by Williams's mother, surreptitious collection of his son's utensils
at a football banquet, and a warrantless trash pull that yielded chew-spit
bottles whose DNA matched the crime-scene profile. Decades earlier (2000),
police had filed a "John Doe" DNA complaint and arrest warrant — identifying
the accused only by six RFLP loci common to all humans, with no DNA profile
attached and no random-match statistics — to toll the statute of limitations.
The Pennsylvania Superior Court affirmed in a published opinion
(Commonwealth v. Williams, 342 A.3d 742 (Pa. Super. 2025)), holding the Doe
warrant sufficiently particular and the trash/utensil DNA extraction and
profiling warrantless-search-free under the abandonment doctrine. The
Pennsylvania Supreme Court denied allowance of appeal on February 4, 2026.

The paid petition (filed May 5, 2026, docketed May 12) presents two questions:
(1) whether a John Doe DNA complaint/warrant that lists only generic loci —
no profile, no statistics — satisfies the Fourth Amendment's particularity
requirement; and (2) whether the warrantless extraction of DNA and creation of
DNA profiles from lawfully seized/discarded items is an unconstitutional
search. As of the 2026-07-17 snapshot: no brief in opposition or waiver entry
appears on the docket (response was due June 11), no amici, and the case was
distributed June 24 for the September 28, 2026 long conference.

## Base rate anchor

From the committed statpack (live/historical slice, denial-reweighted): modern
discretionary-cert petitions run ~3% granted overall; recent complete Terms
show est. grant rates of 2.5% (T2025), 3.0% (T2024), 3.3% (T2023). This is a
paid petition (paid petitions grant meaningfully more often than IFP, so the
paid-only anchor sits somewhat above the blended rate), but every observable
salience signal is at baseline: zero distributions beyond the initial one
(relist bucket 0 → 0.8% grant among resolved), no CVSG (none → 3.0%), no
amici, and — most tellingly — distribution without a response on file and
without a call for a response as of the snapshot. The Court essentially never
grants plenary review without at least a CFR when the respondent has waived.

## Cert-positive factors

- **Genuinely unresolved, recurring federal questions.** The Court has never
  addressed John Doe DNA warrants or whether extracting and profiling
  "abandoned" DNA is a separate Fourth Amendment search. With forensic genetic
  genealogy now routine, both issues will recur.
- **A real split on QP1.** Kansas (State v. Belt) and Connecticut (State v.
  Police) invalidated Doe DNA warrants lacking an attached profile or
  statistical-rarity showing; California (Robinson), Tennessee (Burdick), and
  the Seventh Circuit (Boughton) upheld warrants that included them. The
  Pennsylvania court upheld a warrant that had neither — arguably placing it
  on the wrong side of a discernible line rather than distinguishing it.
- Published lower-court opinion; competent counseled presentation.

## Cert-negative factors

- **Vehicle.** The decision comes from an intermediate state appellate court
  after discretionary review was denied — a posture the Court disfavors. QP1
  also has a remedy problem: the Doe complaint's operative function was
  tolling the limitations period, and the trial evidence came from the 2021
  trash-pull DNA match, not from executing the 2000 warrant, so particularity
  may not control suppression; the limitations question underneath is one of
  state law.
- **The QP1 split is fact-reconcilable.** Every cited case turns on whether
  the profile/statistics were included; courts can (and do) treat that as a
  case-by-case sufficiency question rather than a doctrinal split requiring
  resolution.
- **QP2 runs against a wall of authority.** Nearly every court to consider
  abandoned/discarded DNA — Athan (Wash.), Raynor (Md.), Burns (Iowa 2023),
  and the state cases the petition itself distinguishes — has upheld
  warrantless profiling; the claimed conflict with United States v. Davis
  (4th Cir.) is thin. The Court denied cert in Raynor (2015) and has
  repeatedly passed on this issue. The novel parental-standing theory for the
  son's DNA is unsupported (the petition concedes it found no authority), and
  QP2 as printed is textually truncated ("...creation of DNA profiles from."),
  which does not help.
- **No engagement signals.** No response filed by the due date, no CFR, no
  amici, single distribution to the long conference — the routine
  deny-pile track.

## Bottom line

The issues are important and will eventually get the Court's attention, but
this petition, in this posture, with no respondent engagement and no CFR as of
the snapshot, looks like a standard long-conference denial. Starting from the
~2.5–3% paid-petition anchor, the interesting QP1 split and the salience of
genetic-genealogy privacy roughly offset the weak vehicle, the fact-bound
split, the anti-precedent on QP2, and the absence of any docket interest
signals. P(grant, including GVR) ≈ 0.03; predicted disposition: **denied**.
(A CFR or relists after September 28 would be the signals that this estimate
is too low.)

## Retrieval note

The CourtListener MCP server was rate-throttled (HTTP 429, shared daily quota)
for most of the run; a late retry succeeded and confirmed via the dockets
endpoint that No. 25-1277 is still pending (`date_terminated` null) — the
forward cell is properly provisioned. CourtListener carries no SCOTUS
docket-entry detail, so whether Pennsylvania formally waived its response
could not be confirmed beyond the snapshot's silence; the analysis above
treats the missing BIO plus distribution as the (standard) waiver pattern.
Everything else rests on the provisioned snapshot (2026-07-17), the
provisioned petition text, one corpus `fedcourts query`, and the committed
statpack.
