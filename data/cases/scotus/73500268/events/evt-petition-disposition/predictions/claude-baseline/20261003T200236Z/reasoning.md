# Reasoning — why P(any grant) = 0.75, predicted disposition GVR

## What I read

Provisioned inputs: `record/snapshots/2026-10-03.json` (the full supremecourt.gov docket as stored, six entries), `record/context.json` (mode `forward`, band `elevated` under sal-v4, `distribution_count` 2, no CVSG, Term 2025, `signals_observable` true), `event.yaml` (stage `cert`, moment `distribution`), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (44 pages, including the Fifth Circuit's unpublished per curiam and the magistrate judge's summary-judgment opinion as appendices), and `brief-in-opposition.txt` (20 pages). None was flagged `empty_text`. Beyond those I ran one corpus query and four CourtListener MCP calls, listed in `retrieval.md`.

## The posture, in one paragraph

Roofing Designs, a Texas roofing subcontractor, lost its counterclaims against Royal American and its bond claim against Hartford on judicial estoppel: during its Chapter 11 case it scheduled the Royal American claim at $0, omitted the Hartford claim until Hartford threatened a dismissal motion, and told the bankruptcy court its litigation could not benefit creditors, all after it had claimed $227,756 in initial disclosures and over $600,000 in deposition testimony. The Fifth Circuit affirmed (per curiam, unpublished, January 13, 2026), resolving the inadvertence prong by reciting *Coastal Plains* and *Love*: inadvertence exists "only when" the debtor lacks knowledge or has no motive, and "any potential motivation for concealing a claim" defeats it. The petition (filed June 4, 2026) asked only that the Court hold the case for *Keathley v. Buddy Ayers Construction* and then GVR. *Keathley* was decided June 11, 2026: a unanimous Court (Jackson, J.) vacated the Fifth Circuit and held that its two-factor rule was "too rigid and too broad" and that courts must look to the totality of the circumstances. The Court distributed this petition for the September 28 conference, called for a response on August 7, received the BIO on September 8 and a reply on September 18, and redistributed it for the October 9 conference.

## Anchors

- **Salience band.** Context band is `elevated` under sal-v4, which matches the statpack's table version. Pooling the bracketed `reached` figures for `elevated` over the Terms strictly before OT2025 that the table renders (OT2017–OT2024) gives **about 17.2% (n≈2,810)**. That is the yardstick this cell is scored against.
- **Relist cut (paid scored segment).** The stored distribution count of 2 places this petition in the "1 relist" bucket: granted 8.2%, GVR 5.1% (about 13% grant family). But the second distribution here is a call-for-response reschedule, not a conference relist — the petition has never yet been considered at a conference — so this bucket overstates the relist signal while understating the signal the CFR itself carries.
- **CVSG cut.** None on the docket; the `none` bucket runs about 6% grant family. Not informative here.
- **Circuit.** CA5 petitions run about 3.7% grant family, with the highest GVR share of any circuit (2.1%).
- **Summary-route baseline.** Across prior Terms where the `gvr` label is comparable, GVRs are roughly half of the grant family (e.g., OT2019 1.7/2.9, OT2021 1.8/3.2, OT2025 1.3/2.6).

## Why I moved far above the anchor

The anchor describes the population of once-relisted elevated-band paid petitions. This petition is not a typical member of it. It is a **post-decision GVR candidate from the very circuit whose rule the lead case rejected**, where:

1. The court of appeals **applied the repudiated test in terms** — the opinion's inadvertence analysis consists of the *Coastal Plains*/*Love* "only when … no motive" / "any potential motivation" formulation that *Keathley* quotes and rejects. There is no alternative holding on the inadvertence prong.
2. The **Court called for a response.** The Court does not GVR against a respondent who has waived; a CFR is the ordinary prelude to a GVR on a petition like this one, and it is the Court's own signal that the petition was being looked at rather than denied on the pool memo.
3. The **respondents' own BIO concedes the route**: "if the Court concludes that Keathley may affect the judgment, the ordinary limited disposition would be a GVR." Their argument is that the record would satisfy a totality standard anyway, which is the standard anti-GVR argument and the one the Court routinely leaves to the lower court under *Lawrence v. Chater*'s "reasonable probability" test.
4. Timing fits cleanly: the petition was ripe only after the June cleanup conference, so an October GVR is the natural first opportunity.

Against that, the reasons the Court might deny:

- The district court's findings are **unusually record-specific** (sworn knowledge of the claims' value by the very person who signed the $0 schedules; a plan that told creditors there was no litigation of value; an incomplete amendment made only after Hartford threatened a motion). A Justice could read the panel's affirmance as resting on actual rather than hypothetical motive, so that *Keathley* changes nothing. The panel's "Obviously, leaving out the amount … assists in keeping out money to give to creditors" sentence points that way.
- *Keathley* **assumed without deciding** that judicial estoppel applies in bankruptcy and did not adopt petitioner's bad-faith rule, so the petition's QP as framed asks for something *Keathley* declined to give. The GVR inquiry does not turn on that, but a denial memo could lean on it.
- The petition is thin (a nine-page hold request from a small firm) and the decision below is unpublished, which matters little for a GVR but is not nothing.

Weighing those, I put P(any grant, which here means a GVR) at **0.75**. I would not go above about 0.85 because the Court does occasionally deny GVR-request petitions when the lower court's result plainly survives the new rule, and the BIO makes that case competently; I would not go below about 0.65 because the panel's inadvertence analysis is a verbatim application of the rejected test and the CFR shows the Court engaged with the petition rather than letting it be denied unanswered.

## The other claims

- **relist-increment 0.25.** From two distributions shown. A ripe post-decision GVR candidate is normally disposed of at the first conference that considers it; the increment comes from a possible one-week carry-over or a Justice writing.
- **cvsg-increment 0.01.** No federal interest; the legal question is already decided.
- **summary-disposition-route 0.96.** Conditional on a grant, the only plausible grant is a GVR; the petition asks for nothing else and the QP has been answered. The 0.04 covers an improbable plenary grant on some reframed question.
- **dissent-from-denial 0.12.** A denial would be a quiet one in most worlds; the residual accounts for a statement from one of *Keathley*'s separate writers.
- **big_case_score 0.08.** Private commercial dispute, follow-on to a decided case, unpublished decision below.

## Where to discount me

My number rests heavily on the general proposition that the Court GVRs liberally after rejecting a circuit test; I did not have a corpus cut for "post-decision GVR candidates with a CFR," and `fedcourts query` cannot filter on subject, so I could not pull a measured rate for this posture. The corpus GVR priors I did pull (the June 2026 cleanup GVRs, mostly federal criminal petitions with two or three distributions) confirm the shape — distributed, then GVR'd on the first conference after the lead decision — but are a different docket. The unusually strong factual record for non-inadvertence is the main reason this could be a denial, and I may be underweighting it.

## Leakage and mode

Forward cell; the disposition does not yet exist (next conference October 9, 2026). The one decisive piece of outside information — *Keathley*'s June 11, 2026 decision — predates this petition's first distribution and is legitimate forward signal; it is noted in `flags.json`. I did not search for this case's own docket or disposition; nothing I retrieved concerned this case.
