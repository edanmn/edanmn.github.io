---
title: The data
---

# The data

Everything below is public information that was hard to get. Some of it sits behind a bot wall,
some of it is one PDF per school district, some of it exists only inside a report's appendix,
and some of it was deleted from the internet and had to be pulled back out of an archive. We
put it in one place so you do not have to repeat the work.

Every file is free to download and use. If you find an error, write to edanmnorg@gmail.com and
we will fix it and say that we did.

!!! note "How to read these files"
    Every file is a plain CSV. Suppressed cells are marked as suppressed and are never
    estimated. Where a source hides small counts, we keep them hidden. Methods and the scripts
    that build each file are named in each row below.

## Schools and seizure plans

| File | What it is | Source we assembled it from |
|---|---|---|
| [audit_full.csv](files/audit_full.csv) | Every Minnesota public school district, whether a seizure plan is publicly findable online, with district type, county and enrollment | Our own review of 329 district websites, June 2026 |
| [district_confirmations.csv](files/district_confirmations.csv) | Districts that told us directly whether plans and trained staff are in place, and what they said | Our outreach, July to September 2026 |
| [mn_district_risk_composite.csv](files/mn_district_risk_composite.csv) | The audit joined to school nurse staffing, ambulance response times and county health measures | Ours, plus NCES, MN Office of Emergency Medical Services, CDC PLACES |
| [mn_nurse_risk_analysis.csv](files/mn_nurse_risk_analysis.csv) | Estimated school nurse coverage by district | NCES staffing data joined to MDH's 2022 workforce report |
| [mn_district_ohd.csv](files/mn_district_ohd.csv) | Students served under Other Health Disabilities, by district, December 2025 | 329 separate MDE child count PDFs, one per district |
| [mn_noplan_districts_by_ohd.csv](files/mn_noplan_districts_by_ohd.csv) | Districts with no posted plan, ranked by that count | Derived from the two files above |
| [mn_district_language.csv](files/mn_district_language.csv) | English learner counts by district, for translation priority | Federal education data |
| [mn_ems_response_times_2023.csv](files/mn_ems_response_times_2023.csv) | Ambulance response times by county | MN OEMS 2023 report tables |

## Distance to care

| File | What it is | Source |
|---|---|---|
| [mn_district_care_access.csv](files/mn_district_care_access.csv) | Distance from every school district to the nearest neurologist, child neurologist and epilepsy center | Federal provider registry, geocoded by us |
| [mn_epilepsy_providers.csv](files/mn_epilepsy_providers.csv) | Neurology, child neurology and epilepsy providers in Minnesota and border areas | Same |
| [mn_pharmacies_npi.csv](files/mn_pharmacies_npi.csv) | Retail pharmacies used for the distance layer | Same. The state's own licence list sits behind a bot wall, so this is a proxy |

## Medication cost and supply

| File | What it is | Source |
|---|---|---|
| [mn_apcd_rx_asm.csv](files/mn_apcd_rx_asm.csv) | What Minnesotans actually pay per fill for seizure medicines, by payer, 2020 to 2022 | Minnesota All Payer Claims Database public files |
| [mn_medicaid_asm_by_year.csv](files/mn_medicaid_asm_by_year.csv) | Minnesota Medicaid seizure prescriptions and spending by drug and year | CMS State Drug Utilization Data |
| [mn_medicaid_asm_by_quarter.csv](files/mn_medicaid_asm_by_quarter.csv) | The same by quarter, for spotting drops | Same |
| [mn_brandonly_asm.csv](files/mn_brandonly_asm.csv) | Which seizure medicines have no generic, with the evidence for each | FDA Orange Book, checked drug by drug |
| [nadac_asm_quarterly.csv](files/nadac_asm_quarterly.csv) | What pharmacies pay for each seizure medicine, quarter by quarter since 2019 | CMS national acquisition cost files |
| [nadac_asm_30day_cost.csv](files/nadac_asm_30day_cost.csv) | Cost of a 30 day supply at a standard adult dose, brand against generic | Same, with doses from FDA labels |
| [nadac_asm_changes.csv](files/nadac_asm_changes.csv) | Price changes and sudden jumps by molecule | Same |
| [mn_rx_price_transparency_asm.csv](files/mn_rx_price_transparency_asm.csv) | Every price increase on a seizure drug reported to Minnesota since 2022, with the reason given | MDH drug price transparency filings |
| [mn_plan_cost_sharing.csv](files/mn_plan_cost_sharing.csv) | What ten real Minnesota insurance plans charge for five seizure medicines, in January and mid year | Carrier formularies and benefit summaries, read by hand |
| [fda_asm_shortages.csv](files/fda_asm_shortages.csv) | FDA shortage records for seizure medicines | openFDA |
| [mn_asm_shortage_crosscheck.csv](files/mn_asm_shortage_crosscheck.csv) | Every large drop in Minnesota prescriptions, checked against shortage records | Ours |
| [shortage_archive_2024.zip](files/shortage_archive_2024.zip) | Archived FDA and ASHP shortage lists from 2024, five FDA exports and eight ASHP snapshots | Internet Archive. The live FDA database keeps only current shortages, so this is the only way to answer questions about a past year |

