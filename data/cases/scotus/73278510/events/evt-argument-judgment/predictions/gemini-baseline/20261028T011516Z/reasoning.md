# Reasoning for `evt-argument-judgment`: *Salazar v. Paramount Global, dba 247Sports* (No. 25-459)

## 1. Case Posture and Question Presented

This cell (`evt-argument-judgment`, moment `argued`) forecasts the merits judgment in *Michael Salazar v. Paramount Global, dba 247Sports*, No. 25-459 (`scotus/73278510`), following oral argument held on October 14, 2026 (`2026-10-15.json` snapshot).

The Question Presented concerns the Video Privacy Protection Act ("VPPA"), 18 U.S.C. § 2710:
> Whether the phrase "goods or services from a video tape service provider," as used in the VPPA's definition of "consumer" (18 U.S.C. § 2710(a)(1)), refers to all of a video tape service provider's goods or services or only to its audiovisual goods or services.

In the proceedings below, Michael Salazar alleged that he signed up for 247Sports.com's free online email newsletter, watched video clips on 247Sports.com while logged into Facebook, and had his Facebook ID (`c_user` cookie) and video-viewing history transmitted to Meta via the Meta Pixel without his consent. The Middle District of Tennessee (683 F. Supp. 3d 727) dismissed the complaint under Rule 12(b)(6), holding that Salazar was not a VPPA "consumer" because he did not subscribe to audiovisual goods or services. A divided panel of the Sixth Circuit affirmed (133 F.4th 642, with Judge Bloomekatz dissenting), assuming without deciding that Paramount is a "video tape service provider" ("VTSP") under § 2710(a)(4) and that the disclosed data constituted "personally identifiable information" ("PII") under § 2710(a)(3), but holding that "goods or services from a video tape service provider" in § 2710(a)(1) is limited by association with § 2710(a)(4) to audiovisual goods or services.

