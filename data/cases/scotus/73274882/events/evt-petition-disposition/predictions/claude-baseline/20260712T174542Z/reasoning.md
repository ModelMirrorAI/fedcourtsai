# Duncan v. Bonta, No. 25-198 — cert petition disposition

**Prediction: granted — P(granted) = 0.72** (with roughly half of that mass on a
GVR-style summary grant rather than plenary review; see "Coding note" below).

## The legal question

Petitioners (represented by Clement & Murphy) challenge California Penal Code
§32310, which bans possession of ammunition magazines holding more than ten
rounds, including retrospectively. The questions presented are (1) whether a ban
on "exceedingly common" ammunition feeding devices violates the Second
Amendment under Heller/Bruen's common-use principle, and (2) whether
uncompensated forced dispossession of lawfully acquired magazines violates the
Takings Clause. The en banc Ninth Circuit upheld the ban 7–4 (133 F.4th 852,
Mar. 20, 2025), holding that 10+ round magazines are not "arms" under the plain
text and that, alternatively, the ban fits a historical tradition of regulating
especially dangerous weapons. This is the case's second trip: the Court GVR'd
it in light of Bruen in June 2022 (No. 21-1194).

## Base rate and where this case sits against it

The statpack's modern discretionary-cert anchor puts the grant rate at ~4.9%
(denied 92.6%), with Ninth Circuit petitions at ~5.3% granted. So the prior is
heavily deny. Everything that follows is about why this petition is far from
the base-rate population: it is a paid petition, from a final judgment on a
full record, with a 7–4 en banc split below, elite counsel, ~14 amicus briefs
at the cert stage (including a multi-state brief), and — decisively — a docket
history showing the Court has actively engaged with it for an entire Term.

## The facts that drive the prediction

1. **~24 conference distributions without a denial.** The petition was
   distributed for roughly two dozen conferences from 11/21/2025 through
   6/29/2026. Serial relisting at this scale means the Court was actively
   holding the case while it decided what to do with the hardware-ban issue —
   not that the petition was languishing.

2. **The intervening Benson split.** In early March 2026 the D.C. Court of
   Appeals held in Benson that D.C.'s materially identical 10+ round magazine
   ban *violates* the Second Amendment, expressly parting ways with the Ninth
   Circuit's decision in this very case (and with the D.C. Circuit's Hanson).
   Both parties filed supplemental briefs about Benson (Mar. 11/13, Apr. 23,
   2026). The BIO's lead argument — no genuine conflict, following the
   Snope/Ocean State/Hanson denials — was substantially weakened mid-pendency:
   there is now a square, acknowledged split on the ultimate question.

3. **The June 30, 2026 grants in the companion AR-15 cases, and the hold
   here.** At the same 6/29/2026 conference at which Duncan was last
   distributed, the Court granted cert in Viramontes v. Cook County (25-238,
   CA7, 22 distributions) consolidated with Grant v. Higgins (25-566, CA2, 17
   distributions), limited to whether the Second Amendment protects possession
   of AR-15-platform and similar semiautomatic rifles in common use — argument
   expected early in OT2026. The same day it *denied* other Second Amendment
   petitions (e.g., McCoy v. ATF, 25-24; WVCDL v. ATF, 25-132). Duncan — along
   with the other magazine-ban petitions, Gator's Custom Guns v. Washington
   (25-153) and NAGR v. Lamont (25-421) — received no order and shows no
   disposition on the docket as of the July 10, 2026 docket refresh. The Court
   plainly chose to *hold* the magazine cases pending the AR-15 decision
   rather than deny them at the end-of-term cleanup, which it could easily
   have done (and did do to Snope and Ocean State Tactical in June 2025).

4. **The hold pattern has a standard ending.** Petitions held for a pending
   merits case are, after the decision, either GVR'd (if the decision bears on
   the judgment below) or denied (if it does not help the petitioner). The
   granted question in Viramontes/Grant — common-use protection for the
   most popular semiautomatic rifles — directly implicates the Ninth Circuit's
   core holdings here: that common use is irrelevant at the plain-text step,
   that magazines (standard equipment on those same rifles) are not "arms,"
   and that a dangerousness tradition justifies banning commonly possessed
   hardware. If the Court rules for the challengers in Viramontes/Grant on
   common-use grounds (likely given the grant posture after 20+ relists, the
   Court's post-Bruen trajectory, and Kavanaugh's Snope statement that the
   AR-15 question would be addressed "in the next Term or two"), a GVR of
   Duncan is close to automatic — and an outright grant to resolve the
   now-live Benson split on magazines specifically is also plausible.

## Probability construction

- P(Viramontes/Grant is decided favorably to the challengers on grounds that
  bear on Duncan): ~0.78–0.80.
- P(Duncan is then GVR'd or granted plenary | favorable ruling): ~0.88. The
  residual is the scenario where the opinion is written so narrowly (rifles
  only, magazines expressly reserved) that the Court denies Duncan and lets
  the magazine question percolate — possible but in tension with the choice
  to hold rather than deny, and with the Benson split.
- P(Duncan granted anyway | unfavorable/narrow ruling): ~0.2–0.25 (the Benson
  split independently supports a later grant).

That yields ≈ 0.72 for grant (plenary or GVR), ≈ 0.26 for denial, and ≈ 0.02
for dismissal/other (e.g., mootness through legislative change — no sign of
that). The main scenario against: this Court has twice before relisted
magazine/AWB petitions at length and then denied (Harrel/Snope/Ocean State),
and it limited the Viramontes QP to rifles, arguably signaling it wants only
the rifle question for now. I weight that below the hold signal because those
prior denials predated both the Benson split and the Court's actual
commitment to the underlying common-use question.

**Timing:** resolution most likely comes at the end of OT2026 (June–July
2027), after Viramontes/Grant is decided; an earlier plenary grant at the
long conference (fall 2026) is possible but less likely.

**Votes:** omitted — the most likely disposition (GVR) produces no recorded
per-Justice votes. From the Snope/Ocean State denials, Thomas, Alito, and
Gorsuch are on record favoring review of hardware bans; Kavanaugh signaled
sympathy on the merits.

## Coding note

If the eventual order is a GVR ("petition granted, judgment vacated, case
remanded" — as happened to this same case in 2022), I treat that as
`granted` for this event, consistent with how the corpus derives disposition
from the cert-granted date. A plenary grant limited to QP1 would also be
`granted`. See flags.json.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-12.json`), the petition's
questions-presented section and petition text, and the brief in opposition
(`record/documents/`), plus the retrieval logged in `retrieval.md` (statpack
base rates, corpus priors — which surfaced the June 30 Viramontes/Grant
grants and same-day denials — and two web searches identifying Benson and the
scope of the Viramontes/Grant grant). Mode: forward (pending petition), so
retrieval was unrestricted; no outcome for this event exists to leak.
