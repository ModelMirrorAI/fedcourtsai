# Why 0.74

## Mode and what I read

Forward cell, `arrival-position` cut anchored at entry 0 (the application's
submission). I read `record/snapshots/2026-09-25.json`, `record/context.json`
(`band: null`, `response_requested: false`, `referred_to_court: false`,
`amicus_briefs: 0`, term 2026), `event.yaml` (stage `interim`, moment `arrival`), and
the full text of the provisioned `record/documents/application.txt` (45 pages, not
truncated, not OCR-derived). In forward mode retrieval is unrestricted; I also read
the live supremecourt.gov docket for 26A406 and for the prior application in this
case (24A1153), two news/commentary posts from September 24 and 25, the corpus
statpack, and two `fedcourts query` sweeps of recent SCOTUS applications. Nothing I
saw discloses this application's disposition: as of the fetch the docket ends at
Justice Jackson's September 24 call for a response, due September 28, so the cell is
genuinely pending.

## Anchor

The statpack's interim-docket section carries the scored base rate. Pooling
application-Terms strictly before 2026 (Terms 2016 through 2025, of which only 2024
and 2025 have parsed rows): resolved 70 + 226 = 296, granted 14 + 17 = 31, a pooled
grant rate of 10.5%, well above the 50-resolved floor. The section's caption states
that its rows ground the scored rate (not the older descriptive-only wording). Two
cautions: Term 2024 is 972 unparsed of 1297, so the pool blends a partially covered
Term with a fully covered one; and the pooled population is unconditioned on the
ladder while this cell was selected on it. Neither caution moves the number for this
case, because my adjustment away from the anchor is driven by applicant identity and
case history rather than by the ladder.

## Adjustments up

- **Same case, same Court, same relief, already granted twice.** The Court stayed
  the preliminary injunction in this case in full on June 23, 2025 (6-3) and granted
  clarification on July 3, 2025 (7-2). The application argues, plausibly, that the
  final judgment rests on the same jurisdictional and due-process premises the
  Court already found likely wrong, plus a relabelling of the relief (declarations
  and vacatur in place of an injunction). The Court's own stated rule, cited in the
  application (Trump v. Boyle; Noem v. National TPS Alliance), is that interim
  orders inform like cases. This is the strongest single driver.
- **Applicant class.** The Solicitor General is not the pooled population. In the
  corpus's 2026-Term rows the SG is applicant on five substantive applications: three
  granted (League of Women Voters, National Park Service, Trump v. California), one
  denied (USPS v. California), one withdrawn. The SG's OT2024 emergency-docket record,
  which predates this snapshot and is general knowledge rather than corpus data, was
  overwhelmingly favorable. I treat the SG's realistic grant rate on a
  response-requested application as roughly 0.7 to 0.8 before case specifics.
- **Equities framing.** The First Circuit dissolved its stay at 11:36 p.m. without
  awaiting a response, weeks before the mandate, springing a judgment into effect
  that had been stayed for fifteen months. The Court's majority has repeatedly
  treated that kind of disruption of an operating policy as irreparable harm.

## Adjustments down

- **Posture differs.** This is a final judgment affirmed by a court of appeals, not
  a preliminary injunction. The new § 1231(b) statutory ground and the First
  Circuit's FARRA avoidance holding were not before the Court in 2025, and Biden v.
  Texas expressly reserved whether § 1252(f)(1) reaches declaratory relief and
  vacatur. A Justice who joined the 2025 stay could regard the declaratory-judgment
  question as genuinely open and prefer to let the cert petition carry it.
- **Mixed-order risk.** The resolver collapses "granted in part" to denied. A stay of
  the vacatur while leaving the declarations as to the four named plaintiffs, which
  § 1252(f)(1) itself permits, is a realistic shape and would score against me. I put
  roughly 0.08 on a partial or otherwise qualified order.
- **Circuit Justice signal.** Justice Jackson neither entered nor formally denied an
  administrative stay and gave respondents four days. That is the same shape as her
  handling of 24A1153, which the full Court then granted, so I read it as weakly
  informative at most. Commentary calling it a "denial" overstates what the docket
  shows.

## Decomposition

P(unqualified grant) 0.74; P(denied outright) about 0.17; P(granted in part or
otherwise qualified, scored as ungranted) about 0.08; P(withdrawn or dismissed)
about 0.01. The number is closer to the SG-specific rate than to the pooled 10.5%
anchor because the pooled anchor is dominated by pro se and capital applicants and
carries essentially no information about a repeat government application in a case
the Court has already acted on.

## The three increments

- **Response requested (0.97).** Already on the live docket, entered later on
  September 24, outside my arrival-position baseline but ordinary forward-mode
  information. The residual is uncertainty about resolution mechanics, not about
  the fact.
- **Referral (0.93).** Every SG application with a response called for in the
  corpus's 2026-Term rows that reached a decision was referred; 24A1153 was referred
  on decision day. The residual covers an in-chambers denial or a withdrawal that
  moots the referral.
- **Amicus (0.88).** 24A1153 drew three amicus briefs inside a one-week response
  window; the recent SG applications in the corpus carry 7 to 20 amicus entries.
  The count rises past zero unless the matter resolves before anyone files, which a
  four-day response window makes possible but unlikely.

## Votes and stakes

The vote block is optional and unscored on an interim cell; I include it because the
2025 lineup in this very case (Sotomayor, Kagan, Jackson dissenting; Sotomayor
writing) is a strong template. Kagan is the least certain deny: she concurred in the
July 2025 clarification order. Big-case score 0.8: a policy governing thousands of
removals, a foreign-policy dimension, an unresolved § 1252(f)(1) question, and a
near-certain cert vehicle.

## Where to discount me

The cell's evidence is heavily posture-and-identity driven; if the Court's majority
reads the declaratory-relief question as new, the number should be nearer 0.6. The
corpus offered only five SG applications for a within-corpus rate, so the
SG-specific anchor rests partly on general knowledge of the OT2024 emergency docket,
stated as such. The statpack pool's Term-2024 coverage is thin.
