# Thompson v. Wilson, No. 25-1105 — cert-stage disposition prediction

**Prediction: denied. P(grant, GVR included) = 0.10.**

## The case

Frank Thompson, a Maine lobsterman represented by Pacific Legal Foundation,
challenges Maine's DMR Rule (13-188 C.M.R. ch. 25.98), which — implementing
ASMFC Addendum XXIX — requires federally permitted lobstermen to keep a GPS
tracking device on their vessels, transmitting position once per minute while
moving and every six hours when moored, as a condition of licensure. The First
Circuit (159 F.4th 91, Nov. 18, 2025) affirmed dismissal, applying the
*New York v. Burger* three-part test for administrative searches of closely
regulated industries (both sides had made framing concessions below: the State
conceded the rule effects Fourth Amendment "searches"; plaintiffs conceded
lobstering is closely regulated).

The petition (filed Mar. 19, 2026, paid, Term 2025) presents two questions:
(1) whether the 24/7 tracking mandate is an unreasonable *trespassory* search,
and (2) whether *Burger* reasonableness must incorporate *Jones* (2012)
trespass-to-property protections rather than resting solely on
reasonable-expectation-of-privacy premises. It alleges a split: First and
Tenth Circuits (*Johnson v. Smith*) versus Ninth (*Rush v. Obledo*, *Patel I*)
and Sixth (*Taylor II*).

## Docket signals (from the 2026-07-16 snapshot)

Pro-grant:

- **Call for response.** Respondent waived (May 21); the case was distributed
  for the June 11, 2026 conference; on June 3 the Court **requested a
  response** (due July 6). A CFR means at least one chambers took interest —
  the strongest single upgrade visible on this docket. Paid petitions with a
  CFR grant at roughly an order of magnitude above the raw paid base rate.
- **Cert-stage amicus support**: five briefs from repeat institutional players
  (American Farm Bureau Federation, Cato Institute & NFIB, Landmark Legal
  Foundation, Manhattan Institute; Liberty Justice Center filed then withdrew).
  Coordinated amicus campaigns of this size are a recognized grant correlate.
- **Experienced counsel** (PLF, with a strong cert-stage track record) and a
  clean, vivid factual frame (fifth-generation lobsterman under warrantless
  24/7 government GPS surveillance, including personal use of the boat).
- **Doctrinal appetite.** The tension between *Jones*/*Carpenter* property
  reasoning and the *Katz*-rooted *Burger* framework is a live academic and
  judicial question (the petition leans on Kerr's 2025 article and Justice
  Gorsuch's January 2026 concurrence in *Case v. Montana*), and the Court took
  *Chatrie* (geofence surveillance) this Term — evidence of continuing
  interest in location-surveillance doctrine.

Pro-deny (and these are substantial):

- **Preservation.** The BIO's lead argument is that the trespass/*Jones*
  theory now headlining the petition was never made to the First Circuit —
  the word "trespass" allegedly appears nowhere in Thompson's CA1 briefs, and
  *Rush* was never cited below. The First Circuit's opinion cited neither
  *Jones* nor *Katz*. If accurate (and it reads as verifiable), this is
  exactly the kind of vehicle defect the cert pool flags; "court of review,
  not first view" denials are routine even in attractive doctrinal areas.
- **The split is contestable.** *Rush* predates *Burger*; *Taylor II* turned
  on municipal parking *not* being a closely regulated industry, so *Burger*
  never applied; *Patel I*'s Jones/Katz discussion went to whether a search
  occurred, not *Burger* reasonableness. The alleged 2-2 split dissolves into
  fact-specific applications more readily than the petition admits.
- **Concession-bound record.** Thompson conceded below that lobstering is
  closely regulated (and tried to walk it back on appeal), so the case cannot
  cleanly present the "closely regulated industry creep" issue the amici
  press. The QP's assertion that the First Circuit held *Jones* applies "to
  criminal cases only" overstates a footnote rejecting a "direct comparison"
  to *Carpenter*.
- **Maritime context.** The BIO invokes the long tradition of suspicionless
  vessel boarding (*Villamonte-Marquez*), which gives the Court a reason to
  see the facts as sui generis rather than a clean vehicle for reshaping
  administrative-search doctrine generally.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted):
modern discretionary cert petitions resolve overwhelmingly to denial (~95%);
Term 2025 paid petitions grant at ~5.4% (Term 2024: ~6.9%; IFP ~1%). The
statpack's relist cut shows the escalation ladder (0 relists → 0.8%; 1 →
7.6%; 2 → 33.6%), but this case has not yet been to conference — the June 11
distribution was superseded by the CFR, and as of the snapshot the BIO is 10
days old with no redistribution yet (a reply and a late-September "long
conference" distribution are the likely next steps). No CVSG. The statpack
carries no CFR cut and this build has no salience-band table, so I calibrate
the CFR effect from general SCOTUS practice: paid + CFR ≈ 8–12%.

Starting from that CFR-conditioned band, the amicus coordination, counsel
quality, and doctrinal salience argue for the top of the band or above
(~12–15%); the preservation defect, the contestable split, and the
concession-bound record argue for a real discount — the BIO gives the pool
clerk three independent, low-cost deny rationales. I land at **P(grant) =
0.10**, which implicitly includes a small (~1–2%) chance of a GVR or
grant-in-part path (e.g., holding for *Chatrie* and disposing in its light —
unlikely, since *Chatrie* is a criminal geofence-warrant case that does not
speak to *Burger*).

Most likely disposition: **denied**, probably after one or more
distributions in fall 2026, possibly with a relist and non-trivially with a
dissent from or statement respecting denial (Gorsuch and/or Thomas are the
natural candidates given their expressed views on *Katz*-based doctrine).

## Inputs used

- Latest snapshot `record/snapshots/2026-07-16.json` (docket 25-1105, full
  proceedings list through the July 6, 2026 BIO).
- Provisioned `questions-presented.txt`, `petition.txt` (45 pp., full), and
  `brief-in-opposition.txt` (32 pp., full) — the QP framing, split argument,
  and vehicle analysis above are anchored on these.
- Committed `metrics/statpack.md` / `statpack.json` base rates (paid vs. IFP
  per-Term grant rates, relist and CVSG cuts).
- `fedcourts query` corpus retrieval was attempted for similar priors
  (Jones/Burger citers, Fourth Amendment topic) and returned no rows — see
  `retrieval.md`.
