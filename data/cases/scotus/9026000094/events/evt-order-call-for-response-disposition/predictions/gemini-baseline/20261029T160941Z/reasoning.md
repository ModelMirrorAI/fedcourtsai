# Rationale for Forecast (`reasoning.md`)

## Summary of Forecast
- **Top-level `probability` (`disposition`):** `0.38` (`granted = 0`, `predicted_disposition = "denied"`)
- **`relist-increment`:** `0.98`
- **`cvsg-increment`:** `0.02`
- **`summary-disposition-route` (conditional on grant):** `0.85`
- **`dissent-from-denial` (conditional on denial):** `0.04`
- **`big_case_score`:** `0.25`

## 1. Base-Rate Anchor (`metrics/statpack.md`)

From `record/context.json`, this cell is in `forward` mode at `moment: response-requested` (`cutoff: "2026-09-04"`, `snapshot_date: "2026-09-04"`), with `term: 2026`, `band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 1`, and `cvsg_date: null`.

Following the cert-stage anchoring rule in `.github/prompts/predict.md`, I anchor on the **"Segment base rate by salience band (`sal-v4`, last 3 Terms of 6)"** table in `metrics/statpack.md`, pooling the bracketed `reached` rates for the `baseline` band over the Terms strictly preceding OT 2026:
- **OT 2024 `baseline` reached:** `2.2%` (`n = 716`, ~15.8 grants)
- **OT 2025 `baseline` reached:** `4.5%` (`n = 1,277`, ~57.5 grants)
- **Pooled prior-Term `baseline` reached rate:** `~3.7%` (~73.2 grants out of `n = 1,993` weighted petitions).

