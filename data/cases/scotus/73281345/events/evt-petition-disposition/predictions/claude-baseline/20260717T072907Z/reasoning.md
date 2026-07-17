# Elkins v. United States, No. 25-1061 — cert disposition prediction

**Prediction: denied. P(grant, GVR included) = 0.07.**

## The case

Holly Ann Elkins was convicted of conspiracy to stalk and of cyberstalking
resulting in death (18 U.S.C. §§ 371, 2261A(2), 2261(b)) for her role in the
campaign of harassment that ended with her fiancé murdering his ex-girlfriend;
the district court called her the "mastermind," and she is serving a life
sentence on the cyberstalking count. The Fifth Circuit (161 F.4th 899) vacated
her separate § 924(c) life sentence (cyberstalking under § 2261A(2)(B) is not
categorically a "crime of violence") but affirmed the cyberstalking and
conspiracy convictions, rejecting her as-applied Commerce Clause challenge on
circuit precedent (Marek): a phone is an instrumentality of interstate
commerce even when used purely intrastate.

The question presented: whether the Fifth Circuit's *categorical* approach to
instrumentalities of interstate commerce is constitutional. The petition
pitches a split with the Tenth Circuit's United States v. Chavarria, 140 F.4th
1257 (10th Cir. 2025), which held that generic "motor vehicles" are not per se
instrumentalities for the federal kidnapping statute, and leans on separate
opinions (Judge Calvert in Bryan (11th Cir. 2025), Judge Murphy in Allen (6th
Cir. 2023)) describing a "developing" split.

## Signals toward grant

- **Call for response.** The United States waived; the case was distributed
  for the April 17, 2026 conference; on April 13 the Court requested a
  response. A CFR means at least one chambers took interest, and it is the
  single strongest pre-grant signal on this docket. The SG then took two
  extensions and filed a full 13-page BIO — the government treated the
  petition seriously.
- **Paid petition, clean vehicle claims.** Preserved below, reviewed de novo,
  no alternative holding by the panel; competent counsel of record; a
  petition-stage amicus (Texas Criminal Defense Lawyers Association).
- **Doctrinal appeal.** The federalism theme (if any phone use federalizes a
  crime, Congress can regulate anything) is calibrated to attract Justices
  Thomas and Gorsuch, and the petition quotes Justice Thomas's Taylor dissent
  throughout. Life sentence gives the stakes urgency.

## Signals toward denial

- **The split largely dissolves on inspection.** The BIO's strongest point:
  Chavarria itself *accepted* that some items are per se instrumentalities and
  reaffirmed the telegraph line of cases; it held only that the undefined
  class "motor vehicles" (including e-bikes and lawnmowers) is not per se an
  instrumentality under the kidnapping statute. And the Tenth Circuit's own
  precedent (Morgan, 748 F.3d 1024, 1033 n.11) holds that *telephones are*
  instrumentalities of interstate commerce. So there is no circuit in which
  Elkins's phone-based conviction would have come out differently — the
  "split" is a dissent and a distinguishable motor-vehicle holding.
- **Vehicle problems.** The indictment and trial record show Elkins also used
  the internet, email, a computer, and a GPS tracker whose data moved through
  out-of-state servers — multiple alternative instrumentalities, at least one
  with genuinely interstate transmission. Even a Court sympathetic to the QP
  could see the judgment surviving on alternative grounds, which the BIO
  presses squarely.
- **The Court has passed on this question repeatedly.** Cert was denied on
  phones/facilities-as-instrumentalities challenges in Smith (146 S. Ct. 356
  (2025)), Stackhouse (145 S. Ct. 558 (2024)), Uhlenbrock (2025), and a long
  older line (Evans, Giordano, Corum, Richeson, Weathers, Marek). Every
  circuit to decide the question holds phones are instrumentalities.
- **No percolating cluster.** CourtListener shows no cert petition filed in
  Chavarria or Bryan, so there is no companion vehicle and no pressure to
  resolve anything now; the Court's usual course with a "developing" split is
  to wait for it to mature.
- **Unattractive facts.** A stalking campaign culminating in murder, with the
  petitioner found to be its architect, is a poor sympathy vehicle for
  narrowing federal criminal jurisdiction.

## Base rates and the number

The statpack's modern discretionary-cert slice puts the overall resolved grant
rate near 3%; paid petitions run higher (Term 2025 paid: ~5.4% granted; Term
2024: ~6.9%; Term 2023: ~8.0%). The statpack has no CFR cut, but a call for
response is empirically worth a several-fold uplift over the unconditioned
paid rate — most grants pass through a CFR, though the large majority of
CFR'd petitions are still denied. Starting from the ~5-6% paid baseline, the
CFR pushes up toward the low teens; the dissolved split, the alternative-
instrumentalities vehicle problem, the Court's long streak of denials on this
exact question, and the absence of companion petitions push back down hard.

I land at **P(grant, incl. GVR) = 0.07** — denial is the strong favorite. No
intervening decision is pending that could prompt a GVR, so `gvr` is not the
likely grant shape; if the Court moves at all, plenary grant limited to the QP
is the form. A dissent from denial (Thomas, possibly Gorsuch) is a live
possibility and costs the petitioner nothing on the binary axis.

Procedurally: the BIO was filed July 13, 2026; expect a reply, distribution
for the end-of-summer long conference (late September 2026), and a disposition
in early October 2026, possibly after a relist.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-17.json`), the questions
presented and full petition (`record/documents/questions-presented.txt`,
`petition.txt` — including the Fifth Circuit opinion appendix), and the brief
in opposition (`record/documents/brief-in-opposition.txt`). Anchored on the QP
and weighed the petition's split claim against the BIO's responses, per the
prompt contract. Base rates from the committed `metrics/statpack.md` /
`statpack.json`; retrieval detailed in `retrieval.md`. Cell mode is `forward`
(`record/context.json`); no information about this case's disposition was
sought or encountered.
