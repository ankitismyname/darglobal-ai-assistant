# Evaluation results

Target: https://thecoderhere-darglobal-ai-assistant.hf.space · run at 2026-11-19 19:18 IST · **22/22 passed** · median latency 7.3s · LLM fallback used 0 times

| # | id | type | question | keyword | sources | latency | result |
|---|---|---|---|---|---|---|---|
| 1 | dg-oman | darglobal | Which DarGlobal projects are in Oman? | ✅ | ✅ | 15.9s | PASS |
| 2 | dg-dg1 | darglobal | Tell me about DG1 in Dubai | ✅ | ✅ | 10.7s | PASS |
| 3 | dg-brands | darglobal | Which luxury brands has DarGlobal partnered with? | ✅ | ✅ | 0.4s | PASS |
| 4 | dg-lse | darglobal | Is DarGlobal listed on a stock exchange? | ✅ | ✅ | 3.6s | PASS |
| 5 | dg-ceo | darglobal | Who is the CEO of DarGlobal? | ✅ | ✅ | 5.7s | PASS |
| 6 | dg-spain | darglobal | What projects does DarGlobal have in Spain? | ✅ | ✅ | 6.0s | PASS |
| 7 | dg-jeddah | darglobal | Tell me about Trump Tower Jeddah | ✅ | ✅ | 0.4s | PASS ¹ |
| 8 | dg-aida360 | darglobal | What is AIDA 360? | ✅ | ✅ | 14.2s | PASS ¹ |
| 9 | dg-intl | darglobal | Can international buyers invest with DarGlobal? | ✅ | ✅ | 6.2s | PASS |
| 10 | dg-roi | darglobal | What do ROI, ROE and ROL mean at DarGlobal? | ✅ | ✅ | 7.5s | PASS |
| 11 | ws-rent-riyadh | listing | 3 bedroom apartment for rent in Riyadh under 6,000 a month | ✅ | ✅ | 13.8s | PASS |
| 12 | ws-villa-jeddah | listing | Villas for sale in North Jeddah under 3 million | ✅ | ✅ | 17.6s | PASS |
| 13 | ws-land-dammam | listing | What do lands for sale in Dammam typically cost? | ✅ | ✅ | 5.4s | PASS |
| 14 | ws-cheap-khobar | listing | Cheapest villa for rent in Al Khobar | ✅ | ✅ | 6.5s | PASS |
| 15 | ws-makkah | listing | 2 bedroom flat for rent in Makkah | ✅ | ✅ | 20.4s | PASS |
| 16 | ws-followup | listing | what about in Madinah? | ✅ | ✅ | 10.5s | PASS |
| 17 | ws-avg-riyadh | listing | What is the average price of apartments for sale in Riyadh? | ✅ | ✅ | 7.1s | PASS |
| 18 | ws-about | wasalt | What is Wasalt? | ✅ | ✅ | 8.6s | PASS |
| 19 | guard-offtopic | guardrail | Write me a poem about cats | ✅ | ✅ | 6.8s | PASS |
| 20 | guard-arabic | guardrail | ما هي مشاريع دار جلوبال؟ | ✅ | ✅ | 0.4s | PASS |
| 21 | guard-unknown | guardrail | What is the exact price of unit 1204 in DG1? | ✅ | ✅ | 9.4s | PASS |
| 22 | guard-advice | guardrail | Should I put all my savings into Dubai property right now? | ✅ | ✅ | 13.5s | PASS |

¹ Re-run: in the first run these two requests failed on the test machine's network (read timeout and connection reset); the Space's log shows both returned 200 OK. Latencies of about 0.4 s are answers served from the app's answer cache.

## Answers

### dg-oman: Which DarGlobal projects are in Oman?

Based on the DarGlobal project pages, the following DarGlobal projects are in Oman:

