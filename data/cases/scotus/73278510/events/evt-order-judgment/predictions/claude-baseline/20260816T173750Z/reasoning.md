# Rationale — P(disturbed) 0.45, judgment: affirmed

**Cell and mode.** Merits stage, `moment: grant` (evt-order-judgment), forward
mode — the judgment does not exist yet (argument is set for October 14, 2026).
I worked from the provisioned snapshot (2026-08-16), the provisioned cert-stage
documents (`questions-presented.txt`, `petition.txt`, and
`brief-in-opposition.txt` — whose text in fact concatenates the cert BIO with
Paramount's June 23, 2026 merits response brief, per the two URLs in
`documents.json`), and the committed statpack. I did not retrieve petitioner's
merits brief or the amicus briefs; petitioner's merits position is well
represented by the petition's full argument section, so the marginal value was
low. The forecast therefore rests on real merits-stage text for respondent and
cert-stage text for petitioner — a mild asymmetry a reader should know about.

**Baseline.** The statpack's "The merits docket (granted cases)" section
publishes an `excluded` count (67), so it is quotable and is the scored
baseline. The grant Term is OT2025 (cert granted January 26, 2026 — taken from
the event's `opened_at`, not the docket number). Pooling `disturbed` over
`parsed` across the ten grant Terms strictly before OT2025 (rows exist for
2017–2024; 2015–2016 carry no parsed judgments and are omitted from the
table): 359/515 = **69.7%**, well above the 30-parsed-judgment floor. Coverage
beside that figure: those Terms show 557 granted vs 515 parsed, so the pool is
nearly complete for the older Terms; the nearest Terms are the most censored.

**Adjustment down to 0.45.** I am forecasting materially below the pooled
disturb rate, for reasons specific to this grant:

1. **The Court's revealed pattern in repurposed-statute class-action cases.**
   Respondent's merits brief leads with Facebook v. Duguid (2021), where a
   unanimous Court adopted the narrow, defendant-side reading of an old
   privacy statute being repurposed by the class-action bar — the closest
   template for this case. TransUnion and Epic Systems point the same way.
   That pattern usually manifests as reversal because the defendant lost
   below; here the defendant *won* below, so the same disposition predicts
   affirmance.
2. **Split posture weakens the grant-implies-reverse inference.** This is a
   clean, acknowledged 2–2 split (CA2 Salazar v. NBA and CA7 Gardner v. Me-TV
   broad; CA6 here and CADC Pileggi narrow, with CA9 argued and pending). The
   Court had to take some vehicle regardless of direction, and it chose this
   one over the interlocutory NBA petition for final-judgment reasons
   petitioner himself argued — so the grant carries less directional signal
   than the average grant.
3. **The narrow side's textual case is strong on this Court's method.** The
   renter/purchaser/subscriber ↔ rental/sale/delivery parallel, the
   prepositional tether to the provider's defined capacity, and § 2710(a)(3)'s
   "specific video materials" limit are exactly the contextual arguments this
   Court's majority has favored over bare "any"-maximalism (Van Buren aside).
   Two circuits (including Judge Bloomekatz in dissent below and Judge
   Easterbrook in Gardner) show the broad reading is respectable — which is
   why I stay near the coin flip rather than lower.
4. **Advocacy and amicus asymmetry.** Clement & Murphy plus Weil (Silbert,
   Tripp) for respondent against a small plaintiff firm for petitioner; the
   merits amicus docket runs roughly 11 briefs on respondent's side (Chamber
   of Commerce, Meta, MPA/NCTA, retail and news-media groups) against two or
   three for petitioner (EPIC, Prof. Schwartz, LJC for neither party). Weak
   evidence individually, but it corroborates where the establishment thinks
   the Court is.

Against all that: the 69.7% base rate is a strong prior, the petition's
meaningful-variation and consistent-usage arguments are genuinely good, and a
Gorsuch/Kagan-led textualist coalition for reversal is a live path. Netting
these, my honest P(disturbed) is a bit below one half: **0.45**. Since the
likeliest single outcome is an affirmance, `judgment` is `affirmed` and
`granted` is 0; the alternative disturbed outcome would most likely be a
plain reversal. DIG and equally-divided outcomes are negligible (clean
vehicle, full bench) and sit in the complement of nothing — they are
undisturbed outcomes and marginally support the affirm side of the binary.

**Stage rules observed.** The frozen `band: "elevated"` in `record/context.json`
is a cert construct; per the merits-stage rule I did not anchor on it (no flag
owed). The cert signals (2 distributions, no CVSG) are spent. `probability`
and the `judgment-disturbed` claim state the same number, and
`predicted_disposition` is `other` as the merits contract requires.

**Where to discount me.** The vote lineup and authorship are the least
grounded part: no merits argument has happened, and I have not read
petitioner's merits brief or the amici, so the 6–3 split (Kagan with the
majority; Barrett writing) is a pattern-based guess with wide error bars. The
directional call itself leans on an analogy (Duguid) rather than case-specific
merits-stage evidence about how the argument will go — a briefed-moment cell
with the argument transcript in hand could reasonably land on the other side
of 0.5. I carry background knowledge of this case's cert-stage history from
training (through January 2026), which overlaps what the snapshot shows;
nothing I know postdates the grant, and the outcome does not exist.
