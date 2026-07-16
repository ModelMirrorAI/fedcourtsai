# Garcia v. Hobbs, No. 25-901 — cert petition disposition

**Prediction: grant-side, most likely a GVR. P(any grant, GVR included) = 0.55; predicted disposition `gvr`.**

## The case

Benancio Garcia III, a Hispanic resident of Washington's Yakima Valley, challenged
Legislative District 15 as a racial gerrymander under the Equal Protection Clause. A
three-judge district court (Estudillo, Lasnik, VanDyke) dismissed his claim as moot after
Judge Lasnik — sitting alone in the parallel VRA §2 case, *Soto Palmer v. Hobbs* —
enjoined LD-15 and ultimately drew a court-ordered remedial map (LD-14) with avowedly
race-conscious lines. Judge VanDyke dissented at length, on both mootness and the merits.
After a first trip to the Supreme Court (No. 23-467, vacated and remanded on
jurisdictional grounds, 144 S. Ct. 994 (2024)), the Ninth Circuit affirmed the mootness
dismissal in a three-page unpublished memorandum (Aug. 27, 2025).

The question presented: whether an Equal Protection racial-gerrymandering claim is mooted
when the challenged district is replaced, in a *different* proceeding, by a judicial
remedy that intensifies the plaintiff's racial-classification injury and remains subject
to appellate review. The petition leans on *North Carolina v. Covington* (the segregation,
not the line-drawing, is the injury) and *Moore v. Harper* (no mootness while appellate
reversal could snap the old map back), and stresses that the State conceded below that
reversal in *Soto Palmer* would "resuscitate" Garcia's claim.

## Docket signals (from the provisioned snapshot, 2026-07-16)

- **Paid** petition, Term 2025 (25-901); elite election-law counsel (Holtzman Vogel;
  Torchinsky as counsel of record).
- Respondents **waived**; the Court **called for a response** (Mar. 25, 2026) after one
  reschedule and two conference distributions — a Court-initiated CFR is a classic
  above-baseline interest signal.
- Response extension granted in part; State's brief in opposition filed June 2, 2026;
  reply June 10; **distributed June 17 for the Sept. 28, 2026 long conference**.
- Linked with 25A482 (the extension application); the Court has already intervened once
  in this very litigation (the 2024 vacate-and-remand).

## Decisive external context (forward mode; see retrieval.md)

1. **Louisiana v. Callais, No. 24-109, decided April 29, 2026** (6–3, Alito): the Court
   held Louisiana's §2-driven second majority-minority district an unconstitutional racial
   gerrymander and sharply narrowed §2 as a justification for race-based districting. This
   post-dates my training cutoff but pre-dates the snapshot — legitimate forward signal,
   and it transforms this cell: the *Soto Palmer* remedial map that grounds the mootness
   holding below is exactly the kind of race-predominant judicial remedy *Callais*
   condemns.
2. **The Court is already GVR-ing in *Callais*'s wake**: redistricting cases from
   Mississippi and North Dakota were vacated and remanded on May 18, 2026 for
   reconsideration under *Callais*.
3. **The companion petition, Trevino v. Hobbs, No. 25-918** (the *Soto Palmer*
   intervenors' challenge to the §2 judgment and remedial map, affirmed by the Ninth
   Circuit pre-*Callais*) is fully briefed on the same schedule (reply also June 10) and
   headed to the same long conference. **Washington — the respondent that won below —
   publicly urged the Court to grant it** (June 2, 2026). Judge Lasnik denied a
   post-*Callais* Rule 60(b) motion to dissolve the remedial map (May 18, 2026), and the
   Court **denied Trevino's motion to expedite on May 26, 2026** — so nothing moves before
   the 2026 cycle, and both petitions will be considered together on Sept. 28, 2026.

## Reasoning to a probability

Anchors first. The modern paid-petition grant rate is ~5.4% (statpack, Term 2025 paid
class; the all-cert anchor is ~2.5–3.3%). The committed statpack has no salience-band
table, but its signal cuts point the same way: petitions that draw Court-initiated
engagement (relists; CVSG at 27% grant) run an order of magnitude above baseline, and a
CFR after waiver plus a reschedule puts this petition well inside that engaged tail.
This cell then carries case-specific signals far stronger than any statpack cut:

**Toward a grant-side outcome:**
- The judgment below is expressly premised on the vitality of a §2 remedial map of the
  very kind *Callais* just held unconstitutional; the Court is actively GVR-ing
  pre-*Callais* redistricting judgments.
- If the Court disturbs *Trevino* (GVR or plenary grant-and-reverse), the mootness
  premise collapses — and Garcia cannot simply resume his dismissed case unless the
  mootness judgment is undone, which is precisely what a GVR accomplishes cheaply. A
  joint disposition (GVR both) is the tidy judicial-administration move.
- The State itself supports review of the companion; even the winner below wants the
  post-*Callais* question resolved.
- The CFR, the earlier reschedule, the prior vacate-and-remand in this same litigation,
  and VanDyke's roadmap dissent all show sustained attention.

**Toward denial:**
- Garcia's own QP is a splitless, fact-bound mootness question resolved in an unpublished
  memorandum — standing alone, a routine denial.
- The Court may deny *Trevino* and let the Rule 60(b) route (now on appeal-track before
  the Ninth Circuit) absorb *Callais* first; Garcia would then surely be denied.
- Even if *Trevino* is granted plenary, the Court could hold Garcia and later deny if
  relief arrives through *Soto Palmer*'s collapse.
- The expedite denial confirms no urgency; the 2026 elections proceed under LD-14 either way.

Rough tree: P(*Trevino* GVR) ≈ 0.55–0.60 with Garcia riding along grant-side ~0.6 of the
time; P(*Trevino* plenary grant) ≈ 0.20 with Garcia held and eventually GVR'd on likely
reversal (~0.65); P(*Trevino* denied) ≈ 0.20–0.25 with Garcia following to denial. That
yields ≈ 0.50 grant-side; the engagement signals (CFR after waiver, prior intervention in
this litigation, the near-zero cost of a companion GVR) justify nudging to **0.55**.

Disposition-label decomposition: `gvr` ≈ 0.43, plenary `granted` (possibly consolidated
with or held for *Trevino*) ≈ 0.10, `granted-in-part` ≈ 0.02, `denied` ≈ 0.43,
`dismissed`/`other` ≈ 0.02. On the binary axis grant-side edges denial, and within the
grant side a *Callais*-driven (or *Trevino*-driven) GVR is much likelier than plenary
review of the mootness QP itself — hence `granted=1`, `predicted_disposition=gvr`.

Timing note: distribution is for the Sept. 28, 2026 long conference; if Garcia is held
for *Trevino*, final disposition could slip well into OT2026. The prediction is of the
ultimate disposition, whenever it lands.

No per-justice votes are predicted: cert-stage votes are not reliably observable, and for
a likely per curiam GVR they would be uninformative.

**Inputs relied on:** the provisioned snapshot (2026-07-16), `questions-presented.txt`,
`petition.txt` (43 pp., read in full), the committed `metrics/statpack.md`/`.json`
(paid-class base rates), and the forward retrievals in `retrieval.md`. The State's brief
in opposition appears on the docket (filed June 2, 2026) but was **not** among the
provisioned documents, so the BIO's arguments are not directly weighed (flagged in
`flags.json`); the State's bottom line is partly reconstructable from its concessions
quoted in the petition and its public cert-stage posture in *Trevino*.
