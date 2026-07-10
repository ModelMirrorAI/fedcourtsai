# Prediction: denied

## Event

The event is the disposition of the petition for a writ of certiorari in Andron Miguel Francis v. Allstate Insurance Company, Supreme Court docket 25-1218. The July 10, 2026 snapshot shows the petition was docketed on April 24, 2026, from the Court of Appeals of Georgia, with a lower-court decision dated May 5, 2025 and a discretionary-court decision dated September 30, 2025. The petition was distributed for the September 28, 2026 conference.

## Record Used

I used the event definition, the July 10, 2026 docket snapshot, the documents manifest, and the committed statpack base-rate context. The provisioned petition text file contained only blank lines, despite the manifest listing a 10-page petition PDF as fetched and not truncated, so I could not anchor on the questions presented or petition argument. No brief in opposition was provisioned; the docket instead records Allstate's waiver of the right to respond.

## Governing Standard

Certiorari is discretionary. The useful prediction standard is whether the petition appears likely to satisfy Supreme Court Rule 10: a conflict among courts, an important unsettled federal question, or another unusually compelling reason for review. Mere error correction in a fact-bound state-court dispute is a weak basis for certiorari.

## Case-Specific Assessment

The visible docket signals are weak for a grant. The case comes from a state intermediate appellate court in a private insurance dispute. The snapshot does not reveal a federal constitutional or statutory question, a lower-court split, government-party involvement, a call for the Solicitor General's views, relisting, or any request by the Court for a response. The respondent waived response after obtaining an extension, which is not dispositive but is consistent with an ordinary low-probability petition.

The committed statpack's resolved SCOTUS slice is small and imperfect, but it reinforces the general baseline that grants are rare. It reports 4 grants among 296 resolved SCOTUS rows, about 1.4%, and the prompt's modern discretionary-cert guidance likewise indicates a low single-digit grant rate. Given the pro se-style docket posture, absence of any visible vehicle or split signal, and waiver of response, I put this petition below the ordinary paid-cert baseline.

## Probability

I predict denial, with P(granted) = 0.01. Confidence is moderate rather than high because the petition OCR was blank, so the actual questions presented were not available from the provisioned record. I omitted votes because cert-stage votes are not ordinarily public and no judge-specific prediction is supported by the record.
