P(grant) 0.82. The case involves a highly consequential question regarding whether statements made by President Trump fall within the scope of his federal office under the Westfall Act. Because the Second Circuit rejected the Attorney General's certification, the United States is petitioning for certiorari.

Under the project's statpack, a petition filed by the United States falls into the `federal` salience band, which historically commands a high baseline grant rate. For the arrival moment (Term 2026), I anchored on the weakest bracketed `reached` rate for the `federal` band in the prior Terms, which ranges from roughly 52% to 90% (averaging ~70% over the last few terms). I adjust this up to 82% because the specific issue involves the immunity of a former President, the separation of powers, and the overturning of a federal executive action, which makes it a uniquely compelling vehicle for Supreme Court review.

The CourtListener MCP server returned a 429 Rate Limit Exceeded error during my attempt to retrieve precedent. Following the pipeline rules, I degraded gracefully and relied entirely on the provisioned snapshot, the filed questions-presented text, and the committed statpack base rates to form this prediction.

Regarding the declared claims:
- Relist: The modern Court routinely relists cases it intends to grant, so P(relist-increment) tracks slightly above P(grant) at 0.85.
- CVSG: The United States is already a party (the petitioner), making a CVSG virtually impossible (0.01).
- Summary Route: The issue is momentous and legally complex, strongly indicating plenary review with argument over a summary disposition (0.05).
- Dissent from denial: If the Court denies the US petition in this posture, it is highly likely (0.70) that conservative justices would write a dissent from denial.
