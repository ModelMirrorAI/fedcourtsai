# Reasoning — Texas v. Black, No. 26-335 (P(any grant) = 0.42)

## Inputs read
- Snapshot `record/snapshots/2026-11-08.json`: petition filed Sep 9 2026; Repole Stable amicus (VIDED with 26-199, 26-201, 26-332); FTC/SG memorandum in opposition and HISA Authority BIO (both VIDED across 26-332/26-335/26-430), Oct 13; Texas reply Oct 26; **distributed once**, for the 12/4/2026 conference. No CVSG (a federal party is a respondent).
- `record/context.json`: forward mode, band `state` (sal-v8), distribution_count 1, `cert_anchor.rate` = 0.233 (10-Term pooled reached rate for the `state` band).
- Documents: questions-presented, petition (truncated at the appendix), the combined BIO (SG memo + Authority BIO), and the cert reply. None empty or OCR-derived.
- `record/related/26-332.json` (relation `vided-amicus`, one shared brief): Gulf Coast Racing v. HISA, the Appointments Clause cross-petition from the same Fifth Circuit judgment, also first distributed for 12/4. It is in fact a true companion (the BIO caption treats 26-332/26-335/26-430 together).

## Posture that drives the number
On remand after the 2025 GVR in light of *FCC v. Consumers' Research*, the Fifth Circuit (June 11, 2026) held HISA's **enforcement** provisions unconstitutional under private nondelegation but upheld the **rulemaking** provisions. The SG and the Authority have their own petitions (26-199 per the live docket; the SG memo says the federal government also petitioned) on the enforcement holding, and every challenger agrees those should be granted. Texas's petition is the challengers' cross-petition on the rulemaking holding. The SG and the Authority oppose it: no circuit conflict post-*Consumers' Research* (the Fifth Circuit here and the Sixth Circuit in *Oklahoma v. United States*, No. 25-1325, both upheld rulemaking).

Live docket (supremecourt.gov, fetched this run): 25-1325 (*Oklahoma*, the same rulemaking question from CA6) was distributed for 10/9/2026, **rescheduled** on Sep 21, and is now distributed for 12/4/2026 alongside 26-199, 26-332 and 26-335. The Court is clearly considering the whole HISA cluster together.

## Anchor and adjustments
- Anchor: `cert_anchor` 0.233 (state band reached rate; per-Term `state` reached rates 14–39% across OT2017–OT2025).
- Up: the government's petition defending a federal statute held unconstitutional is near-certain to be granted (federal petitioner, statute invalidated). When the Court takes the enforcement holding, it has a real incentive to take the companion rulemaking question in the same case, so the whole private-nondelegation framework under *Consumers' Research* is settled at once. Several Justices (Alito's *Amtrak* concurrence, Gorsuch, Thomas) are interested in private nondelegation. And a hold-then-GVR after the merits decision also counts as a grant.
- Down: the SG and Authority note no split. The Court could take only the enforcement question and then deny the held cross-petitions after deciding it, or pick *Oklahoma* (25-1325) as the rulemaking vehicle and hold or deny Texas. A grant of the cross-petition in the same case seems somewhat likelier than a grant in *Oklahoma*, but splitting the probability across vehicles weighs against Texas.
- Net: about 0.42 for any grant, including a later GVR. I named `denied` because the number is below 0.5. This is a near coin-flip, and a reader should treat it as one.

## Uncertainties
- I did not verify 26-201's identity (the SG memo says the government also petitioned). I fetched only 26-199, 25-1325 and 26-335.
- How the Court will treat cross-petitions when it grants the government's petition is the crux, and I have no committed base rate conditioned on that.
- The corpus shows the prior HISA round (24-433) ended in a GVR. That is context only.
