# Predicted Court Trajectory & Reasoning — *Kenneth Genalo, et al. v. D. C.* (No. 26-379)

- **Current Docket State (`2026-09-21.json`):** `distribution_count = 0`, `cvsg_date = null`, `amicus_briefs = null` (at arrival on September 21, 2026).

## 1. Conference Distributions & Relist Trajectory (`relist-increment`: 0.94)

The provisioned arrival snapshot (`2026-09-21.json`) records **zero distributions** (`distribution_count: 0`), as the petition was just docketed on September 21, 2026. Following the brief in opposition (extended to December 8, 2026) and the Solicitor General's reply, the petition will almost certainly be distributed for conference at least once in January 2027 (`P(distribution_count >= 1) = 0.94`, with the remaining 0.06 reflecting the small hazard of pre-distribution Rule 46 dismissal if D.C.'s removal proceedings terminate or moot the case). Moreover, beyond its initial conference distribution, the Court is likely to relist the petition at least once (`total distributions >= 2`, as it distributed predecessor *Genalo v. Black*, No. 25-886, three times before granting certiorari on June 15, 2026) to verify vehicle cleanliness and confirm whether the Second Circuit has entered summary affirmance in *C. v. Noem*, No. 26-1396.

## 2. Call for the Views of the Solicitor General (`cvsg-increment`: 0.01)

The Court will **not** call for the views of the Solicitor General (`cvsg-increment: 0.01`). The petition was filed by Solicitor General D. John Sauer on behalf of federal officials (ICE New York Field Office Director Kenneth Genalo, Attorney General Todd Blanche, DHS Secretary Markwayne Mullin, and Orange County Sheriff Paul Arteta), so the United States is already the petitioner.

## 3. Questions Presented & Scope of Grant

If the Court grants review (`probability: 0.78`), it will take **both Questions Presented in the petition as written**, matching its prior grant in *Genalo v. Black* (No. 25-886):
1. Whether there is a point at which an alien's detention under 8 U.S.C. § 1226(c), pending a decision on whether he is to be removed, becomes "unreasonably prolonged," such that the Fifth Amendment's Due Process Clause requires an individualized bond hearing; and
2. If so, whether, in such a bond hearing, due Process requires placing the burden on the government to justify the alien's continued detention by clear and convincing evidence.

If granted, the Court's likely merits ground will be that under *Demore v. Kim*, 538 U.S. 510 (2003), and *Jennings v. Rodriguez*, 583 U.S. 281 (2018), Congress validly mandated detention during the finite pendency of removal proceedings for the specified criminal categories in § 1226(c) without ad hoc *Mathews v. Eldridge* bond hearings after six months—or, at minimum, that due process does not shift the burden to the government by clear and convincing evidence.

## 4. Plenary Review vs. Summary Disposition (`summary-disposition-route`: 0.04)

Conditional on a grant, plenary review with full merits briefing and oral argument is overwhelmingly likelier than summary disposition (`summary-disposition-route: 0.04`). The Court already set the identical questions down for plenary briefing and oral argument in *Genalo v. Black* (No. 25-886) before that case became moot on September 11, 2026, and no intervening Supreme Court merits decision on § 1226(c) has been issued that would support a GVR. A summary reversal without argument is likewise unlikely given the deep multi-circuit split on prolonged § 1226(c) detention.

## 5. Dissent from Denial & Separate Writings (`dissent-from-denial`: 0.35)

Because the Court is likely to grant plenary review (`predicted_disposition: "granted"`), the cert order itself will likely issue without separate opinions. However, **conditional on the Court denying certiorari** (for example, out of reluctance to grant certiorari before judgment under Rule 11 or because of vehicle complications involving D.C.'s competency finding and medical record), there is a substantial conditional probability (`0.35`) that one or more Justices—most likely Justice Thomas or Justice Alito, potentially joined by Justice Gorsuch or Justice Kavanaugh—would note a dissent from the denial of certiorari or author a statement respecting denial emphasizing the importance of the circuit split left open when *Genalo v. Black* became moot.
