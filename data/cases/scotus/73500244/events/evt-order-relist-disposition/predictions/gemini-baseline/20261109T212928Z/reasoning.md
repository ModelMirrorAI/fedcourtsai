# Predictor Rationale (`scotus/73500244` — `evt-order-relist-disposition`)

## Summary Call

- **`probability` / `disposition`**: `0.32` (`granted: 0`, `predicted_disposition: "denied"`)
- **`relist-increment`**: `0.45`
- **`cvsg-increment`**: `0.005`
- **`summary-disposition-route`**: `0.04`
- **`dissent-from-denial`**: `0.28`
- **`big_case_score`**: `0.55`

## 1. Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

This is a forward-mode `cert`-stage prediction at `moment: relist` (`opened_at: 2026-11-09`). The provisioned conditioning state in `record/context.json` freezes:
- `term`: `2025` (No. 25-1342, paid petition)
- `band`: `"high"` under `salience_version: "sal-v8"`
- `distribution_count`: `3` (distributed for the Conferences of October 16, 2026, November 6, 2026, and November 13, 2026—i.e., two relists)
- `cvsg_date`: `null`
- `cert_anchor`: `rate = 0.3455056179775281` (~34.6%), pooled over `lookback_terms = 10` strictly prior Terms (OT2017–OT2024, `n = 712` weighted resolved cases in the `high` band `[reached]` column of `metrics/statpack.md`).

Cross-checking against the marginal cuts in `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall** (`n = 45,537` resolved): denied `95.2%`, dismissed `2.0%`, granted `1.4%`, GVR `1.4%` (`2.8%` grant family).
- **Originating circuit (`ca11`, modern cert)** (`n = 3,954` resolved): denied `94.9%`, GVR `2.1%`, dismissed `1.8%`, granted `1.2%` (`3.3%` grant family).
- **Relist count cut (paid scored segment)**:
  - Pooling all relisted buckets `1+` (`n = 2,532 + 495 + 483 = 3,510` resolved) gives a `19.9%` grant-family rate (`13.5%` in bucket `1` [`8.3%` granted, `5.2%` GVR, `n = 2,532`]; `41.2%` in bucket `2` [`28.3%` granted, `12.9%` GVR, `n = 495`]; and `37.3%` in bucket `3+` [`23.2%` granted, `14.1%` GVR, `n = 483`]).
  - Focusing on petitions that have reached at least two relists (`relist_bucket = 2` and `3+`, `n = 978` resolved), the grant-family rate is `39.3%`, composed of `25.8%` plenary grants and `13.5%` GVRs. In `relist_bucket = 2` specifically (`n = 495`), the plenary grant rate is `28.3%` and the GVR rate is `12.9%`.
- **Amicus-brief count cut (paid scored segment)**: `0` amicus briefs (`n = 11,109` resolved) has a `3.8%` grant-family rate (`2.0%` granted, `1.8%` GVR), though that marginal cut mostly reflects non-relisted petitions.

Crucially, both the `high` band's `34.6%` anchor and `relist_bucket = 2`'s `41.2%` grant-family rate include a substantial share of summary GVRs (~12–13 percentage points of the total rate, or roughly one-third of all grants in the bucket), which come from held petitions awaiting a merits decision or Solicitor General confessions of error. Here, there is no pending Supreme Court merits case on 18 U.S.C. § 1201(a)(1) or *Lopez* category-two instrumentalities for which *Brown* could be held, and no GVR basis. Benchmarking against the plenary-grant component (~26–28% in the `2` and `3+` relist buckets) while accounting for the fact that both relists here are genuine post-conference relists rather than pre-conference reschedules yields a starting baseline of roughly `30–35%`.

## 2. Case-Specific Evidence from the Snapshot, Staged Filings, and Priors

All provisioned documents in `record/documents/` were read (`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `appendix.txt`, `decision-below.txt`, and `lower-court-docket.txt`; none had `empty_text: true` or `ocr_derived: true`). Note that while `lower-court-docket.txt` reported `petition filed: no` for rehearing en banc based on a single post-judgment CourtListener docket entry, `appendix.txt` (Appendix C, p. 30a) and the SCOTUS snapshot confirm that a petition for rehearing en banc was filed and denied by the Eleventh Circuit on February 24, 2026 with no judge requesting a poll.

### Factors Pushing Toward Certiorari
1. **A Square, Freshly Deepened Circuit Split on a Recurring Federal Criminal Statute:**
   - Five courts of appeals—the First (*United States v. Prochilo*, 629 F.3d 264 (1st Cir. 2011)), Sixth (*United States v. McHenry*, 97 F.3d 125 (6th Cir. 1996)), Seventh (*United States v. Mandel*, 647 F.3d 710 (7th Cir. 2011)), Ninth (*United States v. Vega-Castillo*, 548 F.3d 980 (9th Cir. 2008)), and Eleventh Circuits (*United States v. Bryan*, 159 F.4th 1274 (11th Cir. Nov. 2025), applied below in *Brown*)—hold that automobiles are *per se* instrumentalities of interstate commerce under the second category of *United States v. Lopez*, 514 U.S. 549, 558 (1995), so any intrastate kidnapping using a car satisfies 18 U.S.C. § 1201(a)(1) without a case-specific interstate nexus.
   - In June 2025, the Tenth Circuit in *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025) (2–1), squarely parted ways with those circuits, holding that treating motor vehicles as *per se* instrumentalities of interstate commerce would violate the Commerce Clause by federalizing virtually every local kidnapping, and construing § 1201(a)(1) under *Bond v. United States*, 572 U.S. 844 (2014), to require an individualized nexus to interstate commerce. Judge Rosenbaum likewise dissented at length in *Bryan*, 159 F.4th at 1299–1311, arguing that the statutory text ("any means, facility, or instrumentality of interstate or foreign commerce") requires that the instrumentality be used *in* interstate commerce.
   - The Solicitor General acknowledges in the BIO (at 14–17) that *Chavarria*'s reasoning conflicts with the Eleventh Circuit's rule, and the government chose not to seek en banc review or certiorari in *Chavarria*.