Certiorari was granted to resolve an acknowledged 2–2 circuit split:
- **No audiovisual limitation on "goods or services"**: Second Circuit (*Salazar v. National Basketball Ass'n*, 118 F.4th 533 (2d Cir. 2024)) and Seventh Circuit (*Gardner v. Me-TV National Ltd. Partnership*, 132 F.4th 1022 (7th Cir. 2025) (Easterbrook, J.)).
- **Audiovisual limitation required**: Sixth Circuit (*Salazar v. Paramount Global*, 133 F.4th 642 (6th Cir. 2025)) and D.C. Circuit (*Pileggi v. Washington Newspaper Publishing Co.*, 146 F.4th 1219 (D.C. Cir. 2025)).

## 2. Prior and Base-Rate Anchors

From `metrics/statpack.md` (strictly prior Terms OT2020–OT2024, since `context.json` stamps `term: 2025` for docket No. 25-459):
- **Merits judgment disturbed base rate**: Across OT2020–OT2024, the Court disturbed the judgment below (reversed, vacated, or affirmed-in-part/reversed-in-part) in roughly **70.2%** of merits decisions (ranging from 56.5% in OT2022 to 79.7% in OT2020, with OT2024 at 74.2% and OT2023 at 71.7%).
- **Sixth Circuit track record**: Historically, the Sixth Circuit has an elevated disturbance rate on certiorari review (in OT2020–OT2024, disturbed in the majority of reviewed cases).
- **Reversal vs. Vacatur selection**: When the Court rejects a threshold statutory ground on which a court of appeals affirmed a Rule 12(b)(6) dismissal, while leaving open alternative, unaddressed threshold arguments (here, whether Paramount is a VTSP under § 2710(a)(4), whether the pixel data is PII under § 2710(a)(3), and whether signing up for a free email newsletter is a "subscription" of a good or service), the standard disposition—and the explicit prayer of Petitioner's merits brief (Pet. Br. 1, 3, 12, 52; Reply Br. 1, 24) and oral argument colloquy with Justice Sotomayor (Tr. 16:7–21)—is **vacated** and remanded.

## 3. Oral Argument Analysis (`argument-features.json` and Transcript)

### Quantitative Turn and Word Balance
Per `record/argument-features.json`, total questioning volume was nearly balanced between the advocates, with slightly more turns and words directed at Respondent's counsel (Paul Clement) than Petitioner's counsel (Joshua Hammack):
- **Petitioner (Hammack)**: 74 Justice turns, 2,445 words.
- **Respondent (Clement)**: 79 Justice turns, 2,606 words.

However, the per-Justice distribution and the *substance* of the questioning reveal a clear ideological and methodological cleavage on the bench:
- **Heaviest questioners of Respondent (Clement)**:
  - **Jackson**: 12 turns, 637 words to Clement (vs. 10 turns, 344 words to Hammack).
  - **Kagan**: 16 turns, 396 words to Clement (vs. 3 turns, 149 words to Hammack).
  - **Sotomayor**: 12 turns, 286 words to Clement (vs. 6 turns, 129 words to Hammack).
  - **Kavanaugh**: 11 turns, 333 words to Clement (vs. 17 turns, 513 words to Hammack).
  - **Barrett**: 10 turns, 232 words to Clement (vs. 11 turns, 342 words to Hammack).
- **Heaviest questioners of Petitioner (Hammack)**:
  - **Alito**: 14 turns, 377 words to Hammack (vs. 4 turns, 282 words to Clement, which were friendly invitations to elaborate on consequences).
  - **Kavanaugh**: 17 turns, 513 words to Hammack.
  - **Barrett**: 11 turns, 342 words to Hammack.
  - **Thomas**: 4 turns, 174 words to Hammack (and 4 turns, 140 words to Clement, reinforcing skepticism that 247Sports is a VTSP).

### Substantive Signals by Justice

1. **Justice Kagan (Strong Vote to Vacate; Likely Majority Author)**:
   - Kagan was unmistakably in Petitioner's camp. She directly dismantled Clement's core textual argument: *"I don't know if it's mixing and matching. It's following the definitions where they lead. So this definition says 'goods and services.' It doesn't say 'audiovisual goods and services.' Other definitions do have the modifier in them. That suggests that the fact that this definition does not have the modifier in it is especially important. And you -- you -- you can't get the modifier from the 'from' clause because the 'from' clause just tells you what -- where you're getting the goods and services from... What you get, most naturally read, is the Petitioner's understanding of the statute."* (Tr. 49:10–50:5).
   - She also brushed aside Clement's compliance and policy complaints: *"Well, this statutory language, you know, it is relatively clear. And you might have been -- be -- be charged with having read it. And going forward, you have two very simple solutions. One is to get consent. Easy enough. People do it every day. And the other is to stop selling people's private information. Take your pick."* (Tr. 57:20–58:4). She compared consent to a routine cookie pop-up box (Tr. 60:11–18).
   - Having authored *Pulsifer v. United States*, 601 U.S. 124 (2024) (heavily cited in the briefs), Kagan is a prime candidate to write a crisp textualist opinion for the Court.

2. **Justice Sotomayor (Strong Vote to Vacate)**:
   - Sotomayor confirmed with Hammack early on that Petitioner seeks vacatur rather than outright reversal because alternative defenses (like VTSP status) remain open on remand (Tr. 16:7–17:12).
   - With Clement, she pressed the structural refutation of Respondent's "interlocking transaction" theory: subsections (d) (evidentiary exclusion) and (e) (record destruction) govern PII regardless of whether it concerns a "consumer," proving the statute itself separates PII generation from consumer status (Tr. 77:11–78:15). She also rejected Clement's business-model complaints (Tr. 58:13–59:19).

3. **Justice Jackson (Strong Vote to Vacate)**:
   - Jackson spent 637 words pressing Clement with the "Justice Breyer in a video store buying a book about French films and previewing films in a viewing booth" hypothetical (Tr. 51:8–54:21) and later challenged Clement's line-drawing as creating an irrational distinction between customers whose identical video-watching history is disclosed (Tr. 66:18–69:21).
   - With Hammack, she confirmed that standing was not briefed and that lower court dismissals often turn on other elements, and elicited the point that obtaining consent is a straightforward cure (Tr. 25:5–26:23, 41:8–42:22).

4. **Justice Kavanaugh (Pivotal Swing Vote — Leaning Vacate with Concurrence)**:
   - While Kavanaugh pressed Hammack hard on what "engaged in the business" of delivering audiovisual materials means under § 2710(a)(4) and expressed concern about suits targeting ordinary retailers like Chick-fil-A (Tr. 33:11–39:17), his questioning of Clement revealed how he reconciles those concerns with the text of § 2710(a)(1).
   - First, Kavanaugh emphasized with Hammack that PII is a 3–1 circuit split *against* plaintiffs and remains open on remand (Tr. 15:23–16:6, 26:24–27:3).
   - Second, to Clement, Kavanaugh laid out his exact roadmap: *"What seems different to me about now from the 1980s is not so much the -- the plaintiffs but the type of personal identifying information. It's not your name being released. It's this data-sharing code, right? And that's quite a bit different. And there are a lot of arguments about PII. And then treating everyone as a video tape service provider, every business as opposed to the ones that are analogous to Blockbuster. But those two arguments, both of which may be raised in future cases in which your side's prevailing in the lower courts for the most part, are not the issues before us. So how do we think about, you know, the sky-is-falling concern in the amicus briefs and it's part of your brief when there are these two other arguments that you may prevail on? And why shouldn't we just follow 'consumer' as written and worry about that in a future case?"* (Tr. 54:25–55:24).
   - Kavanaugh also pushed Clement hard on how easy it is to obtain consent going forward via pop-up banners and noted that the definition of "consumer" might actually have been under-inclusive given modern technology (Tr. 57:6–13, 60:3–14, 61:18–24).
   - This is a classic Kavanaugh posture: join the textualist majority on the narrow question presented ("follow 'consumer' as written"), while writing a separate concurrence emphasizing that VTSP status under § 2710(a)(4) and PII under § 2710(a)(3) remain substantial, independent guardrails on remand and in future cases.

5. **Justice Gorsuch (Quiet, Leaning Vacate on Plain Text + Concurrence/Remand Guardrails)**:
   - Gorsuch spoke only briefly (8 turns, 82 words, all to Clement). Notably, he asked Clement just one targeted set of questions at the end: whether Clement agreed with the American Newspaper amicus brief that "similar audio visual materials" in § 2710(a)(4) requires content like full-length movies and TV shows (or even physical materials per Judge Randolph's concurrence in *Pileggi*) (Tr. 81:21–82:21).
   - For a committed textualist like Gorsuch—who consistently rejects importing unstated limitations into statutory definitions to solve policy problems when other statutory terms do the work—pointing to "similar audio visual materials" in § 2710(a)(4) as the proper textual home for narrowing the statute's reach signals that he does not need to distort "goods or services" in § 2710(a)(1). He is likely to vote with the majority to vacate on § 2710(a)(1), leaving § 2710(a)(4) for remand.

6. **Justice Barrett (Close Swing Vote — Leaning Majority)**:
   - Barrett tested both sides carefully. She asked Hammack about VTSP limits (Nordstrom, Chick-fil-A) and Article III standing under *TransUnion* (Tr. 7:15–9:6, 22:22–23:20, 39:20–41:5).
   - However, during Clement's argument, Barrett pushed back on Clement's central structural argument (the "temporal gap" argument), pointing out that Clement's own reading suffers from the exact same temporal gap if a subscriber buys a video subscription at Point A and watches a free video five or ten years later (Tr. 64:23–65:15).
   - Furthermore, on standing, Barrett got Clement to admit that Paramount dropped standing in the Sixth Circuit and that standing is intertwined with the unbriefed PII merits question, with Clement explicitly asking the Court *not* to decide standing without briefing (Tr. 82:25–85:12). Barrett's textualist instincts align with Kagan, Kavanaugh, and Gorsuch in reading "goods or services" according to its text while reserving VTSP, PII, and standing for remand.

7. **Chief Justice Roberts (Center-Right Swing — Leaning Majority or Narrow Vacatur)**:
   - Roberts invoked Justice Breyer's "pet snail in the park" hypothetical with Hammack (Tr. 5:14–25), showing some sympathy for purposive narrowing. However, when Clement leaned heavily on the Chick-fil-A and dog-bandana hypotheticals, Roberts pushed back: *"you've picked some hypotheticals that are particularly helpful for you. Chick-fil-A, you don't think of that as anything other than chicken. But there are a lot of stores that sell a lot of different things, including the type of videos that we're talking about. And so I don't know why we should focus just on the easy hypotheticals."* (Tr. 47:20–48:11). If there is a 6–3 or 7–2 majority to vacate on plain text while highlighting the open issues for remand, Roberts is likely to join it rather than dissent, though he is closer to the line than Kagan/Sotomayor/Jackson/Kavanaugh.

8. **Justice Alito and Justice Thomas (Likely Dissenters)**:
   - **Alito** was overtly hostile to Petitioner's reading throughout argument, asking why "smart lower court judges have rejected the kind of very literal interpretation" Hammack advanced (Tr. 18:1–19:1), emphasizing 1980s VHS/Blockbuster technology (Tr. 19:2–21:6), offering the "Costco optical services / gas station" hypothetical to support Clement's reading of "from" (Tr. 28:12–30:11), and inviting Clement to elaborate on the "drastic consequences" and $250 million class-action exposure (Tr. 72:17–76:24). Alito is the most likely author of a dissent.
   - **Thomas** opened the argument by questioning whether "goods or services from a video tape service provider" naturally means video-related services (Tr. 4:10–13), pressed Hammack on how streaming video is even covered by "prerecorded video cassette tapes or similar audio visual materials" as opposed to cable TV (Tr. 31:3–33:2), and agreed with Clement that 247Sports is simply a sports site rather than a video provider (Tr. 44:22–46:6). Thomas is likely to dissent alongside Alito (and potentially write separately on § 2710(a)(4)).

## 4. Calibration of Probabilities and Decomposition Claims

### Primary Binary & Judgment (`probability: 0.72`, `judgment: "vacated"`)
- Starting from the ~70.2% merits disturbance base rate (OT2020–OT2024), the oral argument provides positive confirmation that a majority of the Court (Sotomayor, Kagan, Jackson, Kavanaugh, plus at least two of Gorsuch, Barrett, and Roberts) is persuaded that "goods or services" in § 2710(a)(1) cannot bear an unwritten "audiovisual" modifier when adjacent definitions in § 2710(a)(3) and (a)(4) explicitly include video/audiovisual modifiers.
- At the same time, the strong policy resistance from Alito and Thomas, and the bench's shared concern about runaway pixel litigation against ordinary websites, creates a ~28% chance that Roberts, Barrett, and/or Gorsuch coalesce with Thomas and Alito around the "from a video tape service provider" relational limitation (following the Sixth and D.C. Circuits and *Dubin* / *Duguid*).
- Accordingly, I set `probability` (and `judgment-disturbed`) at **0.72**.
- Because the Sixth Circuit assumed without deciding that Paramount is a VTSP and disclosed PII, and Petitioner explicitly requested vacatur so those issues can be litigated on remand (Tr. 16:7–17:12), `"vacated"` is the modal disturbed judgment.

### Authorship Distributions (`majority-author` and `separate-writers`)
- **`majority-author`**: Using the OT2020–OT2024 uniform bench baseline (~10–12% per Justice, ~2% `per-curiam`), I upweight **Kagan (0.22)** because she articulated the core textualist synthesis at argument and recently wrote *Pulsifer*, and slightly upweight **Kavanaugh (0.12)**, **Gorsuch (0.11)**, **Barrett (0.11)**, and **Jackson (0.11)**, while downweighting **Thomas (0.07)** and **Alito (0.08)** who are likely in dissent. The probabilities sum to 1.00.
- **`separate-writers`**: Anchored on the OT2020–OT2024 separate-writing base rates from `metrics/statpack.md` (Thomas ~27%, Gorsuch ~22%, Jackson ~26%, Sotomayor ~21%, Alito ~17%, Kavanaugh ~14%, Barrett ~11%, Kagan ~8%, Roberts ~2%), adjusted for case-specific roles:
  - **Kavanaugh (0.30)**: Elevated well above his 14% baseline because his questioning strongly telegraphed a concurrence highlighting that the PII (3–1 split) and VTSP ("engaged in the business") defenses remain open on remand.
  - **Alito (0.28)** and **Thomas (0.36)**: Elevated as the likely dissenting voices (with Alito likely authoring the principal dissent and Thomas frequently adding a separate dissent or concurrence on the original meaning of "prerecorded video cassette tapes or similar audio visual materials").
  - **Gorsuch (0.24)** and **Jackson (0.26)**: Near their high historical baselines.
  - **Roberts (0.02)** and **Kagan (0.06)**: Low separate-writing rates, consistent with historical baselines and expected majority participation.
