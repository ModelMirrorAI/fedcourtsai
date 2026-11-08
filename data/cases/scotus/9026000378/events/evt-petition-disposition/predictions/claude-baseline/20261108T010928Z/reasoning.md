# Reasoning — scotus/26-378, Sessanga v. City of DeSoto Police Department

**P(grant) = 0.008; predicted disposition: denied.**

## Inputs used
- Snapshot `record/snapshots/2026-11-08.json`: a paid petition (`sJsonCaseType: Paid`) filed by a
  self-represented petitioner. The docket has two entries: the petition (response due Oct. 21, 2026)
  and "DISTRIBUTED for Conference of 12/4/2026." There is no brief in opposition, no waiver entry,
  no call for a response, no amicus brief, and no CVSG. Distribution count is 1.
- `record/context.json`: forward mode, band `baseline` (sal-v8), `cert_anchor.rate` = 0.0515
  (the reached rate pooled over 10 prior Terms).
- `questions-presented.txt`, `petition.txt`, `appendix.txt` (none truncated or OCR-derived). The
  decision below (App. A) is an **unpublished** Fifth Circuit per curiam (Elrod, C.J., Clement,
  Haynes; 5th Cir. R. 47.5). It affirmed a sua sponte dismissal of a § 1983 malicious-prosecution
  suit with prejudice, holding that the petitioner had pleaded his best case. Panel rehearing was denied on Nov. 17, 2025.

## Anchor and adjustments
- The anchor is the frozen baseline-band reached rate of about 5.2%. That figure is the whole private-class floor. It
  includes counselled petitions that later relisted or drew CVSGs, which is where most baseline-band
  grants come from.
- **Down, by a lot:** (1) the petitioner is pro se, and pro se paid petitions are granted far below
  the counselled rate. (2) The respondents filed nothing, and the Court has not called for a
  response. The Court almost never grants a petition without first asking for a response. (3) The
  decision below is unpublished and fact-bound. (4) The QPs are poor vehicles. QP1 attacks pre-service
  § 1915(e)(2) screening of a *paid* litigant's complaint, but the screening statute applies to IFP
  cases, and the Fifth Circuit rested on failure to state a claim after a chance to amend. The
  claimed Second/Seventh/Ninth Circuit split under *Leatherman* is a general pleading argument, not a
  clean conflict. QP2 (the independent-intermediary doctrine) touches a real area of doctrinal friction, since
  the Fifth Circuit's rule has drawn separate writings before. Here, though, it arrives through a
  pleading-sufficiency record. QP3 (whether a plea offer shows a lack of probable cause) is novel and fact-bound.
- The relist-count cut gives relist-0 denials at 96.8%, but this petition can still move. It would
  only move if a Justice asked for a response, which I put at about 4%.
- The final figure of 0.8% leaves a small chance of a call for a response followed by a GVR or
  summary action. The one plausible GVR hook would be a future intervening decision on malicious
  prosecution or independent intermediaries, and I know of none pending.

## Increments
- Relist increment, 0.04: an undisputed denial at the Dec. 4 conference is the overwhelming path.
  Another distribution would need a call for a response or a reschedule.
- CVSG, 0.002: no federal interest is involved.
- Summary route given a grant, 0.35: if a pro se petition is granted, a GVR or summary action is
  relatively likely. Plenary review is still slightly more likely.
- Dissent from denial, 0.01: a statement on the independent-intermediary question (Thomas, Sotomayor or Jackson) is
  possible but very unlikely on a pro se petition with no response.

## Uncertainty and caveats
- I did not independently check the timeliness question. The entry date is Feb. 6, 2026,
  within 90 days of the Nov. 17, 2025 rehearing denial, and docketing on Sept. 21 suggests the
  filing was corrected and refiled. Timeliness does not change the call.
- A single corpus query returned generic recent denials and was not informative. I relied on the
  statpack and the provisioned documents. I made no CourtListener or web lookups, because the
  provisioned record was enough for a call this lopsided.