2. **Deliberate Differentiation from the Companion Eleventh Circuit Petition (*McMichael*, No. 25-7371):**
   - The BIO (at 14 n.2) noted a pending petition raising a similar contention: *Travis McMichael v. United States*, No. 25-7371 (the direct petition from *United States v. Bryan*, 159 F.4th 1274). Corpus query (`uv run fedcourts query --court scotus --docket-number 25-7371`) shows that *McMichael* was distributed for the exact same October 16, 2026 conference as *Brown* and was **denied on October 19, 2026** after a single distribution (`distribution_count = 1`), whereas *Brown* was held over and has now been relisted twice (`distribution_count = 3`).
   - As the petition in *Brown* explained (Pet. 14), the defendants in *Bryan*/*McMichael* did not raise any constitutional Commerce Clause challenge on appeal (*Bryan*, 159 F.4th at 1281), and their prosecution involved high-profile federal civil-rights murder convictions alongside attempted kidnapping. In *Brown*, by contrast, petitioner preserved both the statutory and Commerce Clause challenges at every stage (pretrial motion to dismiss, Rule 29 motion, appeal, and cert petition; App. 14a–27a), and kidnapping (plus conspiracy to kidnap) is the entire conviction. The Court's decision to deny *McMichael* immediately while relisting *Brown* twice is strong evidence that at least several Justices view *Brown* as the serious candidate vehicle for the § 1201(a)(1) split.
3. **Experienced Supreme Court Clinic Counsel and Strong Doctrinal Salience:**
   - Petitioner is represented by Stuart Banner and the UCLA School of Law Supreme Court Clinic, and the federalism/overcriminalization theme aligns closely with this Court's decisions in *Lopez*, *Morrison*, *Jones*, *Bond*, and *Dubin*.

### Factors Pushing Against Certiorari (Vehicle Obstacles)
1. **The Alternative Cell-Phone Instrumentality Evidence and Abandonment Footnote:**
   - The government's primary vehicle objection (BIO 8–10, 17–21) is substantial. At trial, the indictment and jury instructions permitted the jury to find the interstate-commerce element based on an automobile, cell phones, the internet, or a GPS tracker. When denying Brown's Rule 29 motion, the district court specifically relied on evidence that the kidnappers used cell phones during the kidnapping to coordinate the abduction and demand the $50,000 ransom, including leaving a phone in the abandoned car's glove box (App. 17a, 24a–25a).
   - In Footnote 1 of the decision below (App. 5a n.1), the Eleventh Circuit observed that Brown did not challenge on appeal the sufficiency of the cell-phone evidence or binding circuit precedent (*United States v. Evans*, 476 F.3d 1176 (11th Cir. 2007)) holding that cell phones are instrumentalities of interstate commerce even when used intrastate, and stated that she "abandoned any challenge to the government's theory that she used cellphones as an instrumentality of interstate commerce during the kidnapping."
   - Moreover, even the Tenth Circuit in *Chavarria*, 140 F.4th at 1265–66, reaffirmed its prior holding in *United States v. Morgan*, 748 F.3d 1024 (10th Cir. 2014), that cell phones and the internet *are* facilities/instrumentalities of interstate commerce.
   - Petitioner's reply brief offers a plausible response (Cert Reply 7–9): because the jury returned a general verdict after the prosecutor told the jury in summation that driving the car a tenth of a mile satisfied the element, *Yates v. United States*, 354 U.S. 298 (1957), and *Hedgpeth v. Pulido*, 555 U.S. 57 (2008), would require the government to establish harmlessness beyond a reasonable doubt on remand rather than insulating the Eleventh Circuit's sole ground of decision from review. Nevertheless, the high likelihood that Brown's conviction would be sustained on remand on the cell-phone theory—and that her conduct would satisfy § 1201(a)(1) even in the Tenth Circuit—makes *Brown* an imperfect vehicle and creates a real risk that four Justices will prefer to await a kidnapping or carjacking case involving only a motor vehicle.
2. **Unpublished Decision Below and No Amicus Briefs:**
   - The Eleventh Circuit decision below is unpublished and per curiam (simply applying *Bryan* from a month earlier), and no amicus briefs were filed at the cert stage.

## 3. Synthesis and Uncertainty

Balancing the strong signal of two post-conference relists after *McMichael* was denied at the first conference against the serious cell-phone alternative-ground vehicle problem, I set `probability = 0.32` (`predicted_disposition = "denied"`, `granted = 0`). My main uncertainty is whether four Justices are willing to look past the cell-phone harmless-error issue (leaving harmlessness under *Hedgpeth* for remand) in order to resolve the *Chavarria*/*Bryan* conflict now, or whether the relists instead reflect one or two Justices (most likely Justice Thomas or Justice Gorsuch) drafting a dissent from or statement respecting the denial of certiorari (`dissent-from-denial = 0.28`).