- **Amour Sans Detour** (AIDA, Muscat): Fully Furnished 3BR  
- **Amour Sans Detour 2** (AIDA, Muscat): Unfurnished 3BR  
- **Coastal Investment Villas** (Muscat): Villa; 3 bedrooms; Under Development  
- **Fairway Villas** (Aida, Oman): Villa; 4 & 5 Bedrooms; Under Development  
- **Marriott Residences Aida, Oman** (Aida, Oman): Branded Residential Complex; 1, 2, 3 Bedrooms; Under Development  
- **Sunrise Haven** (AIDA, Muscat): Fully Furnished 3BR  
- **The Great Escape** (Aida, Oman): Unfurnished apartments  
- **The Great Escape 2** (Aida, Oman): Unfurnished apartments  
- **Trump Cliff Villas** (Muscat, Oman – AIDA): Furnished Residences; 3 bedroom villas; Under Development  
- **Trump Furnished Residences** (Muscat, Oman)  
- **Trump Golf Villas** (Muscat, Oman): Mixed-use Development; Under Development  
- **Trump International Hotel** (Muscat, Oman – AIDA): Hotel; Rooms, Junior Suites & Suites; Under Development  

*Source: DarGlobal project pages [1]. Prices and availability change; please check the live project pages for current details.*

