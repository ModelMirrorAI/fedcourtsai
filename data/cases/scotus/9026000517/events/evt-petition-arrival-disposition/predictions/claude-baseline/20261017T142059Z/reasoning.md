# Why P(grant) = 0.004

**Inputs.** I read `record/snapshots/2026-10-17.json` and `record/context.json` (mode `forward`, band `baseline` under `sal-v4`, distribution_count 0, no CVSG, Term 2026). No documents were provisioned, so there was no QP, petition, or BIO to read. That limits how far I can judge the merits.

**Anchor.** This is an arrival-moment cert cell with a private petitioner, so per the prompt I anchor on the `baseline` class floor. That is the bracketed `reached` figure in `metrics/statpack.md`'s *Segment base rate by salience band (sal-v4)*, pooled over Terms 2017–2025, which are strictly before Term 2026. Pooled it comes to about **5.0%**: roughly 644 weighted grants over roughly 12,877 weighted petitions. The table's heading version matches my context's `salience_version`.

**Adjustments (strongly down).**
- **The petitioner is pro se.** The snapshot names the petitioner, Alejandro E. Perez, as their own counsel of record. Paid pro se petitions are granted far below the paid segment's average. The 5% baseline is driven mostly by petitions with counsel, including the specialist Supreme Court bar.
- **Private civil dispute against a corporate respondent**, from the Fifth Circuit, with no government party and nothing in the caption suggesting a recurring legal question.
- **A stale, odd timeline.** The Fifth Circuit decision is dated 2024-10-07. The only proceedings entry reads "Petition for a writ of certiorari filed" on Nov 07 2024, yet the case was docketed 2026-10-16 with a response due 2026-11-16. That suggests a long filing or correction history, and possibly a timeliness or vehicle problem. I cannot resolve it from the record.

I land at 0.4%. That is below the class floor by roughly an order of magnitude, but not zero, because occasionally a pro se petition draws a GVR.

**Other claims.** relist-increment 0.95: some distribution almost always follows, unless the petition is withdrawn or dismissed under Rule 39 or 46. cvsg-increment 0.002. summary-disposition-route 0.30, conditional on a grant. dissent-from-denial 0.01.

**Where to discount me.** I never saw the petition. If it raises a real circuit split, despite the pro se framing, my number is too low. Retrieval was limited to two CourtListener searches; one returned nothing and the other failed on a malformed court filter (see `retrieval.md`).
