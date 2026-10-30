# Predictor Rationale (`reasoning.md`)

## 1. Cell Posture and Inputs Consulted

This cell predicts `evt-brief-response-disposition` (`stage: interim`, `moment: response-filed`) for `scotus/72406996` (*Thomas Douglas Arthur v. Alabama*, No. `16A450`).
- **Provisioned snapshot:** `data/cases/scotus/72406996/record/snapshots/2016-11-04.json` (`input_snapshot: "2016-11-04.json"`).
- **Provisioned documents:** None (`record/documents/` was not provisioned; `paper_only_filings` is `false` in `context.json`). My forecast therefore relies on the provisioned docket snapshot, the base-rate tables in `metrics/statpack.md`, corpus queries via `uv run fedcourts query`, and lower-court opinions retrieved via the CourtListener MCP server.
- **Snapshot contents (`2016-11-04.json`):**
  - Case Number: `16A450 *** CAPITAL CASE ***` (`sJsonTerm: "2016"`, `bCapitalCase: true`), linked with `16-595`.
  - Lower Court: Supreme Court of Alabama, Case No. `1951985`.
  - Three proceedings entries, all dated **November 3, 2016**:
    1. *Application (`16A450`) for a stay of execution of sentence of death, submitted to Justice Thomas.*
    2. *Response to application (`16A450`) from respondent Alabama filed.*
    3. *Reply of applicant Thomas Douglas Arthur filed.*
  - Frozen `context.json` conditioning: `mode: "forward"`, `cutoff: "2016-11-04"`, `cut_kind: "date"`, `term: 2016`, `band: null`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `signals_observable: true`.

## 2. Disclosure of Historical Context and Companion Order Surface

Although `context.json` stamps `mode: "forward"`, this case (`16A450`) is a historical November 2016 application with a snapshot cutoff of `2016-11-04`. In accordance with the leakage doctrine in `.github/prompts/predict.md`, I treated `2016-11-03` / `2016-11-04` as a strict temporal boundary and passed `--decided-before 2016-11-03` on corpus queries and `filed_before="2016-11-03"` on CourtListener opinion searches.

