# Reasoning — Trump v. Thakur, No. 26-210 (evt-petition-disposition)

**P(grant) 0.72.**

## Anchor
`record/context.json` (forward mode, sal-v6) freezes band `federal` with
`cert_anchor.rate` = 0.734 (federal band's bracketed *reached* rate pooled over
the 10 prior Terms; per-Term rows in `metrics/statpack.md` range 47.6%–96.2%,
n=12–41 each). The petitioner is the Solicitor General (D. John Sauer) for the
President and NSF/NEH, so the caption class is unambiguously federal. I start at
~0.73.

## Case specifics (petition, BIO, cert reply in `record/documents/`)
- QP (`questions-presented.txt`): whether the First Amendment prohibits the
  government from considering the viewpoint furthered by academic research
  projects when awarding or terminating competitive grants.
- Ninth Circuit (176 F.4th 1187, per curiam, May 26, 2026) affirmed a classwide
  preliminary injunction for the "Equity Termination Class" solely on First
  Amendment grounds, distinguishing *Finley*/*Rust* and drawing on *Rosenberger*.
- Pushing up: SG says the ruling conflicts with *Finley* and *Rust*; the issue is
  important and recurring (a long list of pending grant-termination suits, an
  S.D.N.Y. nationwide-class NEH ruling on appeal in the 2d Cir.); large sums
  are at stake; the Court has already dealt with related grant-termination
  disputes on its emergency docket (*NIH v. APHA*, 2025). The SG waived the
  Rule 15.5 14-day period so the case would be considered quickly, which points to
  a push for this Term. The reply notes the BIO does not dispute importance or
  vehicle quality.
- Pushing down: there is no circuit split (the BIO's main point, and the
  petition admits it); the posture is interlocutory (a preliminary injunction);
  the 2d Cir. appeals give the Court a reason to wait for more lower-court rulings
  or to hold the case. A Tucker Act / remedy-preclusion wrinkle exists, but the SG
  says it was not pressed as to this claim, so it should not get in the way. The
  government apparently did not seek an emergency stay of the Equity-class
  injunction here, which suggests it is less urgent.

On balance this is a typical strong SG petition. The adjustments cancel out
and I stay close to the anchor at 0.72.

## Other claims
- Docket shows **1 distribution** (conference of Nov 13, 2026), no relists, no
  CVSG. relist-increment 0.45: SG grants this Term often come at the first
  conference, but the Court also relists often before granting, and a denial
  with a written dissent would likely be relisted. CVSG 0.01, because the SG is
  the petitioner.
- summary-disposition-route 0.06: I see no intervening decision that would
  support a GVR. Summary reversal of a published interlocutory First Amendment
  ruling is unlikely when plenary review is on offer.
- dissent-from-denial 0.55 (given a denial): if this SG petition is denied,
  a written dissent is fairly likely (Alito, Thomas, Gorsuch). order-writers is
  the unconditional chance of writing on the disposing order. A grant order
  almost never carries writings, so these numbers are small.

## Uncertainty / discount
`same-question.json` lists no matching petitions. The federal-band anchor
rests on small per-Term samples. I did not check the Court's live docket
or the 2d Cir. appeals' status. The petition text was truncated at the
appendix, so I relied on the Ninth Circuit opinion only as the petition
describes it.
