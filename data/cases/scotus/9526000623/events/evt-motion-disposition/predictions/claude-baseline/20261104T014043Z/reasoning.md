# Reasoning — Guardado v. Florida, 26A623 (stay of execution), arrival moment

**P(stay granted in whole or part) = 0.015.**

## Record
- Snapshot `2026-10-31.json` (arrival-position cut, anchor index 0): one entry — the Oct 30, 2026 application for a stay of execution, submitted to Justice Thomas as Circuit Justice for the Eleventh Circuit. Capital case; linked with cert petition 26-6013 (filed the same day, 0 distributions per a corpus lookup). Execution set for Nov 5, 2026, 6:00 p.m.
- Context: forward mode, `band: null` (normal for interim), no response requested, not referred, 0 amicus.
- `record/documents/application.txt` (5 pages, not truncated, not OCR). The application asks for a Rule 23 / § 2101(f) stay pending the concurrently filed cert petition from the Florida Supreme Court's Oct 29 denial. Its only substantive theory: Florida's clemency process violates due process because no death-sentenced prisoner has received clemency since 1983 and the Governor has said he will not grant clemency to murderers, so the process is a predetermined "coin flip" under Justice O'Connor's *Woodard* concurrence. The application is short and generic. It names no split, gives no Florida Supreme Court analysis beyond saying that court follows the *Woodard* concurrence, and does not take on the State's finality interest beyond calling it "minimal."

## Anchor
- The statpack's interim section has no published baseline for my pool. In `statpack.json`, every application-Term from 2016 to 2025 has `finer_granted`/`finer_resolved` = 0/0 and `finer_unread` equal to its whole resolved count. The prompt's rule requires zero unread in every pooled Term, so this pool fails it. **I anchored without a published baseline.** For shape only, the older registered `substantive_granted/resolved` reading over 2016–2025 pools to 160/1466 ≈ 10.9%. That slice is mostly non-capital stays and injunctions, including government applications that win often, so it overstates a capital prisoner's odds badly.
- My working prior comes from general knowledge of the Court's practice. Stays of execution filed on a warrant timeline almost never succeed: well under 5%, and close to 0% for Florida warrant litigation in 2023–2026. Florida's record pace of executions under Governor DeSantis has drawn many last-minute applications. The clemency-arbitrariness theory in particular has been raised by Florida CCRC counsel in earlier warrant cases and denied each time, as far as I know without a noted dissent on that ground.

## Adjustments
- Down: the claim relies on a single-Justice concurrence (*Woodard*) and asks the Court to find a whole state clemency regime arbitrary. That has no foothold with the current majority. The application is cursory, with no split and no new evidence.
- Small residual: a capital case brings some irreparable-harm weight, and one Justice may write. Neither changes the grant probability.

## Ladder claims
- Response requested (0.08): in capital cases the State usually files a response on its own without a formal call. A formal docketed request is uncommon, and the State's uninvited response does not count.
- Referral to the full Court (0.9): Circuit Justices routinely refer execution-stay applications to the Court, and the docket usually records "referred to the Court." The residual covers a Thomas-alone denial or a docket that never records the referral.
- Amicus (0.03): amicus briefs on Florida warrant stays are rare.

## Uncertainty
I have not seen the cert petition or the Florida Supreme Court's opinion. The petition may raise other questions (the application mentions the Sixth and Eighth Amendments only in passing). A strong unpleaded issue could raise the odds, but nothing on my record suggests one.
