# Reasoning — why 0.35, and why the ladder numbers

## Inputs

Provisioned: snapshot `2026-10-06.json` (two entries), `context.json`
(forward; band null; response requested; not referred; zero amici; Term 2026),
and the application text (134 pages, truncated — the appendix with the
lower-court opinions was cut, so the Ninth Circuit's reasoning reaches me only
through the applicants' account). Retrieved: the district and Ninth Circuit
dockets and the Mirabelli v. Bonta per curiam via CourtListener; two
`fedcourts query` sweeps that returned nothing usable (see `retrieval.md`).

## Base rate

The statpack's interim section is the anchor. Pooling the substantive resolved
slice over application-Terms strictly before 2026 and within ten Terms
(2016–2025): only Terms 2024 and 2025 carry parsed rows — 14/70 and 17/226 —
for **31 granted of 296 resolved, 10.5%**, well above the 50-resolved floor, so
a published baseline exists and that is the yardstick I am scored against. The
section's own caption calls the rows the grounding of the scored rate (not the
descriptive-only wording), so I read it as the estimator's caption. Caveats I
carried: Term 2024 is 972/1297 unparsed, so the pool leans on 2025; the
escalation-signal columns (response requested 64 of 367 substantive) are
right-censored and not as-at-prediction, so I read them only for shape — a
requested response is uncommon in the slice, which marks this application as
one of the serious minority; and the predicted cohort is selected on exactly
these rungs, so a skill number here is not by itself evidence of skill.

Interim cells do not use the cert band table, and `band` is null as it should be.

## Adjustments from 10.5% to 0.35

**Up, strongly.** The 2026 Court has shown its hand on both theories the
application rests on: West Virginia v. B.P.J. (June 2026) held, on the
applicants' account, that sex-separated athletics may exclude male athletes and
described their safety and competitive advantages as the "reality of sports";
Mirabelli v. Bonta (March 2026, read in full) granted parents interim relief
against California's school gender-identity policies 6–3, with the per curiam
calling "children's safety the overriding equity" and Justice Barrett (joined by
the Chief Justice and Justice Kavanaugh) calling the parents' likelihood of
success "dictated by existing law." The facts here — a girl digitally
penetrated by a male opponent during a sanctioned girls' match, then told by
her principal "that's wrestling" — are as sympathetic as an emergency
application gets. Counsel of record (Bursch) is a repeat Supreme Court advocate
and ADF has won on this docket before. The ask is modest and administrable:
let one student decline matches against male athletes without a recorded loss.
The Ninth Circuit's grounds, as described, are vulnerable — a "doubly
demanding" mandatory-injunction standard this Court has never endorsed, and a
reliance on disputed facts that B.P.J. treated as legislative. A requested
response confirms the Circuit Justice did not treat it as frivolous.

**Down, substantially.** The posture is the hardest on the Court's emergency
docket: a first-instance injunction pending appeal, where the applicant's right
must be indisputably clear and the Court is writing relief no lower court
entered. Mirabelli was the opposite shape — vacating a stay to restore a
permanent injunction entered after a full merits process — and Justice
Barrett's concurrence leaned on exactly that. Her Does v. Mills concurrence
(2021, with Kavanaugh) warned against using an application to give the Court's
"first view" of a novel merits question; both claims here are extensions: the
Title IX claim runs into the question B.P.J. reserved, and the parental-rights
claim moves Mirabelli from concealment of a child's mental-health condition to
scheduling of athletic contests, a step the Ninth Circuit found distinguishable.
Two courts found factual disputes on the Title IX merits. The state's position
(it does not know athletes' sex and cannot opt K.M.K. out without disclosing
other students' information) gives the Chief Justice and Justice Barrett an
administrability reason to leave the matter to the Ninth Circuit's expedited
appeal, with the applicants free to file a certiorari petition. And a grant
that is partial — relief on the opt-out but not on notice or on any
Title IX-based ground — resolves as ungranted under the denial-first collapse.

**Net.** I think Thomas, Alito, and Gorsuch grant; Kavanaugh probably grants on
the Labrador v. Poe logic (likely cert, likely reversal, irreparable harm); the
Chief Justice and Justice Barrett are the question, and I put the chance they
both join a grant at roughly 0.4. Discounting for a mixed order and for the
cert-before-judgment-without-injunction route leaves **0.35** for an
unqualified grant. `granted` is 0 and `predicted_disposition` is `denied`
because denial is the modal outcome; `interim-disposition` restates 0.35.

## The ladder claims

- **response-requested-increment 0.02** — already fired; vacuous for this cell.
- **referral-increment 0.88** — the near-universal path for a contested
  substantive application of this profile, and Justice Kagan referred
  Mirabelli. The residual is a chambers denial.
- **amicus-increment 0.85** — three organized amici (a multistate coalition,
  Women's Liberation Front, Do No Harm) filed in the Ninth Circuit within a week
  of the motion there; the window before disposition is three to five weeks;
  submitted briefs count.

## Votes and stakes

The vote block is unscored at this stage and is my modal 5–4 denial lineup
(Alito writing); it is banked, not a confident call. `big_case_score` 0.7: a
nationally watched issue with 22 states' policies implicated and a plausible
future certiorari vehicle, but individual relief sought.

## Where to discount me

I have not read the Ninth Circuit's order or the district court's opinion
directly — CourtListener holds no text for the published order and the
appendix fell outside the truncated application — so my read of their grounds
is the applicants' read. My knowledge of B.P.J. is likewise mediated by the
application. The corpus `query` surface returned no comparable private-applicant
injunction priors, so the applicant-class and ladder-conditioned adjustments
rest on training knowledge of the Court's practice, not a committed cut. The
largest single uncertainty is whether the Chief Justice and Justice Barrett
read this as Mirabelli (dictated by existing law) or as Does v. Mills (a first
view on a novel claim); the number would move to roughly 0.55 or 0.2
respectively if I knew.