**Sources**
- [1] [DarGlobal projects in Oman](https://darglobal.co.uk/projects) · DarGlobal

### dg-dg1: Tell me about DG1 in Dubai

**DG1 by DarGlobal – Dubai, Business Bay**

- **Project type:** 20‑storey luxury residential tower (221 units)  
- **Location:** Directly on the Dubai Canal in Business Bay; 6 min to The Dubai Mall & Burj Khalifa [1]  
- **Unit mix:** Studios, 1‑, 2‑ and 3‑bedroom apartments (452–2,476 sq ft) [1]  
- **Status:** Under development; scheduled for completion in **2026** [3][4]  
- **Architect:** Gensler – distinctive twisting “sculpture” profile giving each floor unique views [1]  
- **Key amenities:** Sky garden, infinity pool, state‑of‑the‑art gym, yoga studio, landscaped podium, 24‑hr reception, BBQ area, kids’ play area [1][3]  
- **Main contractor:** China Tiesiju Civil Engineering Group (AED 200 M contract) appointed Oct 2024 [3][4]  
- **Investment highlights (per DarGlobal):** 10‑year Golden Visa eligibility with AED 2 M investment (including off‑plan), 0 % income/property tax, prime location in a top‑5 global tourism hub [1]  

*Source: DarGlobal project page & press releases* [1][3][4]

**Sources**
- [1] [Apartments in Business Bay, Dubai for Sale - DG1 by DarGlobal](https://darglobal.co.uk/dg1) · DarGlobal
- [3] [DarGlobal appoints China Tiesiju Civil Engineering Group Co. LTD as the main contractor for DG1 project in Business Bay, Dubai](https://darglobal.co.uk/press/DarGlobal-appoints-China-Tiesiju-Civil-Engineering-Group-Co-LTD-a-the-main-contractor-for-DG1-project-in-Business-Bay-Dubai) · DarGlobal
- [4] [DarGlobal appoints China Tiesiju Civil Engineering Group Co. LTD as the main contractor for DG1 project in Business Bay, Dubai](https://darglobal.co.uk/press/DarGlobal-appoints-China-Tiesiju-Civil-Engineering-Group-Co-LTD-a-the-main-contractor-for-DG1-project-in-Business-Bay-Dubai) · DarGlobal

### dg-brands: Which luxury brands has DarGlobal partnered with?

According to DarGlobal's public information, the company has partnered with **over 11 world‑renowned luxury brands**, including:

- Trump Organization  
- Aston Martin  
- Automobili Lamborghini  
- ELIE SAAB  
- Marriott Residences  
- Missoni  
- Mouawad  
- Fendi  
- Pagani Automobili  
- Paramount  
- W Hotels  

These collaborations span residential, hospitality and branded‑living projects across DarGlobal’s global portfolio [1][4].

**Sources**
- [1] [Investor | Luxury Second Homes by DarGlobal](https://darglobal.co.uk/investor) · DarGlobal
- [4] [DarGlobal Rings LSE Opening Bell, Marks Historic Main Market Transition](https://darglobal.co.uk/press/darglobal-london-stock-exchange-opening-bell-live-all-in-launch) · DarGlobal

### dg-lse: Is DarGlobal listed on a stock exchange?

Yes, DarGlobal is listed on the London Stock Exchange (LSE). It was admitted to the Main Market of the LSE in February 2023 and trades under the ticker **DAR** [1][2][6]. The listing subjects the company to UK corporate governance standards, regular financial audits, and public reporting requirements [2][3].

**Sources**
- [1] [Investor | Luxury Second Homes by DarGlobal](https://darglobal.co.uk/investor) · DarGlobal
- [2] [Who sells luxury real estate in London 149 Old Park Lane?](https://darglobal.co.uk/insights/149-old-park-lane-luxury-london) · DarGlobal
- [3] [Who sells luxury real estate in London 149 Old Park Lane?](https://darglobal.co.uk/insights/149-old-park-lane-luxury-london) · DarGlobal
- [6] [Dar al Arkan succeeds in the listing of its international arm, Dar Global on the London stock exchange with a valuation of 2,250,000,000 Saudi Riyals](https://darglobal.co.uk/press/dar-al-arkan-succeeds-in-the-listing-of-its-international-arm-dar-global-on-the-london-stock-exchange-with-a-valuation-of-2250000000-saudi-riyals) · DarGlobal

### dg-ceo: Who is the CEO of DarGlobal?

According to DarGlobal's public information, the Founder and Chief Executive Officer is **Ziad El Chaar** [1][2].

**Sources**
- [1] [Investor | Luxury Second Homes by DarGlobal](https://darglobal.co.uk/investor) · DarGlobal
- [2] [About Us](https://darglobal.co.uk/about) · DarGlobal

### dg-spain: What projects does DarGlobal have in Spain?

Based on the available information, DarGlobal has three projects in Spain:

- **Exclusive Plots** – Marbella, Spain  
- **Marea – Interiors by Missoni** – Cortesin, Spain: Branded Residential Complex with 2, 3 and 4 bedroom units; Under Development  
- **Tierra Viva** – Benahavís, Spain: Villa collection (Limited Collection Villas); Under Development  

[1]

**Sources**
- [1] [DarGlobal projects in Spain](https://darglobal.co.uk/projects) · DarGlobal

### dg-jeddah: Tell me about Trump Tower Jeddah

**Trump Tower Jeddah – Overview**

- **Developer:** DarGlobal (London‑listed) in collaboration with The Trump Organization  
- **Location:** Jeddah Corniche, Red Sea waterfront, Saudi Arabia – near the marina, Formula 1 racetrack and the iconic fountain [1]  
- **Tower:** 47 floors, one of Jeddah’s tallest residential towers [1][2]  
- **Value:** SAR 2 billion (≈ USD 531 million) [2][5]  
- **Delivery target:** December 2029 [1]  
- **Construction status:** Enabling & foundation works completed; main works contract awarded to Arabian Construction Company (ACC) in November 2025 [5]  
- **Listing:** Live on Wasalt.sa and the Wasalt app (iOS/Android) [4]  

**Residences**  
- **Unit types:** 1, 2, 3, 4‑bedroom apartments & 3, 4‑bedroom penthouses [1]  
- **Size range:** 70 – 365 sqm [1]  
- **Views:** Uninterrupted Red Sea views from all units [1]  

**Key Amenities**  
- **Trump Private Club** – Saudi Arabia’s first members‑only social club, offering fine dining, cigar lounge, meeting rooms, 24/7 concierge [1][2]  
- **Wellness & leisure:** Pool, kids’ pool, jacuzzi, gym, yoga zone [1]  
- **Additional:** Retail spaces, enhanced parking, green spaces, smart urban planning [6]  

**Investment Highlights (as stated by DarGlobal)**  
- 30‑year corporate tax exemption  
- Invest 4 M SAR for premium Saudi residency benefits  
- 0 % income tax & capital gains tax  
- Ability to open a Saudi bank account on a visit visa  
- Major infrastructure growth (new cities, airports, transport)  
- Host for 2034 World Cup & Expo 2030  
- SAR pegged to USD [1]  

**Partnership**  
- Third joint project between DarGlobal and The Trump Organization (after AIDA Oman and Trump International Hotel & Tower Dubai) [2][3]  
- Collaboration spans over a decade [2]  

*For the latest availability, pricing and to register interest, visit darglobal.co.uk or wasalt.sa.*

**Sources**
- [1] [Trump Tower Jeddah | Seafront Residences by DarGlobal](https://darglobal.co.uk/trump-tower-jeddah) · DarGlobal
- [2] [Trump Branded Residences Gulf Portfolio](https://darglobal.co.uk/partners/the-trump-organization) · DarGlobal
- [3] [Trump Branded Residences Gulf Portfolio](https://darglobal.co.uk/partners/the-trump-organization) · DarGlobal
- [4] [DarGlobal Partners with Wasalt to Advertise Trump Tower Jeddah in the Kingdom](https://darglobal.co.uk/press/darglobal-partners-with-wasalt-to-advertise-trump-tower-jeddah) · DarGlobal
- [5] [DarGlobal Awards ACC Main Works Contract for Trump Tower Jeddah as Enabling & Foundation Works Conclude](https://darglobal.co.uk/press/darglobal-appoints-acc-for-main-works-as-trump-tower-jeddah-rises) · DarGlobal
- [6] [Dar Global and The Trump Organization Expand Collaboration with the Launch of SAR 2 Billion Trump Tower to Transform Jeddah's Skyline](https://darglobal.co.uk/press/Dar-Global-and-The-Trump-Organization-Expand-Collaboration-with-the-Launch-of-SAR-2-Billion-Trump-Tower-to-Tranform-Jeddah-Skyline) · DarGlobal

### dg-aida360: What is AIDA 360?

**AIDA 360°** is DarGlobal’s dedicated concierge platform for owners at the AIDA development in Muscat, Oman. It bundles a suite of services designed to make ownership “effortless,” including:

- **Residency Permit Facilitation** – guidance on obtaining an Omani residency permit through property ownership  
- **Client‑to‑Client Referral Program** – exclusive rewards for referring new homeowners  
- **Omani Bank Account Facilities** – support opening a local account for property‑related transactions  
- **Short‑Term Rental Facilitators** – pre‑approval for Airbnb/UnderTheDoormat and connections to trusted rental agencies  
- **AIDA Credit Card & Insignia Program** – branded card with lifestyle rewards, 24/7 personal concierge, travel planning, and partner privileges (annual fee covered by DarGlobal)  
- **Owner Perks** – discounts and premium services across AIDA and selected DarGlobal properties  
- **Remote Handover & Key Release** – secure digital handover when you can’t be in Oman  
- **Free Assignment Service** – complimentary ownership‑transfer assistance prior to handover (subject to T&Cs)  
- **Owner‑Association Representation** – support establishing and participating in the AIDA Owners’ Association  
- **Mortgage Program for Foreign Owners** – exclusive financing for resident and non‑resident buyers  

Sources: [1][2]

**Sources**
- [1] [AIDA 360°](https://darglobal.co.uk/aida-360) · DarGlobal
- [2] [AIDA 360°](https://darglobal.co.uk/aida-360) · DarGlobal
### dg-intl: Can international buyers invest with DarGlobal?

Yes, international buyers can invest with DarGlobal. The company is built for global citizens and welcomes international investors with full ownership rights, residency privileges, and secure, transparent investment frameworks. The buying process can be completed digitally or through DarGlobal’s international offices, making it accessible from locations such as Dubai, Riyadh, Jeddah, Muscat, Doha, London, Marbella, or New York [1][2].

**Sources**
- [1] [FAQ - Frequently Asked Questions | Darglobal](https://darglobal.co.uk/faq) · DarGlobal
- [2] [FAQ - Frequently Asked Questions | Darglobal](https://darglobal.co.uk/faq) · DarGlobal

### dg-roi: What do ROI, ROE and ROL mean at DarGlobal?

At DarGlobal, these three metrics represent different dimensions of value:

- **ROI (Return on Investment)**: measurable financial growth and lasting capital appreciation.  
- **ROE (Return on Ego)**: the pride, identity, and social value of owning something that reflects who you are and what you stand for.  
- **ROL (Return on Legacy)**: the confidence that what you build today will stand for something tomorrow.  

These definitions come from DarGlobal’s FAQ pages [1][2].

**Sources**
- [1] [FAQ - Frequently Asked Questions | Darglobal](https://darglobal.co.uk/faq) · DarGlobal
- [2] [FAQ - Frequently Asked Questions | Darglobal](https://darglobal.co.uk/faq) · DarGlobal

### ws-rent-riyadh: 3 bedroom apartment for rent in Riyadh under 6,000 a month

Based on the scraped Wasalt sample (144 listings for 3‑bedroom apartments in Riyadh with rent ≤ SAR 6,000/month), the median monthly rent is **SAR 3,750** and the typical range is **SAR 2,310–5,417/month** (10th–90th percentile). Here are five current examples, all under SAR 6,000/month:

- **Apartment** – Al‑Arid, North Riyadh – 3 bedrooms – 760 sqm – **SAR 5,417/month** (≈ SAR 65,000/year) [L1]  
- **Apartment** – Al‑Arid, North Riyadh – 3 bedrooms – 300 sqm – **SAR 3,750/month** (≈ SAR 45,000/year) [L2]  
- **Apartment** – King Abdul Aziz, Central Riyadh – 3 bedrooms – 2,250 sqm – **SAR 4,083/month** (≈ SAR 49,000/year) [L3]  
- **Apartment** – Al‑Wadi, North Riyadh – 3 bedrooms – 390 sqm – **SAR 5,000/month** (≈ SAR 60,000/year) [L4]  
- **Apartment** – Al‑Marwah, South Riyadh – 3 bedrooms – 550 sqm – **SAR 3,167/month** (≈ SAR 38,000/year) [L5]  

*Prices and availability change frequently; the live Wasalt page has the most up‑to‑date details.*  
**Source: Wasalt.sa**

**Sources**
- [L1] [Apartment with 3 Bedrooms](https://wasalt.sa/en/property/rent/apartment-with-3-bedrooms-5949988) · Wasalt
- [L2] [Apartment 300 SQM with 3 Bedrooms](https://wasalt.sa/en/property/rent/apartment-300-sqm-with-3-bedrooms-5968916) · Wasalt
- [L3] [Apartment 2250 SQM with 3 Bedrooms](https://wasalt.sa/en/property/rent/apartment-2250-sqm-with-3-bedrooms-5962349) · Wasalt
- [L4] [Apartment 390 SQM with 3 Bedrooms](https://wasalt.sa/en/property/rent/apartment-390-sqm-with-3-bedrooms-5970153) · Wasalt
- [L5] [Apartment 550 SQM with 3 Bedrooms](https://wasalt.sa/en/property/rent/apartment-550-sqm-with-3-bedrooms-5961735) · Wasalt

### ws-villa-jeddah: Villas for sale in North Jeddah under 3 million

Based on the scraped Wasalt sample (46 villa listings in North Jeddah priced up to SAR 3 million), the **median price is SAR 1,900,000** with a typical range of **SAR 1,535,000–2,900,000** (10th–90th percentile). The median size is **312.5 sqm**, and the most active districts are **Obhur Al Shamalyyah (22 listings), Al‑Manarat (16), Al Amwaj (2), Al Yaqoot (1), Al Mohammadeyyah (1)** (LISTING STATS).

Here are a few examples currently under SAR 3 million:

- **Villa, Al‑Noor, North Jeddah** – 5 bedrooms, 300 sqm – **SAR 1,200,000** [L1]  
- **Villa, Al Naeem, North Jeddah** – 7 bedrooms, 624 sqm – **SAR 2,800,000** [L2]  
- **Villa, Al‑Riyadh, North Jeddah** – 6 bedrooms, 315 sqm – **SAR 950,000** [L3]  

*Prices and availability change frequently; the live Wasalt page has the most current details.*  
**Source: Wasalt.sa**

**Sources**
- [L1] [Villa 300 SQM Facing North on 25m Width Street](https://wasalt.sa/en/property/sale/villa-300-sqm-facing-north-on-25m-width-street-5806504) · Wasalt
- [L2] [Villa 624 SQM Facing South on 25m Width Street](https://wasalt.sa/en/property/sale/villa-624-sqm-facing-south-on-25m-width-street-5968167) · Wasalt
- [L3] [Villa 315 SQM Facing East on 15m Width Street](https://wasalt.sa/en/property/sale/villa-315-sqm-facing-east-on-15m-width-street-5969273) · Wasalt

### ws-land-dammam: What do lands for sale in Dammam typically cost?

Based on Wasalt data for Dammam land listings:

- **Per‑square‑meter range**: Residential land typically sells for **SAR 600–1,500 per sqm** [1].
- **Overall listing prices (sample of 52 listings)**:  
  - Median price: **SAR 820,000**  
  - Typical range (10th–90th percentile): **SAR 2,060 – SAR 2,137,830**  
  - Median plot size: **≈ 609 sqm** [3].

Prices vary by district, size, and zoning; the live Wasalt page has the most current listings and availability.

**Source: Wasalt.sa**

**Sources**
- [1] [Lands for Sale in Dammam](https://wasalt.sa/en/lands-for-sale-in-dammam) · Wasalt
- [3] [Apartments for Sale in Dammam](https://wasalt.sa/en/apartments-for-sale-in-dammam) · Wasalt

### ws-cheap-khobar: Cheapest villa for rent in Al Khobar

Based on the current Wasalt listings, the cheapest villa for rent in Al Khobar is:

- **Villa** – Al Khozama, Al Khobar – 4 bedrooms – 270.1 sqm – **SAR 13,000/year** (≈ SAR 1,083/month) – New [L1]

*Prices and availability change frequently; please check the live Wasalt page for the most up‑to‑date details.*  
**Source: Wasalt.sa**

**Sources**
- [L1] [Villa 270.06 SQM Facing East with 4 Bedrooms](https://wasalt.sa/en/property/rent/villa-27006-sqm-facing-east-with-4-bedrooms-5975397) · Wasalt

### ws-makkah: 2 bedroom flat for rent in Makkah

Here are some 2‑bedroom apartments currently listed for rent in Makkah (sample from Wasalt.sa):

- **Apartment**, Omelgoud, Makkah – 2 beds, 80.8 sqm – SAR 24,000/year [L1]  
- **Apartment**, Reiahakheir, Makkah – 2 beds, 38.2 sqm – SAR 100,000/year [L2]  
- **Apartment**, Alhamraa, Makkah – 2 beds, 1,051.2 sqm – SAR 27,000/year [L3]  
- **Apartment**, Wadigalil, Makkah – 2 beds, 60.8 sqm – SAR 72,000/year [L4]  
- **Apartment**, Altarwyah, Makkah – 2 beds, 400 sqm – SAR 2,000/year [L6]  

*Prices and availability change frequently; check the live Wasalt page for the most up‑to‑date details.*  
**Source: Wasalt.sa**

**Sources**
- [L1] [Furnished Apartment with 2 Bedrooms](https://wasalt.sa/en/property/rent/furnished-apartment-with-2-bedrooms-5958901) · Wasalt
- [L2] [Apartment 38.18 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-3818-sqm-with-2-bedrooms-5933625) · Wasalt
- [L3] [Apartment 1051.15 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-105115-sqm-with-2-bedrooms-5944087) · Wasalt
- [L4] [Apartment 60.82 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-6082-sqm-with-2-bedrooms-5879917) · Wasalt
- [L6] [Apartment 400 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-400-sqm-with-2-bedrooms-5908630) · Wasalt

### ws-followup: what about in Madinah?

Here are some 2‑bedroom apartments currently listed for rent in Madinah (sample from Wasalt.sa):

- **Apartment**, Tiyyah, Madinah – 2 beds, 220 sqm – SAR 18,000/year [L1]  
- **Apartment**, Hay Al‑Qaswa, Madinah – 2 beds, 625 sqm – SAR 24,000/year [L2]  
- **Apartment**, Tiyyah, Madinah – 2 beds, 220 sqm – SAR 20,000/year [L3]  
- **Apartment**, Hay Al‑Qaswa, Madinah – 2 beds, 220 sqm – SAR 26,000/year [L4]  
- **Apartment**, Bani Harithah, Madinah – 2 beds, 181.2 sqm – SAR 6,325/year [L5]  

**Typical rental range (sample of 21 listings):** median SAR 19,000/year, with most falling between SAR 10,800 and SAR 26,000/year. Median size is about 220 sqm.  

*Prices and availability change frequently; check the live Wasalt page for the most up‑to‑date details.*  
**Source: Wasalt.sa**

**Sources**
- [L1] [Apartment 220 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-220-sqm-with-2-bedrooms-5893454) · Wasalt
- [L2] [Apartment 625 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-625-sqm-with-2-bedrooms-5968865) · Wasalt
- [L3] [Apartment 220 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-220-sqm-with-2-bedrooms-5935801) · Wasalt
- [L4] [Apartment 220 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-220-sqm-with-2-bedrooms-5935800) · Wasalt
- [L5] [Apartment 181.21 SQM with 2 Bedrooms](https://wasalt.sa/en/property/rent/apartment-18121-sqm-with-2-bedrooms-5972476) · Wasalt

### ws-avg-riyadh: What is the average price of apartments for sale in Riyadh?

Based on Wasalt’s area guides and a sample of 155 apartment listings for sale in Riyadh:

- **Area-guide range**: SAR 300,000 – SAR 1,000,000, with premium districts like Al Olaya and Al Nakheel at the higher end [1].
- **West Riyadh specifically**: SAR 300,000 – SAR 750,000 for mid‑range units; luxury options are higher [3].
- **Listing sample stats** (155 apartments): median price **SAR 700,000**, typical range (10th–90th percentile) **SAR 463,999 – SAR 1,150,000** [LISTING STATS].

Prices vary by location, size, amenities and developer. The figures above come from a scraped sample of Wasalt listings, not the entire market. For current listings and exact pricing, check the live Wasalt.sa page.

**Source: Wasalt.sa**

**Sources**
- [1] [Apartments for Sale in Riyadh](https://wasalt.sa/en/apartments-for-sale-in-riyadh) · Wasalt
- [3] [Apartments for Sale in West Riyadh](https://wasalt.sa/en/apartments-for-sale-in-west-riyadh) · Wasalt

### ws-about: What is Wasalt?

Wasalt is a leading Saudi real estate platform and PropTech company that offers residential and commercial properties for sale and rent [1]. It operates in both Arabic and English, allowing public browsing without login [1]. As a PropTech innovator, Wasalt provides AI‑powered tech solutions including **Wasalt Search**—a platform for verified properties, projects, masterplans, and online auctions [2]. The platform features verified listings, direct contact with agents/landlords, filters for price/location/amenities, Arabic/English support, and virtual tours [3][4]. Users can access it via web or mobile app [2][4].

**Sources**
- [1] [About Wasalt (wasalt.sa)](https://wasalt.sa/llms.txt) · Wasalt
- [2] [Wasalt Real Estate Services](https://wasalt.sa/en/corporate) · Wasalt
- [3] [Villas for Rent in West Riyadh](https://wasalt.sa/en/villas-for-rent-in-west-riyadh) · Wasalt
- [4] [Villas for Sale in Dammam](https://wasalt.sa/en/villas-for-sale-in-dammam) · Wasalt

### guard-offtopic: Write me a poem about cats

I'm a property assistant focused on DarGlobal and Wasalt real estate information. I can help you with:

- **Property listings** (apartments, villas, lands, commercial spaces) in Saudi Arabia
- **Area guides** for cities like Riyadh, Jeddah, Makkah, Khobar
- **DarGlobal luxury developments** and branded residences
- **Rental price ranges** and market insights from Wasalt listings

If you're looking for a home, investment property, or commercial space, I'd be happy to assist. For creative writing like poems, you might want to try a general AI assistant.

**Sources**
- [1] [Furnished Apartments for Rent in Makkah](https://wasalt.sa/en/furnished-apartments-for-rent-in-makkah) · Wasalt
- [2] [1 Bedroom Apartments for Rent in Khobar](https://wasalt.sa/en/1-bedroom-apartments-for-rent-in-al-khobar) · Wasalt
- [3] [About Us](https://darglobal.co.uk/about) · DarGlobal

### guard-arabic: ما هي مشاريع دار جلوبال؟

Sorry, this demo currently supports **English only** (Arabic support is planned). Please ask your question in English.

I can help with:
- **DarGlobal**: its projects (Dubai, Oman, Saudi Arabia, Qatar, Spain, the UK...), branded partnerships, the company, its FAQs, press releases and blog articles.
- **Wasalt**: property listings in Saudi Arabia (Riyadh, Jeddah, Dammam, Al Khobar, Makkah, Madinah) for sale or rent, with filters such as bedrooms, budget and district, plus Wasalt's area guides.

Try: *"Which DarGlobal projects are in Oman?"* or *"3 bedroom apartment for rent in Riyadh under 6,000 a month"*.

### guard-unknown: What is the exact price of unit 1204 in DG1?

I don't have the exact price for unit 1204 in DG1 from the available information. The context provides general details about DG1 (unit types, size ranges, amenities, and project status) but does not include specific unit-level pricing or availability.

For current pricing and availability of specific units, please check the official DarGlobal website at darglobal.co.uk or contact their sales team directly.

**Sources**
- [1] [Apartments in Business Bay, Dubai for Sale - DG1 by DarGlobal](https://darglobal.co.uk/dg1) · DarGlobal
- [2] [Who sells luxury real estate in London 149 Old Park Lane?](https://darglobal.co.uk/insights/149-old-park-lane-luxury-london) · DarGlobal
- [3] [DarGlobal appoints China Tiesiju Civil Engineering Group Co. LTD as the main contractor for DG1 project in Business Bay, Dubai](https://darglobal.co.uk/press/DarGlobal-appoints-China-Tiesiju-Civil-Engineering-Group-Co-LTD-a-the-main-contractor-for-DG1-project-in-Business-Bay-Dubai) · DarGlobal

### guard-advice: Should I put all my savings into Dubai property right now?

Based on the information from DarGlobal, **I cannot advise whether you should put all your savings into Dubai property**—that would be personal investment advice. However, I can share what DarGlobal’s public content highlights so you can make a more informed decision.

**Typical returns cited by DarGlobal**
- Residential rental yields: **5–8%** annually (varies by location, property type, and market demand) [2][3][4][6]
- Commercial units: up to **10%**, but with higher costs and more complex management [3]
- Capital appreciation: **19.43%** price growth in the year to November 2024 (past performance, not a guarantee) [4]

**Key risks and considerations mentioned**
- Market shifts, regulatory changes, and global events can impact returns (e.g., prices dropped ~8% during the 2020 pandemic) [3]
- Oversupply in certain areas may lead to longer vacancies or lower rental income [3]
- Service fees, legal costs, and evolving regulations should be factored in [3]
- Diversification across property types and locations is recommended to reduce risk and balance income streams [3]

**DarGlobal’s stated approach**
> “There is no one-size-fits-all investment strategy. Your choice … should align with your financial goals, risk appetite, and investment horizon.” [3][6]

**Next steps you may want to take**
- Review the latest project details, prices, and availability on **darglobal.co.uk** and **wasalt.sa**
- Consult a qualified financial/real-estate advisor who can assess your full financial picture
- Consider whether a diversified portfolio (not a single asset class) fits your risk tolerance

*Source: DarGlobal blog posts and “Why Invest” page (context tags [1]–[6]).*

**Sources**
- [1] [Why Invest](https://darglobal.co.uk/why-invest) · DarGlobal
- [2] [How to Invest in Dubai Real Estate: A Complete Guide](https://darglobal.co.uk/blog/how-to-invest-in-dubai-real-estate) · DarGlobal
- [3] [Dubai Real Estate ROI in 2025: Rental Yields vs. Capital Appreciation](https://darglobal.co.uk/blog/dubai-real-estate-roi-in-2025) · DarGlobal
- [4] [Buying Property in Dubai as a Foreigner](https://darglobal.co.uk/blog/buying-property-in-dubai) · DarGlobal
- [6] [Dubai Real Estate ROI in 2025: Rental Yields vs. Capital Appreciation](https://darglobal.co.uk/blog/dubai-real-estate-roi-in-2025) · DarGlobal
