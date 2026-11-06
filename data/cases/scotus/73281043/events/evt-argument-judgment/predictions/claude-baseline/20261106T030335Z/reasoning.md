# Reasoning — P(disturbed) = 0.85, judgment: reversed, 6–3

## Inputs
I read the snapshot `record/snapshots/2026-11-05.json`. It shows the grant on Jun 15 2026 after three distributions, merits briefing, the United States as amicus supporting petitioner with divided argument, and argument on Nov 4 2026. I also read `record/context.json` (forward mode, date cut 2026-11-05) and these files under `record/documents/`:
- the questions presented
- the argument transcript (73 pp., read in full)
- the petitioner's merits brief, sections on the statement of the case and the conclusion, to establish the posture
I did not read these closely, though they were provisioned: the respondent's merits brief, the reply, the US amicus brief, the BIO, the cert reply and the petition. My reading of the respondent's position comes from his argument.

The **United States' brief supports the petitioner** (Texas). My forecast follows it: the SG argued both prongs, saying Atkins is not "new" as to Johnson and was "previously available."

The `band: high` in the context is a cert-grant construct. Under the merits rules I did not use it.

## Anchor
The statpack's merits section publishes an `excluded` count, so it is quotable. This case was granted Jun 15 2026, so its grant Term is OT2025, and the pool is grant Terms 2015–2024. Only 2017–2024 have parsed rows: 376 disturbed out of 534 parsed, which is **70.4%**. Coverage in those Terms is near-complete (parsed/granted runs 56/56 to 73/80). The pool clears the 30-judgment floor.

## Adjustments (up to 0.85)
- **The argument.** Questioning was asymmetric in content, more than in volume. Per `argument-features.json` (coverage: 106 of 107 Justice turns attributed, 4 of 4 segments), Justices spoke 73 turns / 2,834 words while petitioner's side held the lectern and 33 / 918 during respondent's time. Most of the petitioner-side volume was Jackson, Sotomayor and Kagan challenging Texas. That is consistent with the liberal Justices fighting a losing position, but I do not read counts as votes.
- **What the questions showed.** Thomas (the "Marbury" question) and Barrett (the telephone analogy; futility; the statute of limitations and actual-innocence tension in respondent's dual fact/law theory) were openly skeptical of respondent. Kavanaugh read the 23-state finality concern into the record and asked whether the case could be resolved on the new-rule prong alone, which only matters if the ruling is for Texas. Barrett asked how to write the opinion narrowly *if* the Court agreed with Texas. Alito offered the formulation that the DSM is evidence rather than part of the Atkins standard, and the SG accepted it. Gorsuch and Roberts gave little away. Gorsuch got respondent to concede that "previously unavailable" modifies "rule." Neither said anything favorable to respondent. A question is not a vote. Still, five of the six conservative Justices signaled toward Texas, and respondent needed two of them.
- **Merits.** The Fifth Circuit's Cathey test is a minority position. It was challenged by an en banc dissent (rehearing denied 9–7) and opposed by Texas, the SG and 23 states. The Court took a state's AEDPA petition in a capital case. Textually, respondent's reading of "new" was weak even to Kagan.

## Why not higher
- The Court could split on the ground, though that would still disturb the judgment.
- Kagan's Atkins-II theory is a coherent narrow path that could attract Gorsuch, who has shown idiosyncratic habeas votes.
- A small DIG or remand-without-disturbance tail exists, and so does the general error rate of reading argument.

## Votes
I am most confident in Thomas, Alito, Barrett and Kavanaugh. Roberts and Gorsuch are less certain but probably in the majority. Sotomayor and Jackson are near-certain dissents, and Kagan is a likely dissent. Pooled per-Justice disturb rates for OT2020–OT2024 sit around 60–75% for every Justice; for example Roberts is 161/230 and Thomas 140/229. They don't separate the Justices much, so the vote calls rest on the transcript.

## Writers
The writer forecasts are judgment calls. The November 2026 sitting's assignments are unknown, so the majority-author distribution is spread across the six likely majority Justices, with Thomas and Barrett slightly ahead because of their argument engagement and habeas record.

## Retrieval
I ran one corpus query (generic modern granted priors). It was not on point and did not move the forecast. I made no MCP or web calls. I did not seek, and do not know, this case's outcome.
