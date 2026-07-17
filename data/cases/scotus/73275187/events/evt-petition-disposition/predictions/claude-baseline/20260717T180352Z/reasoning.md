# Jouppi v. Alaska, No. 25-246 — cert petition disposition

**Prediction: denied (most likely single outcome), P(grant, GVR included) = 0.35.**

## The legal question

The Alaska Supreme Court (Apr. 18, 2025, 566 P.3d 943) upheld, as a matter of
law, the criminal in personam forfeiture of petitioner Kenneth Jouppi's
$95,000 Cessna for attempting to fly a passenger's alcohol — visibly, at least
a six-pack of beer — into the dry village of Beaver, a misdemeanor. The
question presented is whether, under *United States v. Bajakajian*, 524 U.S.
321 (1998), courts assessing gross disproportionality under the Excessive
Fines Clause may weigh the gravity of the offense **in the abstract** (the
Alaska Supreme Court and Eleventh Circuit approach) or must weigh the
**specific defendant's actual wrongdoing** (the Ninth Circuit's approach in
*Thomas v. County of Humboldt*, 124 F.4th 1179 (9th Cir. 2024), plus the
Indiana (*Timbs* remand), Pennsylvania, Utah, and D.C. high courts). The
petition frames a clean, purely legal, outcome-determinative split, including
the classic "state high court vs. its own federal circuit" configuration.

## Facts from the record that drive the call

Docket signals (snapshot 2026-07-17), roughly in order of importance:

1. **Call for response.** Alaska waived; the Court requested a response on
   Sep. 17, 2025. A CFR is Court-initiated interest and historically raises
   grant odds by roughly an order of magnitude over the paid-docket baseline.
2. **Held ~6.5 months for a related merits case.** Distributed for the
   12/12/2025 conference, then no action until June 2026 — the classic hold
   pattern. Petitioner's supplemental brief (June 25, 2026, retrieved from the
   docket) confirms the hold was for *Pung v. Isabella County*, 609 U.S. ___
   (2026), which resolved only the **threshold** Excessive Fines question
   (whether that tax-forfeiture scheme imposed a "fine" at all, answered no).
   *Pung* did not reach Jouppi's **step-two** question — the excessiveness
   standard — and the threshold is conceded here (Alaska agrees the in
   personam criminal forfeiture is a fine). So the hold neither moots nor
   GVR-resolves this petition.
3. **Survived the end-of-term cleanup.** After the supplemental brief, the
   petition was redistributed for the 6/29/2026 mop-up conference — and as of
   the 7/17 snapshot it was neither granted, denied, nor GVR'd in the early
   July orders where held cases are normally cleaned up. It is being carried
   over the summer, presumably to the long conference. Summer-carried
   petitions are a highly selected, elevated-grant-rate pool — but carrying is
   also the signature of a dissent-from-denial being written.
4. **Quality of the cert effort.** Institute for Justice (which won *Timbs v.
   Indiana*) is counsel of record; cert-stage amici are the Cato Institute,
   Prof. Beth Colgan (the leading Excessive Fines scholar), and Tyson Timbs
   himself. Paid petition, state criminal case, waiver of the Rule 15.5
   waiting period (petitioner pressing for speed).
5. **Fresh judicial acknowledgment of the split.** Per the supplemental brief,
   three Washington Supreme Court justices cited this very petition's split
   analysis in *State v. Meta Platforms* (Wash. June 18, 2026) (McCloud, J.,
   dissenting).

## Against the grant

- **Base rates.** Modern paid cert petitions grant at ~2.5–3% (statpack,
  Terms 2023–2025); CFR'd petitions at roughly 10%; the statpack's relist cuts
  top out at ~34% (two relists). Even very strong signal stacks rarely justify
  crossing 50% before a grant order exists.
- **The Court's revealed preference in this doctrinal space.** Since
  *Bajakajian* (1998) the Court has repeatedly declined step-two
  excessiveness-standard vehicles (*Leonard v. Texas* (2017, Thomas statement);
  *Toth* (2023, Gorsuch dissent from denial)), taking only threshold questions
  (*Timbs* 2019; *Pung* 2026). The interested justices (Gorsuch, Sotomayor,
  Thomas per *Culley*, *Toth*, *Timbs*) may not be four grant votes.
- **Two passed grant opportunities.** The Court could have granted in December
  2025 alongside *Pung*, and again from the 6/29/2026 mop-up conference to fill
  the OT2026 fall calendar. It did neither. A deny-with-writing at the long
  conference is a very live scenario.
- **BIO's vehicle attacks.** This is a criminal, not civil, forfeiture (blunting
  the forfeiture-abuse narrative — Alaska has abolished standalone civil
  forfeiture); the state says the Alaska court did examine case-specific facts
  and the petition is error-correction dressed as a split; and there are
  unresolved factual disputes about the extent of Jouppi's culpability (the
  Alaska Court of Appeals would have remanded for factfinding). Petitioner's
  rejoinder — the court below assumed all facts in his favor and still upheld
  the forfeiture as a matter of law — is fair, but the criminal posture and
  the state-specific statute give pause.

## Weighing

This petition sits far out on the selected tail: CFR + three quality amici +
elite counsel + a hold for a related merits case + surviving the post-*Pung*
cleanup + a contemporaneous judicial citation of its split. Each of those
conditions multiplies the base rate. Against that: the Court's 27-year pattern
of avoiding exactly this question, two foregone grant moments, and a plausible
deny-with-dissent ending (the *Toth* pattern), which the summer carry equally
supports. A GVR "in light of *Pung*" is unlikely because *Pung* is threshold-
only and the threshold is conceded here; I fold a small residual GVR chance
into the grant-side probability.

I put P(any grant, GVR included) at **0.35** — several multiples above even the
strongest statpack cut, reflecting the extreme selection, but below coin-flip
because denial (likely with a separate writing) remains the single most likely
outcome and the modal disposition. Predicted disposition: **denied**;
`granted = 0`.

## Big-case score

0.6 — if granted and decided, this sets the constitutional standard governing
fines and forfeitures nationwide (the first excessiveness-standard case since
1998), with heavy advocacy interest and vivid facts; but the QP is
methodological ("level of abstraction"), the amounts modest, and a likely
narrow opinion tempers the ceiling.

## Provenance and degradations

- Anchored on the provisioned snapshot, `questions-presented.txt`,
  `petition.txt`, and `brief-in-opposition.txt` (all non-empty, untruncated).
- Retrieved from the case's own docket: the June 25, 2026 supplemental brief
  (supremecourt.gov PDF listed in the snapshot), which identifies the *Pung*
  hold — pre-decision material, no leakage.
- Web checks (forward mode, unrestricted) confirmed the petition is still
  pending; no disposition surfaced anywhere, so the cell is genuinely forward.
- The cell's corpus query sidecar was unreachable, so `fedcourts query` priors
  were unavailable; base rates come from the committed `metrics/statpack.md`
  (details in `retrieval.md`, flag in `flags.json`). This degraded prior
  retrieval slightly but does not change the analysis, which is docket-signal
  driven.
