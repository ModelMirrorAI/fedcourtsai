# Jouppi v. Alaska, No. 25-246 — cert-petition disposition

**Prediction: denied (modal), P(granted) = 0.42.** This is a genuinely
high-variance cell: the petition carries nearly every classic pre-grant
signal short of an actual grant, but the modal outcome for even the
strongest cert candidates is still denial, and the probability I can
justify stays just under a coin flip.

## The legal question

Kenneth Jouppi, an 82-year-old Alaska bush pilot represented by the
Institute for Justice, challenges the forfeiture of his $95,000 Cessna
after a misdemeanor conviction for knowingly transporting a passenger's
alcohol (on the state's own framing, at least one visible six-pack of
beer) toward the dry village of Beaver. The Alaska Supreme Court held
unanimously, "as a matter of law," that the forfeiture is not grossly
disproportional under *United States v. Bajakajian*, 524 U.S. 321 (1998),
evaluating the gravity of the offense by reference to the legislature's
abstract judgment about dry-village alcohol importation rather than
Jouppi's individual culpability.

The question presented is whether Excessive Fines Clause proportionality
review measures the gravity of the offense in the abstract (Alaska
Supreme Court, Eleventh Circuit) or by the specific defendant's
wrongdoing (Ninth Circuit — Alaska's home circuit — plus the First
through Tenth Circuits in varying formulations and the Indiana,
Pennsylvania, Utah, and D.C. high courts, per the petition).

## Signals from the record (snapshot + provisioned documents)

Favoring a grant:

- **Call for response.** Alaska waived its response (Sept. 4, 2025); the
  Court requested one (Sept. 17, 2025). A CFR is one of the strongest
  observable cert-stage signals — at least one chamber flagged the case.
- **Three cert-stage amicus briefs** — Cato Institute, Prof. Beth Colgan
  (the leading Excessive Fines Clause scholar), and Tyson Timbs himself
  (the *Timbs v. Indiana* petitioner), all with experienced Supreme Court
  counsel.
- **Split quality.** The alleged conflict pits a state high court against
  its own home federal circuit (Ninth), a classic Rule 10 "compelling
  reason." A June 18, 2026 Washington Supreme Court dissent (*State v.
  Meta Platforms*) cited this very decision as emblematic of the split.
- **Vehicle.** The decision below resolved the question "as a matter of
  law," assuming disputed facts in Jouppi's favor (culpability limited to
  one six-pack), and the state concedes the in personam criminal
  forfeiture is a "fine." Pure legal question, squarely presented,
  outcome-determinative.
- **The hold-and-carry pattern.** The docket shows distribution for the
  12/12/2025 conference and then silence until June 2026 — the signature
  of a hold, not serial relists. Petitioner's June 25, 2026 supplemental
  brief confirms the hold was for *Pung v. Isabella County*, No. 25-95
  (decided June 23, 2026), which resolved only the *threshold* "is this a
  fine?" question and did not touch Jouppi's second-step excessiveness
  standard. The petition was then redistributed for the June 29, 2026
  end-of-term cleanup conference — and, critically, **was not disposed of
  on the June 30 orders list**. Corpus priors show that conference
  produced same-day grants and denials (e.g., *Viramontes*, *McCoy*,
  granted/denied 2026-06-30); Jouppi's docket shows no order as of the
  July 13 snapshot. The petition is being carried over the summer, which
  means someone in the building wants it either granted after the
  customary further look (the *Little v. Hecox* / *Collins v. Mnuchin* /
  *AMG Capital* post-hold-grant pattern that petitioner's own supplemental
  brief catalogs) or held for a written dissent from denial.
- **Subject-matter appetite.** The Court has taken three fines-adjacent
  cases in eight years (*Timbs*, *Culley*, *Pung*), and Justices Gorsuch
  and Sotomayor have both written separately urging attention to
  exorbitant fines (*Toth* dissent from denial; *Culley* opinions).
- **Paid petition** with repeat-player counsel (IJ won *Timbs* on this
  same clause).

Favoring denial:

- **The base rate.** Modern discretionary-cert petitions grant at ~4.9%
  (statpack, denial-reweighted, resolved slice). Even conditioning on a
  CFR (~8–12x enrichment historically) and multiple amici, most such
  petitions are still denied.
- **The BIO's vehicle attack has real content.** Troopers testified
  Jouppi repacked open boxes containing nine gallons of beer; the jury
  was instructed on deliberate ignorance; the sentencing record included
  three prior alleged importation flights and a separate felony case
  resolved by plea; the trial judge found Jouppi "really did know what
  was in the box." The "plane for a six-pack" framing is contestable, and
  a Justice looking for a reason to pass can find one — though the state
  court's matter-of-law holding on facts assumed in Jouppi's favor blunts
  much of this.
- **The Court has passed on this precise second-step question before**
  (e.g., *Toth* (2023), over a written dissent; the First Circuit's
  *Facteau* cert denial (2024)). Excessive-fines-standard petitions have
  a track record of near misses.
- **A summer carry-over is not a grant.** A substantial fraction of
  petitions that survive the cleanup conference emerge in October as
  denials accompanied by a statement or dissent from denial — an outcome
  this case, with its sympathetic facts and two demonstrated
  fines-hawk Justices, fits comfortably.
- **GVR is essentially off the table** (~3%): *Pung* resolved the
  threshold question in a way irrelevant to a conceded in personam
  criminal fine, so there is nothing for the Alaska courts to reconsider
  "in light of" it — which removes the usual cheap exit for held cases
  and pushes probability mass toward both plenary grant *and* outright
  denial.

## Calibration

Start near the CFR-conditioned grant rate (~10–15%), then adjust up for
the amicus support, the state-vs-home-circuit split, the clean
matter-of-law vehicle, the post-*Pung* survival of the June 30 orders
list, and the demonstrated subject-matter appetite. The strongest
comparable public pattern — held petition, hold case decided without
resolving the QP, supplemental briefing, carried past the cleanup
conference — resolves as a grant roughly 40–50% of the time, with most
of the remainder denials (often with writing). I land at **P(granted) =
0.42**, so the binary call is 0 and the modal predicted disposition is
**denied**, most likely on an early-October orders list after the long
conference, quite possibly over a dissent from denial; the grant branch
(~40%) would put the case on the OT2026 argument calendar.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-13.json`), the event
definition, `record/context.json` (mode: `forward`), and the provisioned
document texts: `questions-presented.txt`, `petition.txt` (42 pp.), and
`brief-in-opposition.txt` (41 pp.). Beyond the provisioned inputs I
consulted the committed statpack, two `fedcourts query` corpus lookups,
the petitioner's June 25, 2026 supplemental brief (fetched from the
supremecourt.gov link in the snapshot docket), and one CourtListener MCP
search confirming *Pung*'s existence and decision date — all logged in
`retrieval.md`. I did not search for, and did not encounter, any
disposition of this petition; the snapshot and the corpus's live-polled
priors confirm it remained pending as of 2026-07-13.
