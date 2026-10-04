# Reasoning for my numbers

**P(grant) = 0.13; predicted disposition: denied.**

## What I read

- Snapshot `record/snapshots/2026-10-04.json` (the file `context.json` names).
  Paid petition docketed Aug 12, 2026, from the Fifth Circuit (No. 24-10708,
  published at 168 F.4th 713; rehearing en banc denied Apr 10, 2026 with no poll).
  BIO filed Aug 24 (early, waiving nothing — respondents chose to engage), reply
  Sep 4, distributed Sep 9 for the Sep 28 conference. Two amicus briefs in support
  (Airlines for America, by Skadden; International Franchise Association). Counsel
  of record for petitioner is a former Solicitor General (Jones Day); for
  respondents, an experienced Supreme Court advocate (Schaerr | Jaffe).
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, no CVSG, Term 2026, `signals_observable` true.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (50 pp.) and
  `brief-in-opposition.txt` (49 pp.), all with text (`empty_text: false`,
  none truncated). I read both briefs in full. The reply brief is on the docket
  but was not provisioned and I did not fetch it.

## Anchor

The salience table's version (`sal-v4`) matches my context's, and my band
(`baseline`) is a column, so the anchor is the bracketed `reached` rate for
`baseline` pooled over the Term rows strictly before 2026 (2017–2025, all nine
rendered prior Terms). Weighting each Term's bracketed rate by its risk-set `n`
gives roughly 5.4% (about 637 grants over about 11,720 petitions that reached the
band). The relist-count cut's relist-0 row (granted 1.2% + GVR 0.5%) is the
terminal-state figure and understates a live petition's prospects, as the prompt
warns; I did not anchor on it. The modern-cert overall grant family is a few
percent; the Fifth Circuit's bucket (granted 1.6%, GVR 2.1%) is unremarkable.

## Adjustments up from 5.4%

