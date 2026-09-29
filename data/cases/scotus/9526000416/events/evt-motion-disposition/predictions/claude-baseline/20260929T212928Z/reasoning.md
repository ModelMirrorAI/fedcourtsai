# Why 0.68

## Mode and what I read

Forward cell, `arrival-position` cut anchored at entry 0 (the submission entry).
I read `record/snapshots/2026-09-28.json`, `record/context.json` (`band: null`,
`response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`,
term 2026, `signals_observable: true`), `event.yaml` (stage `interim`, moment
`arrival`), and the full text of the provisioned `record/documents/application.txt`
(40 pages, not truncated, not OCR-derived; no response or appendix was
provisioned, so the respondents' side is inferred from the application's own
account of the rulings below). In forward mode retrieval is unrestricted; I also
read the live supremecourt.gov dockets for 26A416 and for Trump v. Orr (25A319),
the SCOTUSblog case page, two news items from September 28, the ACLU case page,
the district court docket on CourtListener, the corpus statpack, and one
`fedcourts query` sweep of recent SCOTUS applications. Nothing I saw discloses
this application's disposition: as of the fetch the docket ends at the Chief
Justice's September 28 call for a response, due October 8, so the cell is
genuinely pending. The band is null, as an interim cell's should be; I did not
derive one.

## Anchor

The statpack's "The interim docket (applications)" section carries the scored
base rate, and its caption uses the current "ground the interim stage's scored
base rate" wording, not the older descriptive-only one. Pooling application-Terms
strictly before 2026 within the ten-Term window (2016 through 2025), only Terms
2024 and 2025 have parsed rows: resolved 70 + 226 = 296, granted 14 + 17 = 31, a
pooled grant rate of 10.5%, clearing the 50-resolved floor. Two cautions the
section itself carries: Term 2024 is 972 of 1297 unparsed, so the pool blends a
partially covered Term with a full one; and the pooled population is
unconditioned on the escalation ladder while this cell was selected on it. The
corpus rows I pulled show the same shape: 98 resolved substantive applications
in the recent slice, 7 granted, and every one of the 7 was referred to the Court
and carried amici; 6 of the 7 had a response called for.

## Adjustments up

- **Applicant class.** The pooled population is dominated by pro se and capital
  applicants and says almost nothing about a Solicitor General application. In
  the corpus's federal-applicant substantive rows for Terms 2025 and 2026 the
  government is 4 granted (Trump v. California 26A124, National Park Service
  26A203, League of Women Voters 26A308, D.V.D. 26A406), 5 denied, 1 withdrawn.
  Four of the five denials are dated June 29 and 30, 2026 and look like
  end-of-Term resolutions of applications the Court had held for argued cases
  (Trump v. Cook among them), which is a different animal from a fresh stay
  request; the fifth, USPS v. California, was denied in September. Read for
  fresh stay applications alone, the government's record in the corpus is 4 of
  5, and its OT2024 emergency-docket record, general knowledge rather than
  corpus data, was similarly lopsided. I treat the SG's realistic grant rate on
  a response-requested application as roughly 0.7 to 0.8 before case specifics.
- **The closest analogue is a grant.** Trump v. Orr (25A319) is the same
  Executive Order, the same claim type (APA arbitrary-and-capricious against a
  sex-classification policy), the same relief below (a classwide preliminary
  injunction), the same applicant, and it was granted 6-3 on November 6, 2025.
  United States v. Shilling (the military policy) was granted 6-3 in May 2025.
  Skrmetti supplies the deference framing the application leans on, and the
  application quotes it.
- **Prison-administration deference and the PLRA.** Bell v. Wolfish and Turner
  give the government a second layer of deference the Orr record lacked, and
  the PLRA overbreadth point is strong on its face: the injunction bars the
  surgery prohibition though respondents disclaimed any harm from it.
- **The Court's stated irreparable-harm rule.** League of Women Voters, Trump v.
  California, and CASA all treat a wholesale block on an Executive policy as
  irreparable harm to the government; a universal Section 705 stay plus a
  nationwide class is exactly that shape.

## Adjustments down

- **Mixed-order risk.** The resolver collapses "granted in part" to denied. The
  respondents' irreparable harm is concrete and medical: inmates currently on
  hormones face tapering. A stay that carves out current recipients, or that
  reaches only the surgery and social-accommodation provisions, is a realistic
  shape, and the government's own PLRA argument marks the seam. I put roughly
  0.14 on a partial or otherwise qualified order.
- **A fact-bound APA dispute with an eighteen-month record.** Unlike Orr, this
  policy has already been enjoined once on APA grounds, redone on a new
  administrative record, and enjoined again by a Reagan-appointed district judge
  who found pretext. The D.C. Circuit majority's ground, that BOP asserted
  security harms without addressing whether any had occurred, is the kind of
  record-based criticism a Justice can accept without disturbing any doctrine.
  Justices Barrett and Roberts could regard a preliminary injunction preserving
  a treatment status quo, pending an expedited appeal, as tolerable.
- **No urgency signal.** The Chief Justice set a ten-day response window and
  entered no administrative stay. That is the ordinary shape for an SG
  application (Orr's window was two weeks), so I read it as weakly informative.
- **Term-end denials.** The four June 2026 denials of SG applications, whatever
  their mechanics, are a reminder that the SG's record is not uniform.

## Decomposition

P(unqualified grant) 0.68; P(granted in part or otherwise qualified, scored as
ungranted) about 0.14; P(denied outright) about 0.17; P(withdrawn or dismissed)
about 0.01. The number sits far above the pooled 10.5% anchor because the anchor
carries essentially no information about a repeat federal applicant on a policy
the Court has already sided with twice in adjacent postures.

## The three increments

- **Response requested (0.98).** Already on the live docket, entered later on
  September 28, outside the arrival-position baseline but ordinary forward-mode
  information. The residual is resolution mechanics.
- **Referral (0.94).** Every granted substantive application in the corpus slice
  was referred; every SG application with a response request that reached a
  decision was referred; Orr was referred on decision day. The residual is a
  withdrawal or an in-chambers denial.
- **Amicus (0.93).** Orr drew one amicus entry in a two-week window on a lower
  profile issue; the SG's other 2026 applications carry 2 to 22 amicus entries;
  the trans-healthcare field is heavily organized on both sides. The count rises
  past zero unless the Court acts before anyone files, which a ten-day response
  window makes unlikely.

## Votes and stakes

The vote block is optional and unscored on an interim cell; I include it because
Orr's lineup (Sotomayor, Kagan, Jackson dissenting; Jackson writing) is the
natural template for the same Executive Order in a new setting. Kagan is the
least certain deny. Big-case score 0.7: a nationwide policy on medical care for
about 2,000 inmates, the next step in the Court's gender-identity line, and a
near-certain cert vehicle if the D.C. Circuit affirms; below the removal and
immigration applications in national stakes.

## Where to discount me

The forecast is driven by applicant identity and the Orr analogue more than by
this record; if the Court's majority reads the case as a fact-bound APA dispute
about a twice-enjoined policy, the number belongs nearer 0.55. The corpus holds
only ten federal-applicant substantive rows and I could not verify the mechanics
of the four June 2026 denials, so the SG-specific rate rests partly on general
knowledge, stated as such. The statpack pool's Term-2024 coverage is thin. I did
not have the respondents' filings or the D.C. Circuit order text itself; my read
of the panel's reasoning is the application's account of it.
