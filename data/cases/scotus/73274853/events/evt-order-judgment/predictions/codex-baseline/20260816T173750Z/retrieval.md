# Retrieval

- Read the committed `metrics/statpack.md`, section "The merits docket (granted cases)," and pooled the available strictly prior grant Terms 2017-2024: 359 disturbed judgments among 515 parsed judgments (69.7%).
- Attempted five CourtListener MCP opinion searches by citation: *PennEast Pipeline Co. v. New Jersey*, 594 U.S. 482; *United States v. Kimbell Foods*, 440 U.S. 715; *United States v. Miller*, 317 U.S. 369; *Georgia Power Co. v. 138.30 Acres*, 617 F.2d 1112; and *Sabal Trail Transmission, LLC v. 18.27 Acres of Land*, 59 F.4th 1158. Each returned HTTP 429 (daily rate limit exceeded), so none supplied substantive material.
- Attempted `uv run fedcourts query --court scotus --citation '594 U.S. 482' --limit 1 --full` and `uv run fedcourts query --court scotus --citation '440 U.S. 715' --limit 1 --full`. The commands printed neither results nor a `ranged corpus reads` line.
- Retried `uv run fedcourts query --court scotus --citation '594 U.S. 482' --limit 1 --corpus-backend service --full`. It produced no output before timeout and was terminated; no `ranged corpus reads` line was printed.
- Retrieved and read the official pre-grant Brief for the United States as Amicus Curiae from the Supreme Court docket link recorded in the snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-159/409699/20260522181308374_Hoffmann-5.22-final.pdf`.
- An independent research pass checked the official Supreme Court docket and the pre-decision authorities cited in the provisioned filings; it did not inspect an outcome, another prediction, or any post-decision material.
