# Why 0.13, and where to discount me

## Inputs

Provisioned snapshot `record/snapshots/2026-09-15.json` (the file `context.json` names), `record/context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025, signals observable), `event.yaml` (petition kind, no stage recorded, so cert; `evt-petition-disposition`, so `moment: distribution`), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (35 pp., full text), and `brief-in-opposition.txt` (57 pp., full text, including the appendix excerpts of the suppression-hearing testimony). None was `empty_text` or truncated. Base rates from the committed `metrics/statpack.md`.

## Anchor

Band `elevated`, frozen at prediction, so the scored yardstick is the bracketed `reached` rate of the `elevated` column in the "Segment base rate by salience band (sal-v4)" table, pooled over Terms strictly before OT2025. The table renders OT2017 to OT2024 as prior rows. Pooling the eight rows:

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

Weighted pool: roughly 484 grants over 2,810, about **17.2%**. That is my starting point. For shape I also read the relist-count cut (bucket 2: 27.8% granted plus 13.1% GVR) and the CVSG cut (none: 4.0% granted plus 2.3% GVR), but I did not anchor on the relist-2 bucket, for the reason below.

## Reading the docket signals

The two distributions here are not two conferences. The petition was distributed for May 1, the Court called for a response on April 27 (the State had waived), the BIO and reply came in, and the petition was redistributed for the September 28 long conference. So the "relist" bucket overstates this petition's trajectory: it has been through zero conferences on the fully briefed papers. The salience band is built from the distribution count and the same population includes other call-for-response redistributions, so the band anchor already prices this shape reasonably; I did not add a relist premium on top.

The response request is the one genuine positive signal on the docket. It is not a band feature (the scorer's lattice is relist count, CVSG, originating circuit, and petitioner class), so it is real information beyond the anchor. A call for a response over a waiver means at least one chambers thought the petition might be grant-worthy. In my experience that population grants at something like the low-to-mid teens, so it lands about where the band anchor already sits rather than well above it. Two cert-stage amicus briefs (a gun-rights coalition and public-defender groups) are a modest stakes signal.

## Adjustments from the merits of the petition

Downward, and they dominate:

- **Preservation and reframing.** The BIO's lead argument, backed by record citations to the suppression-hearing transcript and both state appellate briefs, is that petitioner never argued "officer purpose" below. His argument at every stage was about the path taken, standing behind the guest, and not knocking. The QP is built on purpose. The Court routinely denies petitions whose QP was reframed for cert, and Yee v. City of Escondido gives the State a clean rule to cite.
- **No split.** The petition candidly argues "confusion," not a conflict, and the BIO walks through each of the nine cited decisions plausibly showing that four of them do consider purpose and the other five resolved on other grounds. Two of the "confused" courts are intermediate state appellate courts.
- **Repeated prior denials in this exact space.** The petition itself lists Bovat, Chute, Frederick, Christensen, Morgan, and Brienza as knock-and-talk petitions the Court has denied since 2018. The Court has had many chances to police Jardines' knock-and-talk footnote and has taken none.
- **Contested factual premise and alternative grounds.** The officer testified his purpose was to talk, the trial court found no pretext, and the entry into the home rested on plain smell plus exigency. Even if a majority thought the porch conduct exceeded the license, the record is not the clean vehicle the petition describes.
- **Unreasoned state supreme court affirmance.** The only reasoned decision is the intermediate court's 2-1 opinion, which applied state "knock-and-talk exception" precedent.

Upward, more modestly:

- The response request (above).
- Three Justices signaled in Bovat (2020) that Jardines' curtilage rule was being under-enforced, and the petition is written to that statement. The 55-second video of officers holding the storm door and then kicking the door in is vivid and the record is small.
- A paid petition with counsel from an appellate clinic plus a national firm, two amici, and a dissent below.

Net: I moved from about 17% down to **0.13**. The QP-as-written is a poor grant, the reframed version cures preservation but then looks like error correction, and the Court's track record in this area is denial.

## Claims

- `disposition` 0.13, equal to `probability`.
- `relist-increment` 0.38: from a state of two distributions, P(at least one more). The long conference is the first real look; a call-for-response petition with amici is often carried once, and a reschedule would also add an entry. Most likely path is still denial without relist.
- `cvsg-increment` 0.03: state criminal case, no federal party.
- `summary-disposition-route` 0.15, conditional on grant: no intervening decision, contested facts, and pro-defendant summary reversals against state courts are rare.
- `dissent-from-denial` 0.25, conditional on denial: Bovat shows a live constituency for a statement, but the preservation issue is an easy reason not to write.

## Big-case score

0.45. A merits decision would govern a pervasive police practice, but the case has no headline party and the doctrinal move would be incremental.

## Uncertainty and where to discount

- I cannot see how the call for a response was received internally; if it was prompted by a Justice already drafting a statement rather than considering a grant, my relist and dissent numbers are low and the grant number is fine. If it reflects serious grant interest from more than one chambers, 0.13 is too low.
- I have not seen the amicus briefs' text, the reply brief, or the state-court opinions themselves; my read of the decisions below is through the parties' characterizations.
- The `fedcourts query` I ran returned recent granted SCOTUS matters generically ranked (mostly applications and election cases) and gave me no on-point knock-and-talk priors; the corpus retrieval surface has no text search, so it did not inform the number. The CourtListener docket search for other pending knock-and-talk petitions returned nothing (SCOTUS docket coverage there is thin), and the opinion search surfaced only Chatrie v. United States (June 2026, geofence warrants), which is not a companion case and which I did not read.
- I do not know this case's outcome; the September 28 conference postdates today. Forward mode, nothing to flag.
