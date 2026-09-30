# Rationale for the numbers — Nelsen v. Pike (26A428)

**Cell and mode.** Interim stage, `moment: arrival`, `forward` mode. The
snapshot (`record/snapshots/2026-09-30.json`) is cut at arrival-position: it
holds exactly one entry, the submission of the application to Justice
Kavanaugh on September 30, 2026. The frozen context shows `band: null`,
`response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`,
`term: 2026`. I did not derive a band; the cert band table does not apply to
an interim cell. I read the provisioned `application.txt` (15 pages, text
extracted, not truncated) in full.

**Anchor.** The statpack's *The interim docket (applications)* section, whose
caption calls its per-Term rates the grounding of the interim stage's scored
base rate (not descriptive-only). Application-Term 2026; pooling the
resolved substantive slice over strictly-prior Terms in the ten-Term window
(2016–2025) gives 17/226 (Term 2025) + 14/70 (Term 2024) = 31/296 = 10.5%,
which clears the 50-resolved floor. Two coverage cautions: Terms 2016–2023
carry zero parsed rows (the whole window's pool is two Terms), and Term 2024
has 972 unparsed applications beside its 70 substantive ones, so the 20%
Term-2024 rate rests on a partial poll. I treat 10.5% as the yardstick I am
scored against, not as a description of this application's class.

**Why I move far above the anchor.** The pooled slice mixes every substantive
applicant: prisoners seeking stays of execution (granted very rarely),
private litigants seeking stays of civil judgments, and governments. A
*state's* application to vacate a lower federal court's last-minute stay of
execution is a small class with a very different history in this Court:
Dunn v. Ray (2019), Dunn v. Price (2019), Barr v. Lee, Barr v. Purkey, and
Barr v. Hall (2020), Hamm v. Reeves (Jan. 2022), and both Hamm v. Smith
applications (Jan. and Nov. 2022) were all granted; Dunn v. Smith (Feb. 2021,
the chaplain-in-chamber injunction) is the salient recent denial. From
memory rather than a committed cut, that class grants on the order of three
in four. The statpack publishes no applicant-class cut, so this adjustment is
mine and a reader should discount it accordingly.

Case-specific factors pushing up from that class rate:

- The Court denied Pike's own stay application and cert petition the day
  before (the application recites this; it predates the snapshot and is
  legitimate signal). A majority has already declined to halt this execution
  once.
- The Sixth Circuit order (read on CourtListener, RECAP document 495590629)
  contains no likelihood-of-success analysis at all; it rests the stay on the
  need to "properly analyze the parties' fully briefed arguments." Price v.
  Dunn says exactly that is not enough. Pike had not asked for a stay.
- Judge Griffin's dissent lays out the Gonzalez v. Crosby analysis the Court
  would adopt: the only "new" fact is the State's expression of sympathy, and
  the theory (that it undermines the deference given to the state court's
  prejudice finding) attacks the merits ruling. This is the kind of
  disguised-successive-petition case the current majority treats as
  straightforward.
- The 60(b) motion was filed 47 days after the hearing statement it relies on,
  the evening before the execution. The Bucklew/Price equitable presumption
  against last-minute filings applies with full force.

Factors pushing down:

- The panel framed its stay as short and the motion as fully briefed. The
  Court has sometimes let a court of appeals finish a same-week jurisdictional
  question rather than intervene, and the panel could itself rule and lift
  the stay before the Court acts, which would moot the application
  (resolving as withdrawn or dismissed, both ungranted).
- A 2-1 published circuit order is somewhat more resistant to vacatur than an
  unexplained district-court stay.
- Tennessee's execution order fixes a single day; if the Court does not act by
  the end of September 30 the State may withdraw rather than press a moot
  application.

Net: 0.72 for an unqualified grant. The interim vocabulary reads partial
relief as ungranted, but a vacatur application has no natural partial shape,
so that collapse costs little here.

**Increments.** Response-requested 0.25: on this Court's same-day capital
vacatur dockets the response usually appears as a filing without a recorded
request entry; I am uncertain how the harness's matcher reads a Clerk's
letter if one is docketed. Referral 0.9: the full Court decides these, and the
disposing order recites the referral; the residue is the mootness path.
Amicus 0.03: no time for amici on a same-day capital application.

**Big case.** 0.6. Pike is Tennessee's only woman on death row and would be
the first woman executed in the state in roughly two centuries; the stakes are
a life and the coverage is national. The legal question is narrow, which is
why the score is not higher.

**Uncertainties and discounts.** (1) My class rate for state vacatur
applications is from memory, not a committed cut. (2) I have not seen Pike's
remand motion or her forthcoming response, only the panel majority's summary
of them and the State's characterization. (3) The Sixth Circuit docket on
CourtListener showed no entry after the 9:17 a.m. stay order as of its last
poll; if the panel has since ruled, the case's shape may already have changed.
(4) I have no knowledge of this application's disposition and did not seek it.
(5) I cannot verify the current composition of the Court from the record, so I
recorded no per-Justice votes.

**Retrieval degradation.** None. The CourtListener MCP server answered every
call. `fedcourts query` returned only routine time-extension grants for a
granted-applications query and has no text or applicant-class filter, so the
corpus priors surface contributed nothing; the anchor came from the statpack.
