# Predictor Rationale: *Scanlan v. Coalition for Open Democracy* (No. 26A512)

## Summary Call

- **`predicted_disposition`:** `denied` (`granted`: `0`)
- **`probability` (`interim-disposition`):** `0.35`
- **`confidence`:** `0.65`
- **`big_case_score`:** `0.55`
- **Escalation claims (`interim-v1`):**
  - `interim-disposition`: `0.35`
  - `response-requested-increment`: `0.00` (already `true` at snapshot)
  - `referral-increment`: `0.90`
  - `amicus-increment`: `0.18`

## Inputs Consulted

I read the provisioned snapshot `2026-10-19.json`, `record/context.json`, `record/documents/documents.json`, and the two full-text filings provisioned under `record/documents/`:
- `application.txt` (24 pages, `truncated: false`, `empty_text: false`): Emergency Application to Stay Order of the United States District Court for the District of New Hampshire by New Hampshire Secretary of State David M. Scanlan and Attorney General John Formella, filed October 15, 2026.
- `application-response.txt` (44 pages, `truncated: false`, `empty_text: false`): Response in Opposition to Emergency Application for a Stay by Respondent Coalition for Open Democracy, filed October 19, 2026.

I also consulted `metrics/statpack.md` for the interim-docket base rates, queried `fedcourts query` for recent SCOTUS application priors, and read the full text of two September 2026 Supreme Court per curiam stay opinions cited by both parties (*People Not Politicians v. Onder*, No. 26A388, and *National Republican Congressional Committee v. Brown*, No. 26A274) via the CourtListener MCP server.

## Base-Rate Anchoring

