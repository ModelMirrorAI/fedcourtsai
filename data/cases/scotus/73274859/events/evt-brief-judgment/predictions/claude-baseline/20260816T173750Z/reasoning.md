# Rationale for P(disturbed) = 0.77

## Anchor

The committed statpack's merits section publishes an `excluded` count, so its
pooled rate is quotable and is the baseline this cell is scored against. The
grant order issued **2026-02-23**, so the grant Term is **OT2025** and the pool
is grant Terms strictly before it. The pack holds Terms 2017–2024 (the merits
table renders every Term the pack holds, so the rendered window is the
window): disturbed 31+50+42+57+46+49+34+50 = **359** over parsed
52+75+54+69+65+72+55+73 = **515**, a pooled disturbed rate of **69.7%**
(n=515, well past the 30-parsed floor). Coverage caveat: the nearest Term
(2024: 73 parsed of 75 granted) is the most complete recent Term; 2025's thin
parse (24/50) is mostly pendency and sits outside the pool anyway.

## Adjustments

**Up from 0.697, on the merits branch.** Conditional on reaching the merits, I
put P(disturb) ≈ 0.90, well above the unconditional baseline:

- The Court granted a question it had declined in *Sunoco v. Honolulu*
  (Jan 2025) after six distributions, in an interlocutory posture over a
  jurisdiction-led BIO — a deliberate, appetite-signaling grant, not a
  courtesy one.
- The Solicitor General filed an **uninvited** cert-stage amicus supporting
  petitioners, filed again at the merits stage, and moved for divided
  argument. SG-supported petitioners win at rates well above the baseline.
- The lower court ruled **against** the federal-preclusion defense; the Court
  grants to reverse roughly seven times in ten, and the current majority's
  posture toward expansive state-law climate litigation points the same way.
- The amicus lineup at the merits stage (the United States, 20+ states,
  Chamber, NAM, API, congressional leadership) is overwhelmingly weighted to
  petitioners' side.

**Down for the jurisdictional off-ramp.** The Court itself directed briefing on
"whether this Court has statutory and Article III jurisdiction to hear this
case." Respondents' merits brief (provisioned, read) leads with it and it is a
serious argument: the decision below is an interlocutory affirmance of a denial
of a motion to dismiss, the fourth *Cox* exception is a stretch on these facts
(federal defenses remain; reversal arguably would not end the litigation given
possible source-state-law theories), and *Atlantic Richfield*'s
separate-lawsuit route is contested. Petitioners abandoned their cert-stage
Article III theory and now rest on an ASARCO-style injury from the ruling
itself, which respondents plausibly attack as premature. I put P(the Court
reaches the merits) ≈ **0.85**: a Court that wanted the jurisdictional exit
could simply have denied — adding the question in the grant order most often
means the majority intends to clear its path (and the SG will argue
jurisdiction exists) — but this is the largest single source of undisturbed
mass, larger than affirmance.

**Arithmetic.** 0.85 × 0.90 ≈ 0.765, rounded to **0.77**. Undisturbed mass:
~0.15 jurisdictional dismissal/DIG-equivalent, ~0.05 affirmance, ~0.03
DIG-proper and residuals. `judgment = reversed` is the modal label; `vacated`
is possible if the Court resolves less than the full question, but a reversal
on the preclusion question as granted is the natural form. `granted = 1`
carries the same disturbed binary; `predicted_disposition = other` per the
merits-stage contract.

## Votes

6–3 (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett / Sotomayor, Kagan,
Jackson). Alito participated in the grant (no non-participation notation,
confirmed by post-grant press coverage), unlike the 2023 Boulder petition, so
I list all nine; if he later recuses, intersection-only scoring drops him.
Gorsuch is my least confident majority vote, Kagan my least confident
dissenter.

## What I worked from, and where to discount

Forward-mode cell; I worked from the provisioned snapshot (full docket through
2026-08-16, including the grant order text as truncated in the snapshot), the
provisioned petition, the QP, and the provisioned respondents' filing — which
usefully contains **both** the BIO (Nov 2025) and the **respondents' merits
brief** (Jul 27, 2026, the brief that opened this event), so I read the
respondents' actual merits arguments, including their responses to petitioners'
and the SG's merits briefs. I did **not** read petitioners' or the SG's merits
briefs directly; my account of their structural-preclusion framing is inferred
from respondents' point-by-point response and the cert petition, and should be
discounted accordingly. Web retrieval confirmed the grant details and Alito's
participation; a corpus citation query for AEP/Ouellette-citing priors returned
nothing (sparse citation coverage — a data gap, not absence of precedent). The
statpack numbers above are from the committed pack. Main uncertainties: the
jurisdictional branch probability (reasonable readers could put it 0.10–0.30)
and Gorsuch's vote.
