# Forecast of the Court's Decision: *Salazar v. Paramount Global, dba 247Sports* (No. 25-459)

## I. Predicted Judgment and Vote Split

The judgment of the United States Court of Appeals for the Sixth Circuit is **vacated**, and the case is remanded for further proceedings, by a **7–2** vote.

- **Majority (7)**: Justice Kagan (author), joined by Chief Justice Roberts and Justices Sotomayor, Gorsuch, Kavanaugh, Barrett, and Jackson.
- **Concurrence**: Justice Kavanaugh files a concurring opinion (potentially joined by Justice Barrett or Chief Justice Roberts) emphasizing the narrow scope of the question decided and the threshold statutory defenses remaining open on remand.
- **Dissent (2)**: Justice Alito files a dissenting opinion, joined by Justice Thomas.

---

## II. Predicted Majority Reasoning

### 1. Textual Analysis of 18 U.S.C. § 2710(a)(1)
The Court begins with the text of the Video Privacy Protection Act's definition of "consumer": *"any renter, purchaser, or subscriber of goods or services from a video tape service provider."* 18 U.S.C. § 2710(a)(1). Because the VPPA does not define the terms "goods" or "services," the Court gives them their ordinary meaning at the time of enactment in 1988. In ordinary parlance, the unmodified phrase "goods or services" encompasses all commercial wares, merchandise, and intangible offerings provided by a business—not solely audiovisual offerings.

### 2. Meaningful Variation Across Adjoining Definitions in § 2710(a)
The Court places decisive weight on the structure of § 2710(a), where Congress defined three terms in a single statutory sentence using materially different modifiers for the subject matter of each:
- In **§ 2710(a)(4)**, Congress defined *"video tape service provider"* by reference to the rental, sale, or delivery of **"prerecorded video cassette tapes or similar audio visual materials."**
- In **§ 2710(a)(3)**, Congress defined *"personally identifiable information"* by reference to information identifying a person as having requested or obtained **"specific video materials or services"** from a video tape service provider.
- In **§ 2710(a)(1)**, by contrast, Congress defined *"consumer"* as *"any renter, purchaser, or subscriber of **goods or services** from a video tape service provider"*—omitting any "video" or "audio visual" modifier.

Invoking the meaningful-variation canon (*Russello v. United States*, 464 U.S. 16 (1983); *Pulsifer v. United States*, 601 U.S. 124 (2024)), the Court holds that when Congress wanted to limit a statutory term in § 2710(a) to video or audiovisual offerings, it did so expressly. Reading an implicit "audiovisual" limitation into "goods or services" in § 2710(a)(1) would erase that deliberate variation and render the modifier "video" in § 2710(a)(3)'s parallel phrase (*"specific video materials or services from a video tape service provider"*) largely superfluous.

### 3. Rejection of the "From a Video Tape Service Provider" Relational Limitation
The Court rejects Paramount's and the Sixth and D.C. Circuits' argument that the prepositional phrase *"from a video tape service provider"* restricts the *type* of "goods or services" to those provided in the entity's capacity as a video provider.
- First, as a matter of ordinary grammar, the preposition "from" identifies the *source* of the goods or services, not their nature. Indeed, § 2710(a)(3) uses the identical trailing phrase *"from a video tape service provider"* yet still specifies *"video materials or services"* before it.
- Second, Congress understood that a "video tape service provider" under § 2710(a)(4)—such as a department store, general retailer, or media company—need not deal exclusively in audiovisual materials and may sell or offer non-video goods or services alongside audiovisual materials.
- Third, the consistent-usage canon reinforces this reading: in the VPPA's marketing exception, 18 U.S.C. § 2710(b)(2)(D)(ii), Congress permitted limited disclosures solely for the purpose of *"marketing goods and services directly to the consumer,"* where "goods and services" indisputably extends beyond audiovisual products.

