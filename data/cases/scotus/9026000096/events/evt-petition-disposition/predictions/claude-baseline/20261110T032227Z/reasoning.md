# Reasoning — scotus/9026000096 (No. 26-96), evt-petition-disposition

**P(any grant) = 0.66.**

## Inputs read
- Snapshot `record/snapshots/2026-11-10.json`: SG-filed paid petition (Department of the Interior v. Shoshone-Bannock Tribes), docketed Jul 2026; five amicus briefs (Chamber of Commerce, National Mining Association, NAM/Fertilizer Institute, Mountain States Legal Foundation, and the Governors of Idaho, Nevada and Utah), all VIDED with the companion; BIO filed Oct 21; reply Nov 3; distributed once, for the Dec 4, 2026 conference. No CVSG, which can't apply here because the United States is the petitioner.
- `record/context.json`: forward mode, band `federal` (sal-v8), `distribution_count` 1, `cert_anchor.rate` 0.731 (10-Term lookback).
- `record/related/26-109.json` (relation `Vide`): J.R. Simplot Co.'s companion petition from the same Ninth Circuit judgment, also distributed for the 12/4 conference. The two will almost certainly be handled together.
- Documents: QP, petition (reasons section), BIO (no split, importance, interlocutory/vehicle sections), cert reply, lower-court docket summary (en banc rehearing denied with dissent noted). I did not read the decision below in full. I relied on the petition's account of it: a published panel opinion with a Bumatay dissent, and Collins and Tung dissents from denial of rehearing en banc, which per the reply drew six judges on the alternative grounds.

## Anchor
The federal-band reached rate pooled over prior Terms is 0.731 (`cert_anchor`). Statpack rows OT2017–OT2025 range from 47.6% to 96.3%, on small n (12–43 per Term).

## Adjustments
- **Up:** The SG is the petitioner and stresses large stakes: more than 4M acres of federal land nationally, 2.4M of them in the Ninth Circuit. The decision below is published and drew a panel dissent plus dissents from denial of en banc. Three Western governors and industry groups support review. The SG's selectivity is the main reason federal petitions grant at this rate.
- **Down:** There is no circuit split, and the BIO says so credibly. The posture is interlocutory: the district court still has to rule on remedy. The district court's alternative FLPMA and NEPA holdings were not reached on appeal, which the BIO frames as a reason the case isn't outcome-determinative. Indian-law reserved-rights framing may draw some resistance from Justices (e.g., Gorsuch) who are protective of tribal interests. A Senate NDAA provision would ratify the exchange, and the SG itself suggests a "brief deferral" while Congress acts.
- **The NDAA wrinkle cuts both ways for the grant flag.** If Congress ratifies, the SG asks for a Munsingwear GVR, which counts as a grant. If Congress does not, a plenary grant looks likely. The main denial paths are (a) the Court denies outright on interlocutory/no-split grounds, or (b) Congress ratifies and the Court simply denies as moot or academic instead of vacating.

Net result: slightly below the anchor, at 0.66.

## Increments
- relist-increment 0.55: The deferral request and the pending NDAA (which typically passes in December) make a reschedule or relist past Dec 4 fairly likely. A grant at the first conference is the main path to no further distribution.
- cvsg-increment 0.01: The United States is the petitioner.
- summary-disposition-route 0.25 (conditional on grant): mostly the Munsingwear-vacatur path if the NDAA ratifies the exchange.
- dissent-from-denial 0.30 (conditional on denial): a denial of an SG petition with en banc dissents below could draw an Alito/Thomas writing. A denial driven by the interlocutory posture would likely draw none.

## Uncertainty
The biggest unknown is the NDAA's content and timing. I made no web retrieval to check its status.
