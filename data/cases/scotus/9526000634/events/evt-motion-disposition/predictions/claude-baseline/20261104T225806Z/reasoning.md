# Reasoning — scotus/9526000634 (26A634), evt-motion-disposition (interim, arrival)

**P(stay granted in whole or in part | not mooted) = 0.015.**

## Record
- Snapshot `2026-11-04.json` (arrival-position cut at index 0): one entry, the Nov 3, 2026
  submission to Justice Thomas (Circuit Justice, CA11) of an application for a stay of
  execution. Capital case; execution set for Nov 5, 2026, 6:00 p.m. Linked with cert petition
  26-6051 (corpus row shows it docketed Nov 3, undisposed, 0 distributions).
- `context.json`: forward mode, band null (normal for interim), no response requested, not
  referred, 0 amicus briefs.
- `application.txt` (18 pp., not truncated, not OCR). Guardado, through the CHU of the Federal
  Defender (N.D. Fla.), asks for a stay pending the cert petition from the Eleventh Circuit's
  denial of a stay in his 42 U.S.C. § 1983 method-of-execution suit. The claim is an Eighth
  Amendment *maladministration* theory: Florida's drug logs suggest missing/undocumented
  etomidate removals, Wite-Out alterations of expiration dates, possibly expired or
  under-dosed etomidate, and disparate postmortem etomidate levels. The district court held an
  expedited evidentiary hearing, credited the State's witnesses (record-keeping errors only;
  toxicology showed etomidate present), and denied a stay; the Eleventh Circuit affirmed the
  denial and additionally faulted Guardado for delay (could have sued nine months earlier, as
  Heath and Trotter did), with Judge Jill Pryor concurring and noting Florida's 18 executions
  this year. The application's main grievances are the warrant-driven compressed schedule /
  limited discovery and the Eleventh Circuit's delay holding.

## Anchor
The statpack's interim section (pack in the repo at run time) lists substantive grant rates per
Term, but in `statpack.json` every pooled Term 2016–2025 carries `finer_granted = finer_resolved
= 0` with `finer_unread` equal to the whole resolved count. The prompt makes the baseline exist
only where every pooled Term's `finer_unread` is zero, so **no published baseline applies to
this cell**; I anchored without one. For shape only, the older substantive reading runs ~8–14%
per Term — but that slice mixes all stay/injunction asks, including government applications
that are granted far more often.

The relevant reference class is capital stay-of-execution applications, which the modern Court
denies almost uniformly, and method-of-execution § 1983 stays especially (Bucklew, Barr v. Lee,
and Hill/Nelson's emphasis on the State's interest in timely enforcement and the strong
equitable presumption against last-minute claims). Every Florida execution in the 2025–26 run I
am aware of went forward with SCOTUS stay applications denied, usually without noted dissent
or with only liberal Justices dissenting.

## Adjustments
- Down: two courts' factual findings against him after an evidentiary hearing (clear-error
  territory); an independent delay holding below; maladministration claims require showing a
  substantial risk of severe pain *and* the Court has never granted a stay on such a theory;
  the Circuit Justice is Thomas.
- Slight up (keeps it off the floor): the claim was filed before the warrant, so the delay
  rationale is weaker than usual; Wite-Out alterations are an unusual fact; a CA11 judge wrote
  separately. These might draw a liberal dissent, not five votes.

## Ladder claims
- Response requested (0.07): In Florida capital cases the State routinely files its response
  without a formal call; a formal "response requested" entry is uncommon on this timeline.
- Referral (0.85): Capital stay applications are almost always referred by the Circuit Justice
  to the full Court ("presented to Justice Thomas and by him referred to the Court"). Residual
  risk is how the referral is captured on the docket.
- Amicus (0.04): Rare on a 48-hour capital stay.

## Uncertainty
I did not see the Eleventh Circuit opinion itself or the State's response (none staged at this
moment). The order-writers distribution reflects that liberal Justices occasionally write in
Florida execution cases, but most denials issue without written opinions.
