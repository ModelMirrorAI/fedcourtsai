# Prediction: Minor v. Tillotson

## Event

The event asks for the disposition of the SCOTUS petition baseline event in `scotus/1034900`: whether the petition is granted and, more specifically, which disposition label best fits.

## Governing Standard

For a modern certiorari petition, Supreme Court review is discretionary. A grant generally requires at least four Justices to vote to hear the case and is usually associated with a substantial federal question, a conflict among lower courts, or another reason making Supreme Court review important. Denial is the ordinary result for a pending cert petition.

## Snapshot Facts Used

The point-in-time snapshot is `data/cases/scotus/1034900/record/snapshots/2026-07-04.json`. It identifies the case as `Minor v. Tillotson` in SCOTUS, but it contains no docket number, no docket entries, no originating-court information, no filing date, and no cert-granted or cert-denied date. The only concrete signal beyond the case name is a linked CourtListener opinion cluster.

That shape matters. A live modern cert petition normally would not already have a linked published opinion cluster. The repo's scope notes treat sparse historical SCOTUS cases with linked published opinions and no machine-readable cert disposition as a mismatch for the modern discretionary-cert event model: the later label is more likely a merits or historical disposition than a true cert grant/deny label.

## Calibration

I used local corpus tools only for context. The SCOTUS resolved base-rate slice returned 296 resolved rows with dispositions dominated by `other` (about 78%), with `granted` at about 1.4%. The retrieved SCOTUS priors were also mostly historical or merits-oriented rows rather than clean modern cert petitions, so I treated them as weak calibration rather than close analogues.

## Prediction

I predict `other`, with `granted = 0` and `P(granted) = 0.04`.

The linked cluster makes a pure pending-cert denial model less apt, but it does not supply a machine-readable cert grant. Given the absence of entries, cert dates, docket number, lower-court link, or conflict/importance facts, the safest disposition label is `other`, reflecting the likely scope mismatch or historical merits character rather than a modern cert grant. I do not provide per-Justice votes because the snapshot contains no vote-specific or merits-conference information.