During those pre-cutoff CourtListener searches for lower-court opinions in *Arthur v. State* and *Arthur v. Dunn*, two items surfaced that I disclose here and in `flags.json`:
1. The published citation metadata for the Alabama Court of Criminal Appeals' October 19, 2016 decision (*Arthur v. State*, No. CR-15-1452, `236 So. 3d 155`, opinion id `5053254`) includes a Westlaw `history` string mentioning post-cutoff history (*"Certiorari Denied by Arthur v. Alabama, U.S., April 17, 2017"*). That history string refers to the certiorari petition (`16-595`) rather than the disposition of stay application `16A450`, and I did not fold any post-November 3, 2016 information into my forecast.
2. A CourtListener search scoped to `filed_before="2016-11-03"` returned two Supreme Court orders dated **November 3, 2016** (inside the snapshot's opening day, prior to the `2016-11-04` cutoff) in Arthur's **companion** stay application `16A451` / `16-602` (*Arthur v. Dunn*, 137 S. Ct. 14 and 137 S. Ct. 15 (Nov. 3, 2016)), in which Justice Thomas entered an interim stay and the Court subsequently granted a stay of execution in `16A451` pending disposition of the petition for a writ of certiorari in No. `16-602` (Arthur's Eleventh Circuit § 1983 lethal-injection/firing-squad appeal, *Arthur v. Comm'r, Ala. Dep't of Corr.*, 840 F.3d 1268 (11th Cir. Nov. 2, 2016)). No order or outcome for `16A450` (`16-595`) appeared in any search result. Out of an abundance of caution, I have logged a `leakage-disclosure` / `data-quality` note in `flags.json`.

## 3. Base-Rate Anchoring (`metrics/statpack.md`)

Per `.github/prompts/predict.md` (*Stage: interim*), an interim application cell's skill is scored against the substantive resolved slice's grant rate pooled over application-Terms **strictly before** the cell's own Term (`application_term - 10 <= T < application_term`), provided the pooled sample reaches the pre-registered floor of `INTERIM_BASE_RATE_MIN_RESOLVED = 50` resolved substantive applications.

Reading **"The interim docket (applications)"** table in `metrics/statpack.md`:
- This cell's `term` is `2016` (from `16A450`).
- Every application-Term strictly before `2016` in the table (`2006` through `2015`) has `0` parsed substantive applications and `0` resolved substantive applications (`100%` unparsed).
- Thus, the strictly-prior pooled resolved substantive count for Term `2016` is `n = 0`, which falls below the pre-registered floor of **50** (`INTERIM_BASE_RATE_MIN_RESOLVED`).
- Per the prompt contract, because the strictly-prior pool for Term `2016` does not clear the 50-case floor, **I anchored without a published baseline** (and did not substitute the pack-level `11.6%` rate or Term `2016`'s own `8.4%` (`9/107`) rate, both of which include Term `2016` and later Terms).
- For general structural orientation only, across the modern interim docket substantive applications grant at roughly `8%–14%` unconditionally, and applications that climb the escalation ladder (response filed/requested and referred to the full Court) grant at roughly `20%–35%`.

## 4. Case-Specific Adjustments and Probability Derivation (`P(grant) = 0.28`)

### A. Procedural and Doctrinal Weakness of the Underlying Cert Petition (`16-595`)
Application `16A450` arises from the Alabama Supreme Court's denial of review (No. `1951985`, affirming Ala. Crim. App. No. `CR-15-1452`, decided Oct. 19, 2016) of Arthur's eighth successive state postconviction petition under Alabama Rule of Criminal Procedure 32. Arthur's third conviction and death sentence for the 1982 murder-for-hire of Troy Wicker became final on direct review in 1998 (*Ex parte Arthur*, 711 So. 2d 1097 (Ala. 1997), *cert. denied*, 525 U.S. 963 (1998)).

In 2016, following *Hurst v. Florida*, 136 S. Ct. 616 (Jan. 12, 2016), the Supreme Court GVR'd several Alabama capital cases that were on **direct review** (e.g., *Johnson v. Alabama*, 136 S. Ct. 1837 (May 2, 2016); *Wimbley v. Alabama*, 136 S. Ct. 2387 (May 31, 2016); *Kirksey v. Alabama*, 136 S. Ct. 2409 (June 6, 2016); *Russell v. Alabama*, 137 S. Ct. 158 (Oct. 3, 2016)). However, on September 30, 2016, the Alabama Supreme Court held in *Ex parte Bohannon*, 222 So. 3d 525 (Ala. 2016), that Alabama's capital sentencing scheme complies with *Hurst* whenever the jury's guilt-phase verdict finds a capital offense that itself establishes a statutory aggravating circumstance under `Ala. Code § 13A-5-45(e)`. More importantly, Arthur is on **collateral review** nearly twenty years after finality, and *Schriro v. Summerlin*, 542 U.S. 348 (2004), squarely held that *Ring v. Arizona* is procedural and non-retroactive under *Teague v. Lane*. Furthermore, the Alabama courts invoked state procedural bars under Rule 32.2. Consequently, the likelihood of four Justices voting to grant certiorari in `16-595` and five Justices finding a fair prospect of reversal on a collateral *Hurst* claim is low.

### B. Why `P(grant)` is `0.28` Rather Than Near Zero
Despite the weak merits/procedural posture of `16-595`, several factors support a non-trivial (`0.28`) probability of an unqualified stay grant:
1. **Active execution warrant and completed briefing:** On November 3, 2016, Arthur faced an imminent execution scheduled for that evening, and both the State's opposition and Arthur's reply were filed on the docket.
2. **Simultaneous pending applications (`16A450` and `16A451`):** Arthur simultaneously litigated two stay applications arising from the same November 3, 2016 execution warrant: `16A450` (from the state Rule 32 / *Hurst* appeal, linked to `16-595`) and `16A451` (from the 2-1 Eleventh Circuit decision issued November 2, 2016 in *Arthur v. Comm'r, Ala. Dep't of Corr.*, 840 F.3d 1268 (11th Cir. 2016), where Judge Wilson dissented at length on Arthur's firing-squad / *Glossip* claim). When a capital applicant has two stay applications pending on the night of execution, there is some chance the Court grants stays across both dockets to preserve the status quo, though it is more common for the Court to grant the stay only on the primary vehicle (`16A451`) or deny the weaker collateral application (`16A450`) once the execution date passes or when cert in `16-595` is denied.
3. **Active *Hurst*-in-Alabama controversy in late 2016:** In October–November 2016, multiple Alabama petitions challenging *Ex parte Bohannon* and Alabama's capital sentencing scheme were pending before the Court, drawing close attention from Justices Sotomayor, Breyer, Ginsburg, and Kagan.

Weighing the high likelihood of denial on a successive collateral *Hurst* petition (or mootness/denial once the November 3, 2016 warrant is stayed in the companion § 1983 appeal) against the possibility of a protective stay order, I set `probability = 0.28` (`granted = 0`, `predicted_disposition = "denied"`).

## 5. Escalation Increments and Distribution Claims (`interim-v2`)

- **`interim-disposition: 0.28`:** Matches top-level `probability` exactly.
- **`response-requested-increment: 0.02`:** `context.json` shows `response_requested: false`, and the snapshot shows that Respondent Alabama *already* filed its response on November 3, 2016 (along with Applicant's reply). Because the response is already in hand, the probability that the Court subsequently enters a formal call for a response is near zero (`0.02`).
- **`referral-increment: 0.92`:** `context.json` shows `referred_to_court: false` as of the snapshot. In capital stay applications on the eve of execution where briefing is complete, Justice Thomas nearly always refers the application to the full Court rather than disposing of it in chambers (`0.92`).
- **`amicus-increment: 0.03`:** `context.json` shows `amicus_briefs: 0`. Emergency execution-day stay applications (`16A450`) rarely attract post-response amicus filings before disposition (`0.03`).
- **`order-writers` (`claim_distributions`):** On November 4, 2016, the sitting bench had **8 Justices** (`Roberts`, `Kennedy`, `Thomas`, `Ginsburg`, `Breyer`, `Alito`, `Sotomayor`, `Kagan`) due to the vacancy between Justice Scalia's death (Feb. 13, 2016) and Justice Gorsuch's confirmation (Apr. 10, 2017). Justice Sotomayor (`0.14`) and Justice Breyer (`0.08`) were the most frequent authors of separate statements/dissents in Alabama capital and *Hurst*/method-of-execution cases during OT2016; Justice Thomas (`0.03`) occasionally wrote in response; the remaining five Justices rarely wrote separately on interim stay orders (`0.01–0.02`).

## 6. Key Uncertainties

The primary uncertainty is **procedural interaction with the companion stay application (`16A451`)**: because the application text (`application.txt`) and response text (`application-response.txt`) were not provisioned, and because Arthur had a parallel stay application (`16A451`) granted on November 3, 2016 in his Eleventh Circuit § 1983 appeal, there is a meaningful chance that `16A450` was either held until the linked cert petition (`16-595`) was denied (and then denied as moot or alongside cert denial) or granted alongside `16A451` on November 3, 2016. Since the Court's reported orders for November 3, 2016 show a grant in `16A451` (`16-602`) and no corresponding grant order in `16A450` (`16-595`), denial of `16A450` is the clear modal outcome.
