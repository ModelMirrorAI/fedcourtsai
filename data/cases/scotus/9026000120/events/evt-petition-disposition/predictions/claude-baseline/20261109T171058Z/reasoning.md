# Reasoning — scotus/9026000120 (No. 26-120), evt-petition-disposition

**P(grant) = 0.12; predicted disposition: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-11-09.json`: paid petition (Institute for Free Speech) from CA10 (No. 24-1473, decided Mar. 10, 2026; en banc denied Apr. 23, 2026). Four amicus briefs (Women's Declaration International USA; LGB Courage Coalition et al.; Foundation for Moral Law; Women's Liberation Front). BIO filed Sep. 25; reply Oct. 9. Distributed for the 11/6/2026 conference, **rescheduled** Nov. 5, then redistributed Nov. 9 for the 11/13/2026 conference. `distribution_count` = 2. No CVSG.
- `record/context.json`: forward mode, band `elevated` (sal-v8), `cert_anchor.rate` = 0.248 (10-Term pooled reached rate).
- Documents: questions presented, petition (truncated at the appendix), BIO and cert reply. All had text; none were OCR-derived.
- `same-question.json`: no petition scored above the 0.5 threshold, so I have no companion or hold signal.

## Anchor and adjustments
- I anchored on the elevated band's reached rate of about 25%. The amicus cut points the same way: the 2+ bucket's grant family is about 22.7%.
- **Down: the band overstates this case.** The elevation comes from a reschedule *before the first conference*, which the dist-v2 count reads as a relist (the statpack caption warns about this). The petition has not actually been conferenced and relisted. A pre-conference reschedule often means one Justice is looking closely, and that frequently leads to a dissent from denial rather than a grant. The four amici are ideologically aligned advocacy groups, not institutional or governmental ones.
- **Down: merits and vehicle problems.**
  - QP1 asks the Court to hold that legislative immunity does not reach official-capacity equitable claims. That runs straight into *Supreme Court of Virginia v. Consumers Union* (1980), which applied legislative immunity to declaratory and injunctive relief. Petitioners rely mainly on *Kentucky v. Graham* and *Hafer*.
  - The BIO argues credibly that the claimed 4-2 split is thin: *Bols* is unpublished, and the *Minton*/*Schmidt* readings are contestable. The reply's best point is that the BIO concedes some disagreement on scope.
  - The district court gave an alternative ground: the prospective claims were moot. That would complicate review.
  - Judge Carson concurred in the judgment, so the panel was unanimous on the result.
- **Up: the subject matter.** A facially viewpoint-based "misgendering" decorum rule is the kind of First Amendment issue some Justices want to reach. QP2 (whether *enforcing* a speech rule is a legislative act) is a cleaner question.
- **Net:** I moved from 0.25 to 0.12. That is still well above the roughly 1–2% paid baseline because of the reschedule and the amici.

## Other claims
- **relist-increment, 0.35:** the petition is set for 11/13. A further relist would most likely come from a Justice writing a dissent from denial or holding it for a closer look.
- **dissent-from-denial | denial, 0.30:** the reschedule plus the speech subject matter make a writing (Thomas, Alito or Gorsuch) materially likely.
- **cvsg-increment, 0.02:** the respondents are state legislators and no federal interest is in play.
- **summary-disposition-route | grant, 0.10:** I see no intervening decision that would support a GVR, and a summary reversal on immunity is possible but unlikely.

## Where to discount me
I have no lower-court docket or decision-below file beyond the petition appendix, and I made no retrieval of outside commentary. The size of the reschedule signal is my own judgement; no table conditions on it.