From `metrics/statpack.md` (*The interim docket (applications)*), the scored baseline for an OT2026 interim cell (`term: 2026`) is the grant rate pooled over resolved substantive applications in the strictly preceding Terms in the window (OT2023–OT2025):
- **OT2025:** 17 granted / 226 resolved substantive (7.5%, 10 unparsed)
- **OT2024:** 16 granted / 194 resolved substantive (8.2%, 4 unparsed)
- **OT2023:** 18 granted / 127 resolved substantive (14.2%, 3 unparsed)
- **Strictly-prior pooled baseline (OT2023–OT2025):** `51 / 547 = 9.32%` (clearing the `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor).

As `metrics/statpack.md` notes, that 9.32% baseline is unconditional across all resolved substantive applications, whereas the predicted population at `moment: response-filed` is already selected on climbing the escalation ladder:
- Across all 633 resolved substantive applications in the statpack, only 129 had a response requested (`response_requested: true`) and only 99 drew amicus briefs. Because the Court almost never grants a contested stay of a lower-court injunction without requesting a response, the conditional grant rate once a response is requested is roughly 3.5x–4.5x the unconditional rate (~35%–45%).
- Moreover, this application is brought by state officials (New Hampshire's Secretary of State and Attorney General) invoking *Purcell v. Gonzalez* against a federal district court's election-related preliminary injunction entered 32 days before the November 3, 2026 general election, supported by an RNC amicus brief and a dissent from the First Circuit's stay denial (Judge Dunlap). On those surface features alone, a typical state-applicant *Purcell* stay application would start near **50%–60%**.

## Case-Specific Adjustments

Despite the strong surface *Purcell* posture, a close reading of `application.txt` and `application-response.txt` reveals three major substantive and procedural weaknesses in the State's application that pull my probability down from ~55% to **0.35**:

### 1. Severe Merits Forfeiture and Lack of Certworthiness (*Hollingsworth* Factors 1 & 2)
Under *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010)—reaffirmed on September 4, 2026 in *NRCC v. Brown*, No. 26A274, slip op. 2—an applicant must demonstrate a reasonable probability that four Justices will grant certiorari and a fair prospect that a majority will reverse. Here:
- The district court **upheld** New Hampshire's statutory removal of student IDs from the list of per se valid photo IDs (HB 323, amending RSA 659:13, II(a)), denying Respondent's preliminary-injunction motion as to the statute itself.
- The district court enjoined **only** the Secretary's April 23, 2026 press release ("April Directive") and a single sentence in the Election Procedure Manual that categorically prohibited checklist supervisors from considering a student ID alongside other evidence under New Hampshire's statutory catch-all safety valves (`RSA 654:12, I(d)(4)` for identity at registration and `RSA 659:13, I(c)(3)` for identity when obtaining a ballot, both allowing "any other evidence that reasonably establishes that it is more likely than not that the person is who they claim to be").
- Crucially, the district court rested its narrow injunction on **two independent federal constitutional holdings**: (1) an *Anderson-Burdick* First/Fourteenth Amendment violation (because the State offered *no* state interest justifying the categorical bar on considering student IDs under the safety valve, and the Deputy Secretary of State testified at the September 23 hearing that he saw no factual reason a student ID could not be reasonable evidence), and (2) an independent **Twenty-Sixth Amendment** intentional age-discrimination holding.
- In its 24-page Supreme Court stay application, **the State does not challenge either the *Anderson-Burdick* holding or the Twenty-Sixth Amendment holding.** Instead, the State devotes nearly the entire application to *Purcell* and spends a single paragraph arguing that the district court misread New Hampshire state statutes and should have abstained or certified under *Railroad Commission of Texas v. Pullman Co.* or *McKesson v. Doe*.
- Yet as Respondent documents, the State never asked for *Pullman* abstention or certification prior to the injunction; to the contrary, the State stipulated in writing below that both safety valves work identically under the "any other evidence" standard (allowing non-listed documents such as utility bills or marriage certificates). A pure dispute over whether a federal district court properly read a state statute—where the applicant forfeited its statutory reading below and leaves two independent federal constitutional holdings completely unchallenged in its Supreme Court application—is an exceptionally poor candidate for certiorari.

### 2. No Statute Enjoined and Immediate Compliance Flipping the *Purcell* Status Quo
- In *People Not Politicians v. Onder*, No. 26A388 (Sept. 25, 2026), the district court and Eighth Circuit ordered Missouri to switch its congressional redistricting map after absentee and military ballots had already been printed and mailed under the 2022 map, which local election officials attested was "practically impossible."
- Here, by contrast, the October 2 injunction does not touch ballot printing, early/absentee voting (which New Hampshire conducts under separate rules in RSA 657:17-c), or the 97%+ of voters who present a listed driver's license, passport, or state ID. It affects only the discretionary Election Day safety-valve inquiry by three-member local Boards of Supervisors of the Checklist for the tiny fraction of voters lacking any listed ID.
- Most importantly, **the Secretary of State already complied with the injunction immediately after October 2, 2026**: he updated the Secretary of State's public website (both the *Register to Vote* and *Election Day Voting* pages) and emailed revised instructions to local election officials clarifying that although student IDs are no longer per se valid under RSA 659:13, II(a), checklist supervisors "may consider a student identification card along with other available evidence" under the safety valves. That revised guidance has been live for over two weeks (including during the October 6, 2026 municipal election in Franklin, NH).
- Consequently, as in *Republican National Committee v. Common Cause Rhode Island*, 141 S. Ct. 206 (2020), a Supreme Court stay issued around October 21–23 would not preserve a continuous pre-litigation status quo; it would force the Secretary to reverse his own live website and instructions for a second time roughly 10–12 days before Election Day, generating more confusion for voters and poll workers than leaving the already-implemented clarification in place.

### 3. Why P(grant) Remains a Substantial 0.35
I do not push the probability below `0.35` because the Court's current majority applies *Purcell* with great force, as demonstrated in *People Not Politicians v. Onder* (Sept. 25, 2026), where the Court emphasized that "given that the equities heavily favor staying this late-breaking intervention, it suffices that the merits are not entirely clearcut." Here, Applicants have two real *Purcell* talking points that could attract five votes notwithstanding the forfeiture problems:
1. Respondent waited 130 days after HB 323 was signed on April 3, 2026 (and 110 days after the April 23 Directive) before filing suit on August 11, 2026.
2. Because of that delay, the September 8, 2026 state primary was conducted under the April Directive, and the district court's October 2, 2026 injunction ordered the Secretary to revise state guidance 32 days before the November 3 general election—even after the New Hampshire Legislature enacted SB 223 on July 2, 2026 adding the word "Only" to RSA 659:13, II(a).

If five Justices treat *Purcell* as a near-categorical bar on federal-court injunctions ordering changes to state election guidance within a month of a general election—and excuse the State's failure to brief the Twenty-Sixth Amendment and *Anderson-Burdick* holdings on the ground that the state-law predicate is "not entirely clearcut"—the stay will be granted. Weighing that ~35% *Purcell* pathway against the ~65% pathway where the unchallenged constitutional holdings, lack of certworthiness, and already-completed website/guidance update lead the Court (or pivotal Justices such as Chief Justice Roberts, Justice Barrett, and Justice Kavanaugh alongside the three liberal Justices) to deny the stay yields **`probability = 0.35`**.

## Key Uncertainties

- **How strictly pivotal conservative Justices apply `Hollingsworth` certworthiness in a *Purcell* posture:** Justices Kavanaugh and Barrett have repeatedly stressed that an emergency application requires certworthiness (*Does 1–3 v. Mills*; *Labrador v. Poe*), which strongly cuts against Applicants given their forfeiture of the 26th Amendment and *Anderson-Burdick* merits. However, in election cases under *Purcell*, Justice Kavanaugh (*Merrill v. Milligan*, 142 S. Ct. 879, 880 (2022) (Kavanaugh, J., concurring)) and the *Onder* per curiam focus on whether the merits are "clearcut" and whether plaintiffs unduly delayed.
- **Weight given to the Secretary's post-October 2 compliance:** Whether the Conference views the Secretary's immediate compliance as flipping the *Purcell* equities against a second change, or instead refuses to penalize a state official for complying with a district court injunction while seeking appellate stays.