For additional context from `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall (`n = 11,488`):** `2.6%` `granted` + `0.8%` `gvr` = `3.4%` total grant family (`95.3%` `denied`).
- **Originating circuit (`ca9`, `n = 2,188`):** `2.2%` `granted` + `0.5%` `gvr` = `2.7%` grant family (`96.3%` `denied`).
- **Relist count cut (paid scored segment):** Terminal `0` relists (`n = 1,704`) has a `0.8%` grant rate (`0.7%` `granted`, `0.1%` `gvr`), whereas petitions reaching `1` relist (`n = 398`) have a `13.8%` grant+GVR rate (`7.5%` `granted`, `6.3%` `gvr`), and `2` relists (`n = 68`) have a `36.8%` grant+GVR rate (`32.4%` `granted`, `4.4%` `gvr`).
- **Amicus-brief count cut (paid scored segment):** `0` amicus briefs (`n = 683`, with `n = 1,288` `(unknown)`) shows `1.5%` `granted` and `1.2%` `gvr` (`2.7%` grant family). As of the September 4, 2026 snapshot, no amicus briefs have been filed.

## 2. Case-Specific Adjustments from the Provisioned Record

### Upward Adjustments (from ~3.7% to 38%)
1. **Compelling GVR / Hold Posture in Light of *King v. Villegas* En Banc:**
   Reading `record/documents/petition.txt` and `record/documents/questions-presented.txt`, the procedural anomaly below is unusually stark. Respondent Adolfo Cardenas pleaded no contest (*nolo contendere*) to six felony counts—including assault with a deadly weapon on a peace officer (Cal. Penal Code § 245(c)) and felony reckless evading (Cal. Veh. Code § 2800.2(a))—after a vehicle pursuit that ended with officers shooting him and deploying a police canine. In his subsequent § 1983 excessive-force suit, the district court denied summary judgment under *Heck v. Humphrey*, 512 U.S. 477 (1994), based on perceived factual disputes over whether the deadly force was distinct from the conduct supporting the convictions (Pet. App. 18a–21a).
   On interlocutory appeal, however, the Ninth Circuit panel (Pet. App. 3a–4a) did not adopt the district court's factual-distinction theory. Instead, in a single paragraph, it affirmed the denial of *Heck* summary judgment solely on the ground that an intervening Ninth Circuit panel decision—*King v. Villegas*, 156 F.4th 979 (9th Cir. Oct. 20, 2025)—held that Federal Rule of Evidence 410(a) categorically bars the admission of a *nolo contendere* plea to establish a *Heck* bar.
   On April 3, 2026, the Ninth Circuit granted rehearing en banc in *King v. Villegas* and vacated the three-judge panel decision (`171 F.4th 1163`). Yet on April 21, 2026, the *Cardenas* panel denied rehearing and rehearing en banc without modifying its memorandum disposition (Pet. App. 24a–25a). Moreover, in the *King* en banc proceedings (argued June 2, 2026, and still pending decision in the Ninth Circuit as of late October 2026), the plaintiff in *King* abandoned the panel's Rule 410(a) holding. Petitioners (represented by E. Joshua Rosenkranz and Orrick) primarily ask the Supreme Court to hold this petition pending the Ninth Circuit's en banc decision in *King* and then GVR (or GVR immediately in light of *King*'s vacatur).
2. **Call for Response (CFR) Timing:**
   According to `record/snapshots/2026-09-04.json`, respondent did not initially respond by the August 20, 2026 due date, the petition was distributed on September 2, 2026 for the September 28 conference, and the very next day (September 3, 2026) the Court requested a response (due October 5, 2026). Because the Court does not GVR or grant a petition without calling for a response, this immediate post-distribution CFR confirms that the petition's hold/GVR request caught a chambers' attention.

### Downward / Moderating Considerations (Why P(grant) is 0.38 Rather Than >0.50)
Despite the glaring *King* anomaly, there are strong reasons why the Court is still more likely than not (`62%`) to deny certiorari once the Brief in Opposition is filed:
1. **Lack of Interlocutory Appellate Jurisdiction Over *Heck* (`Swint` / `Cunningham`):**
   This case arises on an interlocutory appeal from the denial of summary judgment on qualified immunity. Under *Swint v. Chambers County Commission*, 514 U.S. 35, 51 (1995), and settled Ninth Circuit precedent (*Cunningham v. Gates*, 229 F.3d 1271, 1284 (9th Cir. 2000)), an order denying summary judgment under *Heck v. Humphrey* is not an immediately appealable collateral order, nor does it qualify for pendent appellate jurisdiction alongside qualified immunity. Furthermore, the City of Santa Maria is not entitled to qualified immunity at all. The Ninth Circuit panel itself flagged this jurisdictional problem at oral argument (Pet. 8 n.3) and in Footnote 1 of its memorandum disposition (Pet. App. 2a n.1), stating that it declined to resolve Cardenas's motion to dismiss the City's appeal for lack of interlocutory jurisdiction only because it affirmed on the merits. Once respondent files the BIO, respondent will almost certainly argue that the Ninth Circuit lacked interlocutory appellate jurisdiction over the *Heck* defense in the first place, making a GVR on the *Heck* issue futile or jurisdictionally improper.
2. **Alternative Fact-Bound Basis Below and Ongoing Trial Court Proceedings:**
   The district court never relied on Rule 410(a) or *King*; it denied summary judgment because it found genuine issues of material fact over the sequence of events during the shooting and canine deployment (a determination insulated from interlocutory review under *Johnson v. Jones*, 515 U.S. 304 (1995)). Because the case is interlocutory and returns to the district court—where the *King* panel decision is already vacated and cannot be cited as precedent—petitioners remain free to reassert their *Heck* defense at trial or on appeal from a final judgment once the en banc Ninth Circuit resolves *King*.

Balancing the strong prima facie case for a hold-and-GVR against the serious interlocutory jurisdictional and vehicle defects that the BIO will likely emphasize, I place `probability = 0.38` (`granted = 0`, `predicted_disposition = "denied"`).

## 3. Secondary Claims and Distributions
- **`relist-increment` (`0.98`):** Because the snapshot stops on September 4, 2026 (`distribution_count = 1`) right after the September 3, 2026 Call for Response, the petition will almost certainly be distributed at least once more after the response arrives (masked by the harness on `response-requested` cells for that reason).
- **`cvsg-increment` (`0.02`):** A CVSG is very unlikely in an interlocutory municipal police excessive-force case whose primary ask is a GVR tied to a pending Ninth Circuit en banc decision.
- **`summary-disposition-route` (`0.85`):** Conditional on a grant, there is an 85% probability that the disposition is a summary GVR in the cert order itself (either after holding for *King* en banc or immediately in light of *King*'s vacatur) rather than plenary merits briefing and oral argument (`15%`).
- **`dissent-from-denial` (`0.04`) and `order-writers`:** Conditional on denial, most denials on interlocutory vehicle grounds pass without separate comment, leaving a small (`4%`) chance of a dissent or statement respecting denial (most plausibly from Justice Thomas at `0.02` or Justice Alito at `0.018`).

## 4. Retrieval and Tooling Note
During retrieval, I queried the local corpus service via `uv run fedcourts query` (which succeeded) and attempted two CourtListener MCP `search` calls for *King v. Villegas* and *Cardenas v. City of Santa Maria*, which returned HTTP 429 rate-limit errors. I then used `google_web_search` to check the status of the related Ninth Circuit en banc proceeding in *King v. Villegas* (No. 23-1713), confirming that en banc oral argument took place on June 2, 2026 and the en banc decision remains pending.
