# Parker v. Gates, No. 25-882 — cert disposition prediction

**Bottom line: deny is the modal outcome, but this petition carries genuinely
elevated grant-side risk. P(any grant, GVR included) ≈ 0.20; predicted
disposition: denied.**

## The case

Petitioners Andrew D. Parker and Parker Daniels Kibort, LLC were counsel to
Kari Lake and Mark Finchem in *Lake v. Hobbs* (D. Ariz. 2022), a pre-election
challenge to Arizona's use of electronic vote tabulation. After the complaint
was dismissed for lack of standing, the district court imposed $122,200 in
Rule 11 and 28 U.S.C. § 1927 sanctions on counsel, stating (among other
grounds) that sanctions would "send a message to those who might file
similarly baseless suits in the future." A divided Ninth Circuit panel
affirmed (130 F.4th 1064, Bumatay, J., dissenting); rehearing en banc was
denied over a published 21-page dissent by Judge VanDyke joined by five other
judges (148 F.4th 1110), which accused the district court of "weaponization of
sanctions to chill politically disfavored litigation."

The petition (filed Jan. 16, 2026, by Nathan Lewin) presents four questions:
(1) may a court sanction attorneys to "send a message" against politically
disfavored suits; (2) may it sanction novel/long-shot legal arguments; (3) may
it construe a complaint in the light *least* favorable to counsel for Rule 11
purposes; and (4) is a preliminary-injunction motion sanctionable under
*Purcell* when heard ~4 months pre-election and seeking relief for future
elections too. It asks primarily for **summary vacatur** (a *McKnight*-style
GVR adopting the en banc dissent), or alternatively plenary review. It leans
heavily on the intervening decision in *Bost v. Illinois State Board of
Elections*, No. 24-568 (Jan. 14, 2026), which held candidates have standing to
challenge election procedures pre-election.

The BIO (Maricopa County, June 22, 2026) answers that the sanctions rest on
findings — affirmed under abuse-of-discretion review — that counsel made
**objectively false factual assertions** (that Arizona does not use paper
ballots; that its equipment is untested), persisted after a Rule 11 warning
letter, and that the district court repeatedly gave counsel the benefit of the
doubt. It argues the case is fact-bound, presents no circuit split, that
*Bost* is inapposite (it concerns standing, not sanctions for false factual
allegations), and that the *Purcell* question is waived and non-dispositive
because the § 1927 sanctions have independent bases. It notes the related
merits petition (*Lake v. Fontes*, No. 23-1021) was already denied.

## Docket signals (snapshot of 2026-07-16)

- **Paid** petition, Term 2025, out of **CA9**.
- Extension to file granted by Justice Kagan (circuit justice routine).
- Distributed for the 3/27/2026 conference; on **3/23/2026 the Court called
  for a response** (respondents had not filed one) — the single strongest
  grant-side signal on the docket. A CFR means at least one chamber took
  interest; grants among paid petitions are heavily concentrated in the
  CFR'd pool.
- Response twice extended, BIO filed 6/22/2026; **redistributed for the
  9/28/2026 long conference**. No relist yet — the pre-CFR distribution
  doesn't count as a considered conference.

## Base rates and adjustments

From the committed statpack (`metrics/statpack.md`): modern discretionary-cert
petitions resolve **~95% denied**; recent-Term grant rates 2.5–3.3%; CA9-
originating petitions grant ~3.0%. The statpack has no CFR cut, but the
relist/CVSG cuts show how sharply court-initiated attention shifts the odds
(1 relist → 7.6% grant, 2 relists → ~34%, CVSG → 27%). Public empirical work
on CFRs puts the conditional grant rate for CFR'd paid petitions roughly an
order of magnitude above baseline (low-to-mid teens).

Starting from ~3% and adjusting:

**Toward grant:**
- The CFR (≈ ×4–6 on its own).
- A published six-judge CA9 en banc dissent — a signal this Court has
  repeatedly responded to, and here written expressly as a cert invitation.
- A cheap disposition path: the petition's lead ask is summary vacatur/GVR,
  which needs less institutional investment than plenary review; *Bost*
  (decided two days before filing) gives a colorable intervening-decision
  hook, and several justices have voiced concern about sanctions chilling
  advocacy.
- Capable, veteran Supreme Court counsel and a well-framed "weaponization"
  narrative keyed to the district court's own "send a message" language.

**Toward denial:**
- Sanctions review is quintessentially fact-bound abuse-of-discretion
  territory; the Court almost never grants Rule 11/§ 1927 cases (its last
  cluster was 1989–92), and the asserted circuit conflict on construing
  pleadings under Rule 11 is thin.
- Serious vehicle problems: the affirmed findings are that counsel made
  demonstrably false statements of fact (paper ballots, equipment testing)
  and persisted after a Rule 11 letter — grounds *Bost* does not touch, so a
  *Bost* GVR would likely not change the outcome below; the *Purcell*/§ 1927
  question is arguably waived and non-dispositive.
- The Court denied cert on the merits track of this same litigation
  (No. 23-1021).
- Only 6 of 28 participating active judges joined the en banc dissent.
- Optics: relief for attorneys sanctioned for false allegations about voting
  machines in 2020-era election litigation is unattractive even to justices
  sympathetic to the chilling concern — the cleanest way to voice that concern
  is a dissent from denial, which costs the Court nothing.

## Net assessment

The CFR plus the en banc dissent put this petition well into the small
high-attention pool from which grants are drawn, and the long-conference
setting is where such petitions get their close look. But the BIO's
vehicle attack is strong: the false-statement findings are independent of
every question presented's framing, and the Court has no appetite for
error-correction in sanctions cases absent a clean split. I estimate
P(any grant, including summary vacatur/GVR) ≈ **0.20**, decomposed roughly as
plenary grant 0.07, GVR/summary vacatur 0.10, granted-in-part 0.03 — the GVR
path (in light of *Bost*, or a *McKnight*-style vacatur) is the likeliest
grant-side form, which is why `probability` (0.20) reflects the GVR-inclusive
binary. Modal single disposition: **denied** (~0.77), with a meaningful chance
the denial comes with a written dissent from denial. Residual mass on
dismissed/other ~0.03.

A relist after the 9/28/2026 conference would move my estimate up materially
(toward ~0.35 after one relist, higher if repeated); a straight first-look
denial at the long conference is the single most likely docket path.

## Big-case score

0.55 — the parties (Kari Lake's former counsel), the subject (sanctions for
2020-style election-machine claims), and the "weaponization of sanctions"
framing guarantee substantial press and bar attention if the Court acts, and
any merits ruling would reshape sanctions exposure in politically charged
litigation. It is nonetheless a procedural/attorney-discipline dispute, not a
structural election-law case, so it sits in the upper-middle band rather than
the top.

## Inputs used

- Snapshot `data/cases/scotus/73280380/record/snapshots/2026-07-16.json`
  (docket entries, fee class, term, distribution history).
- Provisioned documents: `questions-presented.txt`, `petition.txt` (23 pp.),
  `brief-in-opposition.txt` (38 pp.) — all non-empty, non-truncated.
- `metrics/statpack.md` base rates (modern discretionary-cert slice, CA9 cut,
  relist/CVSG cuts, per-Term grant rates).
- Mode: `forward` (pending case; conference date 9/28/2026 postdates this
  run). No outcome exists to leak.
