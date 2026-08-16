# Rationale — P(disturbed) = 0.80, judgment = reversed

## Anchor

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count (67), so its rate is quotable and is the registered
baseline. My case's grant Term is OT2025 (petition granted 2026-04-06). The
ten-Term pool strictly before it is grant Terms 2015–2024; the pack holds
2017–2024, so the shown window is my window. Pooled disturbed over parsed:
(50+34+49+46+57+42+50+31) / (73+55+72+65+69+54+75+52) = **359/515 ≈ 69.7%**,
comfortably past the 30-parsed-judgment floor (coverage: 515 parsed of 557
granted across those Terms). That is the bar my Brier skill is scored against.

## Adjustments up from 0.70 to 0.80

- **The decision below sits on the short side of a lopsided, acknowledged
  split.** Per the petition, six circuits (2d, 6th, 7th, 9th, D.C., and
  others) hold that §511(a) does not bar district-court jurisdiction over
  facial constitutional challenges to veterans'-benefits statutes; the
  Eleventh Circuit joined only the Eighth in rejecting that majority rule,
  and acknowledged the break. The Court more often takes the minority-rule
  side of a split to correct it.
- **On-point unanimous precedent the statute preserved.** *Johnson v.
  Robison* (1974) held the predecessor no-review clause did not reach
  constitutional challenges to acts of Congress, and the VJRA carried forward
  the exact "decision[s] ... under" language *Robison* construed; the House
  Report called *Robison* "clearly correct." Affirming requires either
  overruling or sharply confining a unanimous precedent Congress ratified.
- **Doctrinal trend.** *Axon v. FTC* (2023, 9–0) and the Court's recent
  channeling cases have run toward preserving district-court jurisdiction
  for structural/constitutional claims the agency scheme cannot meaningfully
  review; the Board of Veterans' Appeals cannot hold a statute
  unconstitutional in any ordinary sense.
- **Advocacy and amici.** Petitioner is represented by the Stanford Supreme
  Court Litigation Clinic (Anand, Fletcher, Karlan) with Bondurant Mixson;
  nine merits amicus briefs were filed, all on petitioner's side and spanning
  the ideological spectrum. No amicus supported respondent.
- The Court granted quickly (two distributions, no relist, no CVSG) over the
  SG's opposition — consistent with a Court that saw a clean error to fix.

## What holds the number at 0.80 rather than higher

- **The SG's textual argument is not frivolous.** The merits brief (provisioned
  text, filed 2026-07-13) argues §511(a)'s post-VJRA phrase "all questions of
  law ... necessary to a decision by the Secretary *under a law that affects
  the provision of benefits*" is materially broader than §211(a), that the
  Federal Circuit's §7292(c) authority to decide statutory "validity" shows
  constitutional questions were channeled, and that unlike in *Robison* the
  channel now ends in real judicial review. *Elgin v. Department of Treasury*
  (2012) channeled facial constitutional claims on a similar theory.
- **Vehicle wrinkles.** Petitioner sued Congress pro se; the Eleventh
  Circuit's first holding was sovereign immunity. The Court could resolve the
  case in a way that leaves the judgment standing (a DIG if the vehicle
  sours), though the futility holding below makes the QP genuinely
  outcome-determinative. I put the combined undisturbed tail (affirmance +
  DIG) at ~0.20.
- The base-rate pool itself says ~30% of argued cases end undisturbed even
  when the smart money says otherwise.

## Coherence of the fields

`probability` = 0.80 = P(disturbed); `granted` = 1 (I predict disturbance);
`judgment` = `reversed` (vacatur is the runner-up label but also counts as
disturbed, so the binary is robust to that label uncertainty);
`predicted_disposition` = `other` per the merits-stage convention; the single
declared claim `judgment-disturbed` restates 0.80 exactly.

## Votes

All nine predicted `majority`: the modal outcome is unanimous (see
`predicted_reasoning.md`), and vote accuracy is intersection-only, so listing
the full bench with each Justice's individually-most-likely vote maximizes
expected accuracy. I did not forecast writings; authorship has no observation
channel today.

## What I worked from, and uncertainty

Forward-mode cell; the judgment does not exist (argument is set for
2026-10-05, after my 2026-08-16 snapshot). I worked from the provisioned
snapshot and provisioned document texts: the petition (full), the
questions-presented section, and the respondent file — which usefully
contains the SG's *merits-stage* brief (its summary of argument was the basis
for my read of the government's position), not only the cert response. I did
not retrieve the parties' merits briefs beyond that, the amicus briefs' text,
or commentary; no argument transcript exists yet. My main uncertainties are
(a) how much traction the SG's "necessary to a decision" textual reading gets
with the Court's textualists, which is the difference between 9–0 and a
divided reversal, and (b) the salience of the sovereign-immunity vehicle
issue at argument. The cert-stage `band: elevated` in `record/context.json`
is a grant-likelihood construct for a question already settled; per the
prompt I did not anchor on it. One corpus `query` (a citation lookup on the
key precedents) returned empty against a noted coverage gap and contributed
nothing.
