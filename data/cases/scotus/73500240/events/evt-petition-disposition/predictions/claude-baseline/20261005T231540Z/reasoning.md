# Rationale for the numbers

**P(any grant) = 0.24; predicted disposition `denied`; `granted = 0`.**

## Anchor

`record/context.json` freezes this cell at band **`baseline`** under **`sal-v4`**, Term **2025**, with `distribution_count = 1` and no CVSG. The caption is a private petitioner (a police officer sued in his individual capacity, no sovereign marker), so `baseline` is also the class floor. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's salience version, so the band is a valid anchor. Pooling the bracketed `reached` figures for `baseline` over the eight rendered Terms strictly before 2025 (OT2017 through OT2024, n = 11,580 weighted) gives a pooled grant rate of about **5.1%**. That is my starting point.

The surrounding cuts agree on the shape: relist bucket 0 shows a 1.7% grant family and bucket 1 shows 13.3%; CVSG `none` shows 6.3%; the Fifth Circuit as originating court shows a 3.7% grant family on the whole modern cert population.

## Why I moved up, to roughly five times the anchor

1. **Record Requested (September 22), before the first conference.** This is the strongest signal on the docket. The Court requests the record when a Justice wants to review it directly, and in a body-camera case that means watching the video. In practice a record request precedes most summary reversals and most written dissents from denial. It is a signal the baseline band's reached rate does not condition on.
2. **A published, divided panel opinion with a dissent that expressly asks for summary reversal.** Judge Oldham's dissent invokes *Mullenix v. Luna*, the Court's 2015 summary reversal of this same circuit for the same "sufficient threat" formulation, and the panel majority relied on that very *Lytle* formulation at App. 13a. The majority would have left the opinion unpublished; publication came at the dissenter's request.
3. **A 9-8 en banc denial** with two written dissents (Ho, joined by Jones and Smith; Oldham, joined by Jones, Smith, Duncan, and Engelhardt). The circuit itself is nearly evenly split.
4. **Organized amicus support** from the Texas Association of Counties and eight law-enforcement associations, requesting in the alternative a GVR in light of *Zorn v. Linton*.
5. **The Court's current appetite.** *Zorn v. Linton* (per curiam, March 23, 2026, over a Sotomayor-Kagan-Jackson dissent), which I read on CourtListener, shows the Court summarily reversing a court of appeals' denial of qualified immunity this very Term for defining clearly established law too generally. That is public information predating the snapshot and is legitimate forward signal. The pattern it continues (*White v. Pauly*, *Kisela*, *City of Escondido v. Emmons*, *Rivas-Villegas*, *City of Tahlequah v. Bond*) is the exact route this petition asks for.

## Why I did not move further

1. **The holding below is an evidence-sufficiency ruling, not a legal rule.** The panel found two genuine disputes of material fact (whether Granado perceived the gun; whether Ramirez swung it) and reversed summary judgment for trial. The BIO's *Johnson v. Jones* / Rule 10 point is well taken: the Court's summary reversals (*Tahlequah*, *Kisela*, *Rivas-Villegas*, *Zorn*) mostly involved facts that were undisputed or taken in the plaintiff's favor, and the Court rarely wades into whose version of a video is right.
2. **Respondent's facts are not frivolous.** Officer Watson, the closer officer, said Ramirez never pointed the gun; the autopsy shows four back-to-front wounds including the fatal shot to the back of the head; Granado's own body camera shows Ramirez running away; and Granado asked "did he have a gun?" seconds later. On plaintiff's version, a man not known to be armed was shot in the back while fleeing, which is *Garner*'s paradigm "obvious case" (*Brosseau*, *Hope v. Pelzer*). A per curiam would have to run through *Scott v. Harris* and say the undisputed "he's got a gun!" shout forecloses the no-perception inference. That is doable, but it is more fact work than the Court usually takes on summarily.
3. **The interlocutory posture.** Reversal of summary judgment with remand for trial means petitioner can still win before a jury; the Court frequently cites that alone as a reason to deny.
4. **Questions 2 and 3 are not vehicles.** QP 2 was not pressed or passed on below and the Court declined the same invitation in *Zorn* footnote 3, *Wesby*, *Emmons*, and *Rivas-Villegas*. QP 3 is a law-review argument the record does not present. Neither adds grant probability; they slightly signal counsel's distance from the Court's usual practice (petitioner's counsel is a Texas civil-defense firm rather than a Supreme Court practice).
5. **Base-rate humility.** Even once-relisted paid petitions grant at about 13%; petitions at relist 2 or more grant at about 40%. A record request before the first conference is a strong but not decisive predictor of ending up in those buckets, and a good share of record-requested petitions are simply denied, sometimes over a dissent.

Weighing these, a petition with this docket profile in the Court's current qualified-immunity posture sits well above its band but below even odds. I land at **0.24**.

## The other claims

- **`relist-increment` 0.65.** From one distribution. The record request is the main driver; both a summary reversal and a dissent from denial need extra conferences. The 35% complement is a silent denial on the long-conference order list, which the record having arrived by September 28 makes feasible.
- **`cvsg-increment` 0.02.** No federal interest.
- **`summary-disposition-route` 0.75 (conditional on grant).** Petitioner, the dissent below, and the amici all ask for a summary disposition; the Court's qualified-immunity interventions are almost always per curiam reversals or GVRs. The 25% plenary residual covers the possibility that the Court uses this case to say something about segmenting a continuous use of force after *Barnes v. Felix*.
- **`dissent-from-denial` 0.35 (conditional on denial).** Above the ordinary rate for a denied paid petition because of the record request and the dissents below; below even odds because most record-requested petitions are still denied silently.
- **`big_case_score` 0.35.** The case's stakes are a qualified-immunity per curiam and a Fifth Circuit excessive-force standard; significant to that doctrinal line, not a term-defining case.

## What I read, and what I did not

Provisioned inputs: the snapshot (`2026-10-05.json`, whose payload `sJsonCreationDate` is 09/28/2026), `context.json`, `questions-presented.txt`, the full `petition.txt` (including the appended panel opinion, Dennis concurrence, Oldham dissent, and the en banc denial order with the Ho and Oldham dissents), and the full `brief-in-opposition.txt`. `documents.json` shows all three documents fetched with text (no `empty_text`, no truncation). Beyond those I read the committed `metrics/statpack.md`, ran two `fedcourts query` priors lookups (neither returned case-relevant priors; there is no topic filter on SCOTUS rows), and used the CourtListener MCP server to confirm the Fifth Circuit opinion's identity and to read *Zorn v. Linton*. I did **not** look up this petition's own Supreme Court docket or any order list, and I know nothing of its disposition; if the long-conference order list of October 5 or the grant list of October 2 already disposed of it, that is outside everything I read.

## Where to discount me

My number leans heavily on the record request as a signal, and the statpack publishes no cut for it, so that lift is judgment rather than a measured rate. I also lean on the Court's recent *Zorn* reversal as evidence of appetite; one data point is thin. If the reader believes the Court treats fact-disputed video cases as categorically off-limits for summary reversal, the right number is nearer the 10 to 12% a once-relisted petition faces. If the reader believes a record request in an officer's qualified-immunity petition is nearly a precommitment to act, it is nearer 0.40.
