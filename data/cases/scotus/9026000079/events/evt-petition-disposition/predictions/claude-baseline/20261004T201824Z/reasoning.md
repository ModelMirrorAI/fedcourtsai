# Rationale for the numbers

**P(any grant) = 0.02.** Predicted disposition: denied.

## What I read

- The provisioned snapshot, `2026-10-04.json` (supremecourt.gov payload created
  09/29/2026). Paid petition, docketed July 17, 2026 (petition filed April 7,
  2026; paper-form-only filing). Respondent waived the right to respond on
  August 14, 2026. One distribution, for the conference of 9/28/2026. No CVSG,
  no response requested, no redistribution. Petitioner: Rene Acosta-Tapia, a
  private individual represented by a Tucson solo practitioner. Respondent: the
  Attorney General (Solicitor General as counsel of record).
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, `cvsg_date` null, Term 2026. No `record/documents/`
  directory was provisioned, so I had no petition text, no questions presented,
  and no brief in opposition (there is none; the government waived). The
  supremecourt.gov docket page links no petition PDF, which is consistent with
  the Rule 34.6 paper-only entry, so the QP is genuinely unavailable rather
  than fetch-failed.
- The Ninth Circuit memorandum disposition, No. 25-2460 (Jan. 15, 2026;
  Hawkins, Rawlinson, Bress; unpublished; submitted without argument), fetched
  from the Ninth Circuit's datastore. Panel rehearing was denied Feb. 26, 2026.
- The live supremecourt.gov docket page for 26-79 as of today, which showed
  nothing after the August 19 distribution entry: no grant, denial, relist, or
  response request. This is a forward cell and the petition is genuinely
  pending, so no mis-provisioning flag is owed.

## What the case is

Acosta-Tapia, a Mexican national with a reinstated removal order (entered
November 18, 2022), petitioned for review of an IJ's affirmance of DHS's
negative reasonable-fear determination, filing within 30 days of the IJ's
order (April 16, 2025). The Ninth Circuit dismissed the petition as untimely:
under *Riley v. Bondi*, 606 U.S. 259 (2025), the "order of removal" is the
reinstated removal order, so the 30-day clock of § 1252(b)(1) had run in 2022.
Because the deadline is a claims-processing rule that the government invoked,
the panel enforced it. It declined to reach equitable tolling (not
"specifically and distinctly" argued) and the argument that *Riley* should not
apply retroactively (no authority cited). It then held in the alternative that
substantial evidence supported the negative reasonable-fear determination on
both withholding (no nexus; no government involvement or acquiescence) and CAT
(no acquiescence). The National Immigration Litigation Alliance tried to file
an out-of-time amicus brief below and was refused.

## Anchor

Band `baseline` under `sal-v4`, which matches the statpack's segment table
heading, so the table is my anchor. Pooling the bracketed `reached` figures for
`baseline` over Terms 2017 through 2025 (strictly before this case's Term 2026)
gives about **5.0%** (weighted over n = 12,720). The modern-cert anchor for a
Ninth Circuit petition is about 2.1% granted plus 1.1% GVR; the relist-0 cut's
1.2% granted / 0.5% GVR is the terminal-count rate and understates a live
petition's prospects, so I did not anchor on it.

## Adjustments

Down, substantially, from 5.0% to about 2%:

- **The Solicitor General waived**, and the Court did not call for a response
  before the conference. The Court essentially never grants a paid petition
  against the United States without first obtaining a brief in opposition; a
  grant here would first require a call for a response, and the live docket
  shows none as of today. This is the dominant signal.
- **Vehicle quality is poor.** The decision is an unpublished memorandum; the
  two arguments that could make the post-*Riley* question cert-worthy
  (equitable tolling and non-retroactivity) were held forfeited; and the panel
  rejected the merits in the alternative, so even a petitioner win on
  timeliness would change nothing in the case. Each is an independent reason
  for the Court to wait for another vehicle.
- **No split is visible.** Circuits applying *Riley* to pre-*Riley*
  reinstatement petitions are still working out tolling; I am aware of no
  developed conflict, and with no petition text I cannot credit one the
  petitioner may have asserted.

Up, slightly, from where those factors alone would leave it (well under 1%):

- The timeliness question is real and recurring. *Riley* itself acknowledged
  the practical trap for withholding-only litigants, and the organized
  immigration bar (NILA's attempted amicus below) is tracking the issue. If the
  Court takes a better vehicle in the next year or two, a petition like this
  one could be held and GVR'd, which counts as a grant on the binary axis. The
  `summary-disposition-route` figure of 0.7 reflects that nearly all of the
  grant mass runs through that hold-and-GVR path rather than plenary review.

## The other claims

- `relist-increment` 0.12: the snapshot shows one distribution. Most baseline
  petitions with a government waiver are denied at their first conference. The
  paths to a second distribution are a post-conference call for a response
  (followed by redistribution) and a hold for a companion case; I weight them
  at roughly 8% and 4% respectively.
- `cvsg-increment` 0.005: the United States is the respondent. A CVSG is
  structurally impossible; the number is non-zero only for the resolver
  reading a response request or some other entry as a CVSG.
- `dissent-from-denial` 0.03: no Justice is likely to write on an unpublished,
  forfeiture-laden immigration petition that the government did not even
  answer.
- `big_case_score` 0.25: scored on stakes if decided, not grant odds. A
  decision on *Riley* retroactivity and tolling would matter to a sizable class
  of noncitizens in reinstatement proceedings and to the immigration bar; it
  is not a case of broad public salience.

## Uncertainty and where to discount me

- I never saw the petition. If it frames a genuine circuit conflict on
  post-*Riley* tolling, or if the Court has independently flagged this issue,
  the call-for-response probability (and so the relist number) should be
  higher than I have it. The grant number is less sensitive, because the
  vehicle defects are in the Ninth Circuit's opinion, not the petition.
- Timing: the long-conference order list is imminent. If the Court requests a
  response on that list, the relist claim resolves true and the grant
  probability should be re-read upward (roughly to the 5-8% range), but the
  denial remains the most likely terminal outcome.
- I did not read the earlier arrival-moment predictions for this docket; this
  forecast is from the distribution-moment record alone.
- Corpus tooling: two `fedcourts query` calls returned recency-ranked 2020s
  rows that did not add to the statpack's cuts; the anchor rests on the
  committed statpack, read today.
