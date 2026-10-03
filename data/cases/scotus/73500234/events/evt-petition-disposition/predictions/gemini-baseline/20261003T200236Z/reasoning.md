# Reasoning

P(grant) is 0.04. The petition is a second trip to the Court after a 2023 reversal. The petitioner challenges the lower court's application of the law of the case doctrine and the discovery rule for the Quiet Title Act on remand. However, the application of the law of the case doctrine to issues not explicitly decided by the Supreme Court is generally a fact-bound inquiry unlikely to warrant further review. The government's brief in opposition strongly contends that the lower courts simply applied settled law to the specific procedural posture of this case.

I anchor on the pooled `baseline` salience band's bracketed "reached" rate across Terms 2017-2024, which is approximately 5.2%. This is appropriate since the petitioner is a private party. The petition is at its first distribution (relist count 0), which does not elevate the probability significantly. The case lacks compelling circuit split dynamics on the specific discovery rule issue raised.

`big_case_score` is set to 0.1, as the case involves a narrow procedural issue on remand rather than a broad question of national significance.

For the claims:
- `disposition`: 0.04
- `relist-increment`: 0.05 (most petitions are denied after their first conference without relists).
- `cvsg-increment`: 0.0 (the United States is already a party and represented by the Solicitor General, so a CVSG is impossible).
- `summary-disposition-route`: 0.05 (no intervening change in law to support a GVR).
- `dissent-from-denial`: 0.03 (fact-bound case).
