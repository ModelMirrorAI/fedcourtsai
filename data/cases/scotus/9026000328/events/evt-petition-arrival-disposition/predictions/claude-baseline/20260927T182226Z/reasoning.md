# Rationale for the numbers (No. 26-328, arrival cell)

## What I read

Provisioned inputs: `record/snapshots/2026-09-11.json` (one docket entry —
petition filed September 8, 2026, response due October 13; docketed
September 10; paid; lower court Supreme Court of South Carolina; related docket
26-350 "Vide"), `record/context.json` (mode `forward`, band `baseline` under
`sal-v4`, `distribution_count` 0, no CVSG, Term 2026, cutoff 2026-09-11 with a
`date` cut, `snapshot_provenance: truncated`), the event definition
(`stage: cert`, `moment: arrival`), and both provisioned documents:
`questions-presented.txt` and the full 46-page `petition.txt` (both
`empty_text: false`, not truncated). No brief in opposition exists yet — the
response is not due until October 13 — so my read of the opposition is
inference, not text.

## Anchor

The context band is `baseline` and the statpack's band table is computed under
`sal-v4`, the same version, so the table is a valid anchor. The petitioners are
private corporations (no sovereign in the caption), so the caption-class floor
is the `baseline` band's bracketed `reached` figure, pooled over every Term row
the table renders that strictly precedes Term 2026 (2017–2025, nine rows):

| pooled quantity | value |
| --- | --- |
| baseline `reached` grant rate, OT2017–OT2025 | 5.0% (n = 12,720) |
| baseline terminal (leading) rate, same rows | 1.2% (n = 9,635) |

The 5.0% figure is the arrival-population anchor the prompt asks for; the 1.2%
terminal figure and the relist-0 cut (1.2% granted, 0.5% gvr) are the rates
among petitions that *ended* undistributed and understate an arrival, so I do
not anchor on them. For reference, the modern paid scored segment without a
CVSG runs about 4.0% granted + 2.3% gvr. State-court originations grant less
often than circuit originations in the pack's per-court cut, and South
Carolina does not appear among the rendered rows at all, so no court-specific
figure was available.

## Adjustments up from 5% to 20%

1. **A claimed direct conflict the lower court itself acknowledged.** The
   South Carolina Supreme Court expressly declined "to follow" the Third
   Circuit's *In re Whittaker Clark & Daniels* (176 F.4th 241, amended
   April 27, 2026) — same receiver, same appointing judge, same constitutional
   argument. That is the cleanest kind of split narrative, and the petition
   (Gibson Dunn, Amir Tayrani as counsel of record) is professionally built
   around it.
2. **The Court has already shown interest in this receivership practice.** In
   *Atlas Turner, Inc. v. Welch*, No. 25-213 (petition filed August 18, 2025;
   Chamber of Commerce, American Tort Reform Association and National Union
   amici; response waived, then **requested** on October 8, 2025; two
   distributions; denied January 12, 2026), the Court called for a response
   before denying. A response request is a real signal that at least some
   chambers wanted to look closer. All of that predates my snapshot and is
   legitimate forward signal.
3. **Four petitions, one conference.** No. 26-159 (Protopapas v. Whittaker
   Clark & Daniels, docketed August 3, 2026, BIO filed August 25, reply
   September 4) and No. 26-263 (Official Committee of Talc Claimants, docketed
   September 8, response extended to November 6) present the same territorial
   question from the receiver's side; No. 26-350 (Altrad Investment Authority,
   Kannon Shanmugam, docketed September 15, response due October 15) is this
   case's companion. If the Court takes *any* vehicle on this question, this
   petition is granted, held-and-GVR'd, or consolidated, all of which count as
   a grant on the binary axis. That multiplies the paths to a grant relative
   to a lone petition.
4. **Stakes and amici.** The petition documents 24 receiverships by one trial
   judge, a Texas appellate court and a Canadian court criticizing the
   practice, and a live clash with the English High Court. The business amici
   from *Atlas Turner* will very likely refile, and the foreign-relations
   dimension gives the Court a reason to see this as more than a state
   asbestos fight.

## Adjustments down

1. **Finality.** Trial on the receiver's third-party claims against these
   petitioners is stayed but unfinished. The petition spends four pages on
   *Cox Broadcasting* / *Mercantile National Bank v. Langdeau*; that is what
   a petition does when it knows finality is its soft spot. The Court denies
   most interlocutory state-court petitions, and a denial here would cost the
   Court nothing since the question returns after final judgment.
