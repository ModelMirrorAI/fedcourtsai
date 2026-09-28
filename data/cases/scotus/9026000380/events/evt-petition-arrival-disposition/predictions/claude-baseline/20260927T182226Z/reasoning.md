# Rationale for the numbers

**P(grant family) = 0.80.**

*Anchor.* `record/context.json` freezes `band: federal` under `sal-v4`, which
matches the heading of the statpack's "Segment base rate by salience band
(sal-v4)" table, so that table is my anchor. On an arrival cell the published
figure that is the arrival population's own rate is the caption class's floor
— the `federal` band's bracketed `reached` rate, pooled over the Term rows
shown that strictly precede this case's Term (2026). Pooling the nine rendered
rows OT2017–OT2025 by their weighted denominators gives 143 grant-family
outcomes over n = 202, about 0.71 (consistent with the pack's overall
`federal` band split of granted 48.5% plus gvr 22.3%). The per-Term figures
are thin and noisy — from 43.5% (OT2018, n = 23) to 89.5% (OT2022, n = 19) —
and the two most recent Terms sit below the pool (OT2024 60.0%, n = 15;
OT2025 52.4%, n = 21). I did not use the relist-count cut's relist-0 figure,
which is the rate among petitions that ended undistributed and is the wrong
population for an arrival cell.

*Adjustments up.* Within the federal class this is about as strong a petition
as the class contains: (1) an express, acknowledged split — the Fourth Circuit
majority says it "disagree[s]" with the Third Circuit's published *Khalil*
decision and the Second Circuit's *Mahdawi* panel, and the petition also
claims tension with the Eleventh Circuit's *Alvarez* on Section 1252(g);
(2) the Second Circuit granted rehearing en banc in *Mahdawi* on September 3,
2026 and ordered proceedings held in abeyance if this Court grants on the
question — an unusually direct signal from a lower court that the question is
ripe for this Court; (3) a published opinion with a forceful Wilkinson dissent
calling for this Court's intervention; (4) a jurisdictional question of
recurring, government-wide importance that the Court has repeatedly engaged
(*Jennings*, *Nasrallah*, *Guerrero-Lasprilla*), and one the *Jennings*
plurality left open; (5) the Solicitor General asks for plenary review and
proposes a companion grant in *Khalil*, which signals the government's
priority. Historically, SG petitions asserting a genuine circuit conflict are
granted at rates above the federal class's overall average, so I move above
the 0.71 pool.

*Adjustments down.* (1) Vehicle: the posture is interlocutory — the Fourth
Circuit affirmed a release-on-bail order and an All Writs Act order barring
removal while the habeas petition remains pending in the district court, not
a final habeas judgment. The Court has taken jurisdictional questions in this
posture before, but it is a reason to prefer *Khalil* or to wait. (2) Mootness
risk, which the petition itself flags: the immigration judge found the
respondent removable in November 2025 and proceedings continue; a final order
of removal would move his custody to Section 1231 and undercut a challenge to
Section 1226(a) detention, and departure would moot the case. (3) The Court
may grant *Khalil* alone and hold this case — although a later GVR would still
count as a grant on the binary axis, a denial after *Khalil* is decided
against the government would not. (4) The recent-Term federal figures are
lower than the pool. Net, I land at 0.80: well above the pooled floor, below
the near-certainty the petition's rhetoric would suggest.

**relist-increment = 0.93.** The frozen state is zero distributions. The claim
resolves true if the petition is distributed at all. A paid SG petition that
is not withdrawn is essentially always distributed; the residual is a
withdrawal or dismissal before conference (a mootness event, or the government
choosing to proceed only in *Khalil*) plus some parse risk in how
distributions are read. The statpack's relist cut buckets by terminal count
and cannot give this hazard directly.

**cvsg-increment = 0.01.** The United States is the petitioner; the Court does
not call for the views of a party. The number is not zero only because a
claim's resolution is mechanical and I would rather not be certain.

**summary-disposition-route = 0.12** (conditional on a grant). No intervening
decision exists to GVR against, and the Fourth Circuit's opinion is the one
that created the split, so plenary review is the natural route. The
conditional mass comes from the *Khalil*-as-lead-vehicle scenario: grant
*Khalil*, hold this petition, GVR it after judgment. The prior Terms'
cert-order share of the grant family in the statpack runs around a third
(gvr 22.3% against granted 48.5% in the `federal` band overall), but that pool
is dominated by held-and-GVR'd government petitions on already-decided
questions, which this is not.

**dissent-from-denial = 0.25** (conditional on a denial). Dissents from the
denial of a government petition are uncommon, and the likeliest denial path
here is mootness, which produces a silent order. Against that, the topic is
salient and a Justice sympathetic to the Wilkinson dissent might write.

**big_case_score = 0.8.** The question governs the forum for challenges by
tens of thousands of detained noncitizens a year and arises from the
prominent campus-speech deportation cases; it is a jurisdictional rather than
a constitutional holding, which keeps it below the top of the scale.

**What I read.** The provisioned snapshot `2026-09-21.json` (one docket entry:
petition filed, response due October 21, 2026; paid case; Fourth Circuit
No. 25-1560, decided July 23, 2026), `questions-presented.txt`, and
`petition.txt` (the petition proper in full — introduction, statement,
reasons for granting, conclusion — and the opening of the appended Fourth
Circuit opinion; `documents.json` marks the 196-page file truncated, so the
bulk of the appendix was not available to me). No brief in opposition exists
yet, which is the arrival moment's definition rather than a gap. I did not
read the outcome file or anything under `data/qp-topics/`.

**Retrieval beyond the record.** CourtListener confirmed the Fourth Circuit
opinion (published, July 23, 2026, No. 25-1560) and the Third Circuit's
published *Khalil* opinions (January 15 and May 22, 2026, No. 25-2162); it
holds no SCOTUS docket for a *Khalil* petition, so whether that petition has
been filed is unknown to me. A corpus citation lookup for the zipper-clause
precedents returned nothing because the citation column is sparsely filled — a
coverage gap, not evidence. A corpus query for 2020s granted SCOTUS rows
surfaced recent substantive applications rather than comparable cert
petitions and did not move the number.

**Where to discount me.** The federal-class anchor is thin (n = 202 pooled)
and its recent Terms run lower than the pool; my upward move rests on
qualitative reads of the petition, which is one-sided advocacy with no
opposition yet. I have no visibility into the state of the respondent's
removal proceedings after November 2025 or of any *Khalil* petition, both of
which bear directly on the vehicle. I know nothing about the Court's OT2025
decisions the petition cites (*Blanche v. Lau*, *Mullin v. Doe*) beyond what
the petition says of them, and I did not rely on them.