1. **Petition quality and signals.** Former SG as counsel of record, two trade
   association amicus briefs at the cert stage, a published opinion with a
   separate writing (Judge Willett concurring only in the judgment and voicing
   "serious reservations" that sincerity can be resolved "in one stroke," and
   stating that under the majority's approach "no putative class would ever fail
   the commonality requirement"). Amicus support and a separate writing below are
   among the strongest observable pre-conference grant correlates for a paid
   petition.
2. **Subject matter.** Rule 23 commonality/predominance after Wal-Mart, Amgen,
   Halliburton and Tyson Foods is an area the Court repeatedly polices, usually
   on Rule 23(f) interlocutory appeals (Wal-Mart, Comcast, Tyson Foods, and most
   recently Lab Corp v. Davis in OT2024, granted and then dismissed as
   improvidently granted). The "class rostering" procedure the Fifth Circuit
   directed is genuinely novel and gives the Court a concrete, quotable error to
   correct. Interlocutory posture is therefore not a strong negative here.
3. **A plausible hold.** The petition asks in the alternative for a hold pending
   the anticipated *Detwiler* petition (Ninth Circuit, religious-versus-secular
   belief under Title VII, en banc denied over eight dissents). A hold that ends
   in a GVR counts as a grant. I weight this small (about one point) because the
   *Detwiler* petition was due Aug 13, 2026 and would not have reached conference
   by Sep 28, and because *Detwiler* goes to sincerity only, which both Judge
   Willett and the BIO say is not necessary to sustain certification.

Together these would put a petition of this profile well above the band rate —
on their own I would be at roughly 0.18–0.22.

## Adjustments down

1. **The split is soft.** The petition's circuit conflict is built from general
   articulations of the "one stroke" rule (Speerly, Allstate, Parsons) plus
   cases where no common policy existed (Davis v. Cintas, Bolden, Ferreras,
   Stafford) plus district-court denials in COVID-accommodation class cases. The
   BIO's answer — these are the other side of the Wal-Mart line, there was a
   uniform company-wide unpaid-leave policy here, and residual individualized
   rebuttal goes to predominance under Halliburton — is a credible reading. No
   circuit has squarely held that a uniform-policy Title VII accommodation class
   fails commonality. The Court dislikes manufactured splits.
2. **Standard of review and vehicle.** The Fifth Circuit affirmed under abuse of
   discretion; the BIO presses the two-court rule and Rule 23(c)(1)(C)'s
   provisional nature, and Judge Willett himself joined the judgment on the
   deference ground. The Court can reasonably wait for the district court to
   build the trial plan and for a final-judgment appeal.
3. **Ideological cross-pressure.** The Justices most receptive to tightening
   Rule 23 for defendants are also the Justices most sympathetic to religious
   objectors to COVID-19 vaccine mandates. The BIO frames the petition as a
   request for a "per se bar" on religious-accommodation class actions and
   quotes the Fifth Circuit's refusal to "hinder the vindication of religious
   freedom." That framing lowers the chance of four votes relative to an
   otherwise identical securities or consumer class petition.
4. **Petitioner is a private party.** The caption class is private; the band
   anchor already reflects that, but it means no government-petitioner uplift.

## Net

I land at **0.13** — roughly 2.4 times the band anchor, below where the
quality signals alone would put it. Decomposed: about 0.05 for a grant announced
from the long conference without a relist, about 0.07 for a relist followed by a
grant, and about 0.01 for a hold-then-GVR. Confidence 0.6: the main uncertainty
is how the Court weighs the "class rostering" novelty against the religious
liberty valence, which I cannot read from the filings.

## The other claims

- **relist-increment 0.27.** One distribution shown. A relist happens on most
  grant paths (about 0.07 of my grant mass) and on a minority of denial paths
  for a petition of this quality (a Justice drafting a statement, or a hold
  being considered), which I put at about 0.20.
- **cvsg-increment 0.04.** No federal party; the question is Rule 23 procedure.
  The paid-segment CVSG rate is about 1.2% (173 of about 14,000 in the CVSG cut);
  I adjust up a little because the SG has Title VII views and the case is
  prominent, but a CVSG on a private Rule 23 dispute is rare.
- **summary-disposition-route 0.12 (conditional on grant).** The only summary
  path is hold-then-GVR after *Detwiler*; plenary review dominates the grant mass.
- **dissent-from-denial 0.10 (conditional on denial).** A statement respecting
  denial is conceivable (the Lab Corp dissenter's concern about uninjured class
  members maps onto the sincerity problem), but the religious-objector class
  makes a conservative dissent from denial awkward, and most denials of paid
  petitions carry no writing.
- **big_case_score 0.55.** A Rule 23 commonality ruling would be significant
  across class-action practice, and the vaccine-mandate setting is newsworthy;
  but it is a procedural, interlocutory question — not a top-tier case.

## Where to discount me

- I did not retrieve this docket's own state after the Sep 28 conference, by
  the prompt's rule against seeking the case's disposition or subsequent
  history; the forecast is from the provisioned baseline. Note that the corpus
  priors query I ran for context showed other petitions distributed for the
  Sep 28 conference carrying cert grants dated Oct 1, 2026, so the long
  conference's grant list had issued before this cell ran. I did not look for
  this case on it, and nothing in my inputs says whether it was on it (see
  `flags.json`).
- I could not verify the *Detwiler* petition's status: CourtListener's SCOTUS
  docket index returned nothing for it (nor for No. 26-183 itself), and the
  corpus query surface has no case-name filter. The hold weight (about one
  point) rests on the petition's own description.
- I did not read the Sep 4 reply brief or the Fifth Circuit opinion itself; my
  account of the decision below is from the parties' characterizations, which
  diverge on how much the panel relied on sincerity.
- Base-rate vintage: the committed `metrics/statpack.md` as checked in at run
  time; corpus rows read through the cell's service showed `last_live_polled`
  stamps up to 2026-10-04.