2. **The "split" is arguable.** *Whittaker* was a bankruptcy case about a New
   Jersey board's power to file Chapter 11; its constitutional passage is an
   alternative holding the state court characterized as dicta, and the
   Third Circuit itself first held the receivership order did not reach the
   bankruptcy decision. Respondent will say there is no conflict on a holding
   and the state court narrowed the receivership to insurance assets and
   corporate-benefit claims.
3. **Doctrinal mushiness.** The QP bundles Due Process, dormant (foreign)
   Commerce Clause and "principles of federalism." The Court prefers a single
   clean doctrinal hook; the receivership cases the petition relies on
   (*Booth v. Clark*, *Sterrett*) are 19th- and early-20th-century comity
   cases rather than constitutional holdings.
4. **The Court just passed once.** *Atlas Turner* was denied with **no noted
   dissent** — I confirmed this against the January 12, 2026 order list
   itself; a web summary that attributed a Kavanaugh "would grant" to that
   docket was wrong (that notation belonged to the adjacent Hertz entry).
   Justice Alito took no part, and may again (ESAB is publicly traded).

Net: a paid, elite-counsel petition with a credible split narrative, prior
demonstrated Court attention, and three related petitions, but an
interlocutory posture and a recent denial on the same practice. My subjective
grant-family probability is 0.20 — about four times the baseline-band anchor
and in the range I would assign to a well-built paid petition that will surely
draw a response request or a BIO and amici. If I am wrong, the likelier
direction is that I am too high: the Court frequently lets such disputes
ripen to final judgment.

## The other claims

- `relist-increment` 0.97: an arrival cell forecasts P(at least one
  distribution). Only a pre-distribution dismissal or withdrawal (a settlement
  with the receiver, or a Rule 46 dismissal) prevents it; that is rare, though
  not impossible here given ongoing parallel litigation in England and South
  Carolina.
- `cvsg-increment` 0.07: above the segment's raw CVSG frequency (roughly
  1–2% of paid scored petitions) because of the foreign-affairs framing, but
  well below even odds — no federal interest is directly implicated and the
  Court did not seek the government's views in *Atlas Turner*.
- `summary-disposition-route` 0.35 (conditional on a grant): the route
  splits between a plenary grant (this petition or its companion as the
  vehicle) and a hold-then-GVR after a *Whittaker* merits decision. The
  statpack's modern-cert table shows the gvr label at roughly 47% of the
  grant family (577 gvr vs 655 granted), but that figure is dominated by
  hold-companion petitions; here a GVR needs the Court first to grant 26-159,
  which I put at well under even odds, so I set the conditional below the
  pack-wide share.
- `dissent-from-denial` 0.15 (conditional on a denial): the direct prior
  (*Atlas Turner*) drew no statement; the paid segment's rate of noted
  dissents or statements on denial is low single digits; I add for the
  saliency of the practice and the chance a Justice writes to flag it while
  agreeing the posture is premature.
- `big_case_score` 0.45: consequential for a large mass-tort docket, corporate
  federalism and international comity, but not a headline case.
- `votes`: none stated; no cert vote is scored and I have no per-Justice
  signal beyond a possible Alito recusal.

## Retrieval and its limits

CourtListener's docket index holds none of the four SCOTUS dockets (26-159,
26-263, 26-328, 26-350) or 25-213, so the docket-state facts above came from
supremecourt.gov docket pages fetched through the engine's web tools, all
dated on or before September 15, 2026 (the 26-328 docket itself shows only
the filing entry — no later entries exist). The corpus CLI carries no
docket-number or free-text filter, so `fedcourts query` could not surface
*Atlas Turner* or the *Whittaker* petitions as priors; the `--citation` path
returned nothing, with the CLI's own note that the citation column is sparse.
I did not look for, and did not encounter, any disposition of this petition —
none can exist yet. Roughly 27 retrieval calls in total, slightly over the
advisory 25; see `retrieval.md`. Corpus vintage: the corpus service answered
live; I did not run `corpus-info` in this cell.

Where a reader should discount me: I have no text of the opposition, I am
inferring the finality argument rather than reading it, and my estimate of how
the Court will sequence four related petitions is judgment, not a base rate
the pack publishes.