## Deaths

Counts under 10 are suppressed by the CDC and stay suppressed here. We do not publish
combinations that would let a suppressed number be worked out by subtraction.

| File | What it is | Source |
|---|---|---|
| [mn_epilepsy_mortality_mcd_epilepsy_by_year.csv](files/mn_epilepsy_mortality_mcd_epilepsy_by_year.csv) | Minnesota deaths mentioning epilepsy, by year, 2018 to 2024 | CDC WONDER |
| [mn_epilepsy_mortality_mcd_any_by_year.csv](files/mn_epilepsy_mortality_mcd_any_by_year.csv) | Deaths mentioning epilepsy or seizures, by year | Same |
| [mn_epilepsy_mortality_mcd_epilepsy_by_age10.csv](files/mn_epilepsy_mortality_mcd_epilepsy_by_age10.csv) | The same by age group | Same |
| [mn_epilepsy_mortality_mcd_epilepsy_by_county.csv](files/mn_epilepsy_mortality_mcd_epilepsy_by_county.csv) | By county, with 57 counties suppressed as under 10 | Same |
| [mn_epilepsy_mortality_ucd_epilepsy_by_year.csv](files/mn_epilepsy_mortality_ucd_epilepsy_by_year.csv) | Deaths where epilepsy was the underlying cause | Same |
| [mn_epilepsy_mortality_place_of_death.csv](files/mn_epilepsy_mortality_place_of_death.csv) | Where these deaths happened, including at home | Same |
| [epilepsy_mortality_neighbor_states.csv](files/epilepsy_mortality_neighbor_states.csv) | Minnesota's rate against Iowa, Wisconsin, the Dakotas and the US | Same |

## Context files

| File | What it is |
|---|---|
| [mn_district_roster.csv](files/mn_district_roster.csv) | Every Minnesota district with county, city, enrollment and phone |
| [cdc_places_mn_county_health.csv](files/cdc_places_mn_county_health.csv) | County health measures used in the risk layers |

## What we could not get

Being honest about the walls is part of the point.

- The Minnesota Board of Pharmacy licence list sits behind a bot check, and licensee lists are
  sold rather than published. We have a formal request in. Until then our pharmacy distances
  come from the federal provider registry, which keeps some closed stores.
- Medical Assistance claims for seizure detection devices, covered since January 2024, are not
  published anywhere. We have a request with the Department of Human Services.
- School nurse staffing by district exists inside state reporting but is not published. Request
  filed with the Department of Health, acknowledged, still pending.
- The claims database that shows what commercially insured Minnesotans pay stops at 2022 in its
  public files, and covers roughly 40 percent of that market. We have asked MDH for the newer
  tabulation they prepared for the state's own mandate evaluation.
- No public source counts people with epilepsy by Minnesota county. Every county-level figure
  anywhere, including ours, is a rate applied to a population.

## Using this data

Take it. Use it in your own work, your reporting, your testimony or your school board meeting.
A credit to the Epilepsy Data & Advocacy Network and a link back is appreciated and not
required. If you publish something built on it, we would like to know, because that is the
entire point.

The code that builds every file is in our public repository, and the method notes for each
dataset live alongside it.
