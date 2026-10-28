# Reasoning — P(disturbed) = 0.75

## Inputs used
- Snapshot `record/snapshots/2026-10-15.json` (cutoff 2026-10-15, date cut;
  `snapshot_provenance: truncated`). It shows the grant on 2026-01-26 after
  two distributions, the full merits briefing, 14 amicus filings (mostly for
  respondent: Chamber, Meta, MPA, NRF, RLC, News/Media Alliance and others;
  EPIC and Prof. Schwartz for petitioner), and argument on 2026-10-14 (Hammack
  for petitioner, Clement for respondent). No Solicitor General amicus is on
  the docket, and none was staged.
- Documents: QP section, the argument transcript (108 pp., not truncated), and
  the tables of contents of the petitioner's and respondent's merits briefs.
  Petition, BIO, cert reply and petitioner's merits reply were present; I did
  not read them closely beyond the QP, because the argument covered their
  arguments. The petition is marked truncated.
- `record/argument-features.json` (coverage: 154 Justice turns, 153
  attributed, 3/3 segments). Kagan's words fell mostly on respondent (587 vs
  106) and Kavanaugh's mostly on petitioner (616 vs 296). Alito pressed
  petitioner (451 vs 276). Jackson was heavy on both sides. Gorsuch spoke 60
  words, all to respondent. These counts show where questions fell, not which
  way anyone leans; my lean reading comes from the content below.

## Anchor
`metrics/statpack.md`, "The merits docket (granted cases)". The section
publishes an `excluded` count, so it is quotable. The case was granted in OT2025
(grant order 2026-01-26), so the window is OT2015–OT2024. The table carries
parsed rows only for 2017–2024: 378 disturbed of 537 parsed = **70.4%**.
That clears the 30-judgment floor. Coverage is near-complete for these Terms
(e.g. 2024: 76 parsed of 79 granted). The 70.4% is the bar this cell is scored
against.

## Adjustment from the argument
I moved up modestly from the anchor, to 0.75. Questions are not votes, and I
read them as leans only:
- **Kagan** stated the petitioner's reading as the most natural one ("following
  the definitions where they lead"). She also said companies could get consent
  or stop selling the data. Sotomayor and Jackson questioned the respondent
  hard on the structural theory. I count three likely votes to reverse.
- **Kavanaugh** began skeptical ("repurposing a 1980s statute for targeted
  advertising"; a textualist, not literalist Court). By the respondent's turn he
  was asking why the Court shouldn't "just follow 'consumer' as written." He
  noted that PII and VTSP status remain as defences, that consent is easy going
  forward, and that the definition may have been under-inclusive. I read him
  as leaning reverse.
- **Gorsuch** asked nothing about "consumer." His interest was in narrowing
  through "similar audiovisual materials" (whether only full-length films
  count, and whether they must be physical). That fits a justice content to
  read "consumer" broadly and fight elsewhere.
- **Barrett** probed limits on VTSP status and standing, and she challenged
  the respondent's own temporal-gap problem. She is uncertain, but her
  questions did not commit to the audiovisual reading.
- **Roberts** raised a purpose and "pets in the park" concern with the
  petitioner, then pressed Clement on his choice of easy hypotheticals. He is a
  toss-up leaning reverse.
- **Thomas and Alito** look like votes to affirm. Thomas found the
  video-related reading "natural." Alito pressed literalism, 1980s technology,
  and the "from" limitation.
- Clement conceded important ground. He said (a)(4)'s "engaged in the
  business" probably cannot mean "predominantly," and that his reading of
  "includes" in (a)(3) is hard to reach from the text. Both concessions weaken
  the respondent's structural story.

## What holds me below ~0.85
- The consequences argument is strong, the amicus wall is heavy, and the
  Court has narrowed old statutes to their technological context before.
  Roberts, Barrett and Kavanaugh could still join Alito and Thomas.
- The standing issue is unbriefed but was raised at argument. A DIG or a
  standing ruling is possible. A ruling of no standing would most likely
  vacate, which is still disturbed. A DIG would count against me; I put it at
  about 4%.

## Votes and writing
The vote block is my best guess and is banked, not scored. Writer
probabilities move off history only modestly: Alito is high for a likely
dissent, and Thomas, Jackson and Gorsuch are somewhat elevated. I did not
consult the statpack per-Justice tables beyond noting that every Justice's
disturb rate in OT2022–OT2024 sits between 59% and 77%, so no Justice is a
strong affirmer at baseline.

## Retrieval
No MCP or web retrieval, and no corpus `query`. I relied on the provisioned
record and the committed statpack. I have no training-data knowledge of this
case's outcome: it was argued after my knowledge horizon.
