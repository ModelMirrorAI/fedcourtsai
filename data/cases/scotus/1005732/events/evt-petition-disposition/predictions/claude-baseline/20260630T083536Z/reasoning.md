# scotus/1005732 — evt-petition-disposition

**Case:** Rohan Alexander Walters v. United States (No. 02-5080)
**Court:** Supreme Court of the United States, on petition for a writ of certiorari
**Appeal from:** United States Court of Appeals for the Fourth Circuit
(originating docket 01-7203)

## Legal question

Whether the Supreme Court grants Walters's petition for a writ of certiorari.
The event's `decision_target` is the disposition of the petition; in practice
this is a binary cert grant/deny call (granted ⇒ the Court takes the case;
otherwise the petition is denied).

## Governing standard

Certiorari is wholly discretionary (Sup. Ct. R. 10): "Review on a writ of
certiorari is not a matter of right, but of judicial discretion." The Court
typically grants only where there is a genuine, entrenched conflict among the
courts of appeals or with this Court's precedent, or an important unsettled
federal question. The realized base rate is the dominant prior: the Court
disposes of roughly 7,000–8,000 petitions per Term and grants on the order of
60–70 — under ~1% overall, and far lower for the *in forma pauperis* / pro se
docket, where grants are a fraction of a percent.

## Facts from the snapshot that drive the outcome

- **In forma pauperis petition.** The docket number is **02-5080**. SCOTUS
  numbers IFP petitions with the 5000+ block within a Term (paid petitions take
  the low numbers); No. 02-5080 is therefore an IFP filing — the indigent, almost
  always pro se, docket whose grant rate is well under 0.5%.
- **Criminal posture against the United States.** A prisoner/criminal petitioner
  challenging a Fourth Circuit judgment. The originating circuit docket
  (01-7203) is itself in the IFP range, consistent with a pro se criminal appeal.
  These petitions rarely present the kind of clean, acknowledged circuit split
  the Court looks for.
- **No positive cert signal in the record.** `date_cert_granted` and
  `date_cert_denied` are both null; `date_argued` is null; the panel is empty;
  there are no docket entries, no associated cluster indicating a merits opinion,
  and `date_terminated` is null. Nothing in the snapshot suggests the Court has
  shown interest (no CVSG, no relisting signal, no merits scheduling).
- **Snapshot only.** Per the contract I predict solely from the 2026-06-30
  snapshot and do not fetch new docket facts.

## Reasoning behind the probability

Every available signal pushes toward the overwhelming base-rate outcome of
denial: an IFP, pro se criminal petition with no indication of a circuit split
or any Court interest. There is no countervailing factor (no CVSG, no relist, no
high-profile question) that would lift this above the IFP grant rate. I set
**P(granted) = 0.005**, predicted disposition **denied**, with high confidence
(0.95). I leave a small residual probability rather than zero to account for the
rare IFP grant and for the chance that the snapshot simply lacks a
later-recorded disposition.

No per-judge votes are predicted: cert denials are typically issued by order of
the Court without recorded individual votes.