### 4. Statutory Structure: Separation of "Consumer" Status and "Personally Identifiable Information"
The Court also rejects Respondent's structural argument that the transaction making someone a "consumer" under § 2710(a)(1) must be the same transaction that generates "personally identifiable information" under § 2710(a)(3).
- Under § 2710(b)(1), civil liability attaches only when a video tape service provider knowingly discloses *"personally identifiable information"* (which must always identify specific video materials or services requested or obtained) *"concerning any consumer of such provider."*
- Other subsections of the VPPA—namely § 2710(d) (evidentiary exclusion) and § 2710(e) (record destruction)—protect "personally identifiable information" without any reference to a "consumer." Thus, the statute itself contemplates that "personally identifiable information" and "consumer" status are independent concepts with distinct functions: § 2710(a)(3) defines *what* information is protected (specific video-viewing history, never bandana or newsletter records), while § 2710(a)(1) and § 2710(b)(1) limit *who* may bring a private damages action for unauthorized disclosure to individuals who have a rental, purchase, or subscription relationship with the provider, and from whom the provider has an established channel to obtain advance informed consent under § 2710(b)(2)(B).

### 5. Scope of the Holding and Remand Instructions
The Court vacates the Sixth Circuit's judgment rather than reversing outright, emphasizing that the lower courts assumed without deciding several contested elements of Salazar's claim that were not encompassed within the question presented. Specifically, the Court leaves open for remand:
1. Whether Paramount (dba 247Sports.com) is *"engaged in the business . . . of rental, sale, or delivery of prerecorded video cassette tapes or similar audio visual materials"* so as to qualify as a *"video tape service provider"* under § 2710(a)(4);
2. Whether the automated transmission of a Facebook ID (`c_user` cookie) and webpage URL via the Meta Pixel constitutes the knowing disclosure of *"personally identifiable information"* under § 2710(a)(3);
3. Whether signing up for a free email newsletter makes Salazar a *"subscriber"* of "goods or services" under § 2710(a)(1); and
4. Any threshold questions of Article III standing.

---

## III. Predicted Concurring and Dissenting Opinions

### Concurring Opinion (Justice Kavanaugh)
Justice Kavanaugh concurs in full in the Court's textual analysis of § 2710(a)(1), explaining that the Court must follow the statutory text as written rather than rewriting the definition of "consumer" to address policy concerns about modern Internet advertising and pixel litigation. He writes separately to underscore that the VPPA contains other critical textual limits that were not before the Court today and that lower courts have frequently found dispositive:
1. **The "Video Tape Service Provider" Requirement (§ 2710(a)(4))**: Not every business or retailer that posts short promotional or informational video clips on its website is *"engaged in the business . . . of rental, sale, or delivery of prerecorded video cassette tapes or similar audio visual materials."*
2. **The "Personally Identifiable Information" Requirement (§ 2710(a)(3))**: Whether automated browser code transmitted for targeted advertising constitutes "personally identifiable information" is the subject of a separate circuit split (where the majority of circuits apply an "ordinary person" standard) and remains open on remand.

### Dissenting Opinion (Justice Alito, joined by Justice Thomas)
Justice Alito dissents, arguing that the majority reads the words "goods or services" with wooden literalism divorced from statutory context and common sense (*Dubin v. United States*, 599 U.S. 110 (2023); *Facebook, Inc. v. Duguid*, 592 U.S. 395 (2021)).
- Reading all 15 words of § 2710(a)(1) together with § 2710(a)(4), the triad of nouns (*"renter, purchaser, or subscriber"*) directly mirrors the triad of actions that define a *"video tape service provider"* (*"rental, sale, or delivery of prerecorded video cassette tapes or similar audio visual materials"*). In ordinary English, a consumer of "goods or services from a video tape service provider" refers to a customer of the video-related offerings that make the entity a video tape service provider, just as a consumer of "goods or services from a medical provider" refers to a patient receiving medical care rather than someone buying a cup of coffee in the hospital cafeteria.
- The dissent warns that untethering consumer status from video transactions transforms a tailored 1988 video-rental privacy statute—enacted in the wake of the Robert Bork video-store incident—into an arbitrary and punitive regime governing modern website analytics, exposing businesses across the economy to hundreds of millions of dollars in statutory damages ($2,500 per class member) based on the happenstance of whether a website visitor once signed up for a free email newsletter or bought an unrelated product years earlier.
