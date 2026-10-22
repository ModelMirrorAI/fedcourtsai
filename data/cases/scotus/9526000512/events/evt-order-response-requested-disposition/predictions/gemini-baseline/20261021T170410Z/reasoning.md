# Rationale (`reasoning.md`): *Scanlan v. Coalition for Open Democracy* (No. 26A512)

## Summary of Forecast
- **Top-level `probability` (`interim-disposition`):** `0.58` (`granted: true`, `predicted_disposition: "granted"`)
- **Declared `interim-v1` claims:**
  - `interim-disposition`: `0.58`
  - `response-requested-increment`: `1.00` (vacuous; response already requested on 2026-10-15)
  - `referral-increment`: `0.96`
  - `amicus-increment`: `0.55`
- **`big_case_score`:** `0.52`

## Base-Rate Anchoring (`metrics/statpack.md`)
This cell is an `interim`-stage event (`evt-order-response-requested-disposition`, `moment: response-requested`) on a Term 2026 application (`26A512`, `term: 2026`). Per the prompt contract, I anchor on **"The interim docket (applications)"** section of `metrics/statpack.md` (and do not use the cert salience-band table, as `context.json` properly carries `band: null`).

Pooling unweighted `granted` over `resolved (subst.)` across the ten application-Terms strictly preceding Term 2026 (`2016 <= T < 2026`):
- **OT 2025:** 17 granted / 226 resolved (`7.5%`, `unparsed = 0`)
- **OT 2024:** 16 granted / 194 resolved (`8.2%`, `unparsed = 0`)
- **OT 2023:** 18 granted / 127 resolved (`14.2%`, `unparsed = 0`)
- **OT 2016–2022:** 0 resolved (`unparsed` covers all applications in those Terms)
- **Strictly-prior 10-Term pool (`2016–2025`):** `51 granted / 547 resolved = 9.32%` (`~9.3%`, `n = 547`), which clears the `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor.

As `metrics/statpack.md` and `predict.md` caution, that `9.3%` unconditional substantive rate pools across *all* resolved substantive applications, whereas the escalation-signal counts across OT 2023–2025 (`548` substantive applications total) show that a response was requested in only `110` cases (`20.1%` of substantive applications: 27 in 2025, 47 in 2024, 36 in 2023), referrals occurred in `319` (`58.2%`), and amicus filings appeared in `79` (`14.4%`). Because virtually all substantive grants come from the subset of applications where the Court or Circuit Justice requests a response, conditioning on `response_requested = true` shifts the empirical baseline from `9.3%` unconditional to roughly **45%–50%** among response-requested substantive applications.

## Case-Specific Adjustments from the Provisioned Record and Lower-Court Context

I read the provisioned snapshot (`data/cases/scotus/9526000512/record/snapshots/2026-10-15.json`), `context.json`, and the full text of the State's emergency stay application (`data/cases/scotus/9526000512/record/documents/application.txt`, 18 pages, `empty_text: false`). Because this cell is in `forward` mode, I also consulted the underlying District of New Hampshire (`1:26-cv-00647-JL`) and First Circuit (`26-2132`) filings prior to October 15, 2026, as well as the Supreme Court's September 2026 stay opinions cited in the application (*People Not Politicians v. Onder*, No. 26A388, and *NRCC v. Brown*, No. 26A274), via the CourtListener MCP server.

### 1. Upward Adjustments (Supporting a Stay Grant)
- **Strong *Purcell* Posture (`+0.18` over the response-requested baseline):**
  The District Court issued its preliminary injunction opinion on October 2, 2026 (Doc. 63) and its injunction order on October 5, 2026 (Doc. 64)—just **29 days** before the November 3, 2026 general election. By the time Respondent's brief is due in the Supreme Court on October 19, 2026, the general election will be **15 days** away. The Supreme Court has repeatedly enforced *Purcell v. Gonzalez*, 549 U.S. 1 (2006), in the 2026 election cycle, including in *People Not Politicians v. Onder*, 609 U.S. ___ (Sept. 25, 2026) (per curiam), and *Allen v. Milligan*, 608 U.S. 511, 514 (2026).
- **Plaintiff's Four-Month Litigation Delay:**
  New Hampshire enacted HB 323 on April 3, 2026, the Secretary of State issued the challenged "April Directive" on April 23, 2026, and HB 323 took effect on June 2, 2026. Yet Respondent Coalition for Open Democracy waited until August 11, 2026 (130 days after enactment and 70 days after the effective date) to file suit. Judge Laplante relied on that exact delay to deny a preliminary injunction for the September 8, 2026 primary election under *Purcell* (Doc. 43 at 13), calling the compressed timeline "largely one of [the plaintiff's] own making." Under Justice Kavanaugh's four-part *Purcell* test in *Merrill v. Milligan*, 142 S. Ct. 879, 881 (2022), a plaintiff must show inter alia that it "has not unduly delayed bringing the claim to court."
- **Vulnerability of the District Court's Merits Distinction Between HB 323 and the April Directive:**
  Judge Laplante upheld HB 323's categorical removal of student IDs from the list of valid photo IDs in `RSA 659:13, II(a)` under *Crawford v. Marion County Election Board*, 553 U.S. 181 (2008), finding that generalized state interests in election integrity, expiration-date administrability, and uniform rules justified the statute (Doc. 63 at 31–33). However, he held that the Secretary's April Directive violated *Anderson-Burdick* and the Twenty-Sixth Amendment insofar as it barred checklist supervisors from considering student IDs as "other evidence" under the statutory safety valves (`RSA 654:12, I(d)(4)` for registration and `RSA 659:13, I(c)` for obtaining a ballot), reasoning that the State failed to articulate a separate interest specific to the safety-valve exclusion. A majority of the Supreme Court is likely to view the State's interest in preventing an end-run around HB 323 (and `SB 223`, which added "Only" to `RSA 659:13, II(a)`) as self-evidently tied to the same legislative interests that justified HB 323, and to view the District Court's order as functionally second-guessing state officials' interpretation of state election statutes (*Pennhurst* friction). Judge Dunlap's dissent from the First Circuit's October 14 stay denial underscores that the State's position has traction.

### 2. Downward Adjustments and Countervailing Risks (Supporting Denial)
- **The Secretary Already Complied on October 5, Inverting the Practical *Purcell* Disruption (`-0.08`):**
  As Judge Laplante noted in his October 7 Order Denying Stay (Doc. 72 at 3–4) and as Respondent highlighted in its First Circuit opposition (`Doc. 00118521946` at 12, 28–30), the injunction does not alter ballots or enjoin HB 323; it merely removes a single categorical prohibition from p. 17 of the Election Procedure Manual so checklist supervisors may consider a student ID alongside other evidence under the existing case-by-case safety valve. Crucially, the Secretary of State *already updated* his website and transmitted revised guidance to local clerks via the Statewide Voter Registration System on October 5, 2026 (as Applicants acknowledge at Application p. 14 n.2). By late October, that revised guidance will have been live for over two weeks; granting a stay would force the Secretary to reverse his public guidance a second time in the final 10–12 days before Election Day.
- **State's Litigation Forfeitures and Contradictions Below (`-0.04`):**
  In its September 21, 2026 court-ordered supplemental filing (`Doc. 60 ¶¶ 6, 9`), the State represented to the District Court that `RSA 654:12` and `RSA 659:13` are interpreted "in harmony" as "the same process" and gave non-listed documents (such as a marriage certificate) as examples of what supervisors may consider under the safety valve, while the Deputy Secretary of State testified that he saw "no factual reason why a student ID could not be reasonable evidence" under the safety valve (Doc. 63 at 33, 40). As Judge Laplante pointed out in denying a stay (Doc. 72 at 2–3 & n.15), the State raised its `SB 223` exclusivity argument for the first time in its stay motion and waited four days after the October 2 opinion before seeking a stay.

## Uncertainties and Discount Factors
This is a genuinely close shadow-docket call (`P = 0.58`). The central uncertainty is whether at least five Justices apply *Purcell* mechanically (viewing any October federal-court injunction that overrides state election guidance after a 4-month plaintiff delay as per se improper) or whether Chief Justice Roberts and/or Justice Kavanaugh or Barrett conclude that—because Judge Laplante left HB 323 intact, held the State to its own pre-judgment statutory concessions, and the Secretary already published the revised safety-valve guidance on October 5—intervening two weeks before the election would cause more confusion than leaving the narrow order undisturbed.
