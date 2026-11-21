---
title: Distance to Care Map
---

# Distance to care

Status: map published September 2026. This is a data page that supports two of our
initiatives: 80 of the districts farthest from a child neurologist also post no findable
seizure plan ([Seizure-Safe Schools](seizure-safe-schools.md)), and the pharmacy distances
feed [Medication access](medication-access.md).

## The gap
Everyone in Minnesota epilepsy care knows the specialists are in Rochester and the Twin
Cities. Nobody had put a number on what that means for a child in Kittson County. Families
far from a center also tend to face the slowest ambulances: in 31 of 87 counties the slowest
tenth of ambulance runs take 20 minutes or more from dispatch to the scene (Minnesota Office
of Emergency Medical Services, 2023).

## What the data shows
We located every neurologist, child neurologist, and epilepsy subspecialist with a practice
address in Minnesota or in parts of the Dakotas, Wisconsin, and Iowa (as far as Milwaukee and Des Moines), using the
federal provider registry, and measured the distance from every school district office.

<iframe src="../../charts/care_access_map.html" class="microsim" width="100%" height="600" title="Map: distance from each school district to the nearest child neurologist" loading="lazy"></iframe>

## Try it: look up your district
<iframe src="../../sims/distance-lookup/main.html" class="microsim" width="100%" height="130" title="Distance to care lookup" loading="lazy"></iframe>

[Open full screen](../sims/distance-lookup/main.html){ .md-button }

| Measure | Value |
|---|---|
| Child neurologists | 72 in Minnesota; 105 counting those we found in Iowa, Wisconsin and the Dakotas |
| Epilepsy subspecialists | 27 in Minnesota; 35 counting those states |
| Districts more than 60 miles from a child neurologist | 101 (about 70,000 students) |
| Districts more than 100 miles away | 11 |
| Of the 101 far districts, those also without a findable seizure plan | 80 |
| Districts more than 60 miles from a Level 4 epilepsy center | 205 (about 220,000 students) |
| Districts more than 100 miles from a Level 4 epilepsy center | 155 (about 150,000 students) |
| Districts more than 15 miles from any retail pharmacy | 15 (14 without a findable plan) |

Kittson, Roseau, Cook, and Big Stone counties are farthest. Distances are straight-line, so
the drive is longer. Minnesota's Level 4 epilepsy centers, the highest
designation, are Mayo Clinic in Rochester, the University of Minnesota Medical Center and
Abbott Northwestern in Minneapolis, and Minnesota Epilepsy Group with Children's Minnesota in
the Twin Cities.

## How much hospital care seizures require

The distance numbers above say how far a family is from a clinic. They say nothing about
how often Minnesotans actually end up in a hospital or emergency department for a seizure.
We pulled that separately from AHRQ's HCUPnet, which draws on hospital discharge records
reported by the Minnesota Hospital Association.

| Minnesota, principal diagnosis of epilepsy or convulsions | 2022 | 2023 | 2024 |
|---|---:|---:|---:|
| Inpatient stays, Minnesota hospitals | 4,042 | 4,338 | 4,618 |
| Emergency department visits (treat-and-release) | 12,247 | 13,007 | 13,524 |
| Minnesota resident inpatient rate per 100,000 | 64.1 | not yet released | not yet released |

Children carried more of this than adults. Minnesotans aged 1 to 17 made up 28.6 percent of
Minnesota's epilepsy inpatient stays in 2023, against 16.5 percent nationally, and their own
resident inpatient rate has run at or above the national children's rate every year HCUPnet
reports. A Minnesota epilepsy stay in 2023 billed $50,555 in charges and cost the hospital
$17,649 on average, both lower than the national mean, and in-hospital deaths from epilepsy
ran below the national rate in every year from 2016 to 2023.

HCUPnet cannot isolate status epilepticus specifically. The closest available category,
CCSR NVS009, bundles chronic epilepsy together with single convulsions and febrile seizures,
so a status-epilepsy-specific Minnesota count would need record-level data MDH or the
Minnesota Hospital Association would have to pull directly.

Source: Agency for Healthcare Research and Quality, HCUPnet (State Inpatient and State
Emergency Department Databases, Minnesota, data from the Minnesota Hospital Association;
Community-Level Statistics; Nationwide Inpatient Sample), accessed 2026.

## How long EMS takes to reach a seizure

The Minnesota Office of Emergency Medical Services pulled every ambulance record from 2021 to
2025 in which the crew recorded a seizure, at EDAN's request. There were 58,469 of them,
about 32 a day. The yearly count rose from 9,781 in 2021 to 12,401 in 2025, and part of that
rise may come from changes in reporting. About one record in four, 14,236 in all, was for a
patient under 18.

Half of these crews reached the scene within 6.6 minutes of dispatch. The slowest tenth took
13.6 minutes or more statewide, and the wait grows with distance from a metro area.

<iframe src="../../charts/ems_seizure_wait.html" class="microsim" width="100%" height="420" title="Chart: slowest tenth of EMS seizure responses, by county type" loading="lazy"></iframe>

| EMS seizure responses, 2021 to 2025 | Metropolitan | Nonmetro, urban | Nonmetro, large town | Rural |
|---|---:|---:|---:|---:|
| Median minutes, dispatch to scene | 6.5 | 6.7 | 6.7 | 9.0 |
| Slowest tenth, minutes or more | 12.7 | 14.8 | 17.1 | 21.0 |
| Crew gave a benzodiazepine | 15.9% | 18.2% | 17.8% | 13.5% |

Crews gave a benzodiazepine (midazolam, lorazepam or diazepam) in about 16 percent of records,
with no change across the five years. About 80 percent of patients were taken to a hospital.
The lower benzodiazepine share in rural counties may reflect crews trained at the basic life
support level, who do not carry these drugs. The records cannot show that.

How we counted. A record is one crew's patient care report, so two crews at the same patient
make two records. The selection covers emergency responses and public assistance calls where
the symptom or either impression began with ICD-10 R56 or G40 or named a seizure. Response
times below zero or above four hours, and blanks, were left out (10,422 records, mostly 2021
and 2022). County type is the USDA rural-urban category.

Source: Minnesota Office of Emergency Medical Services, MNSTAR summary data, request
R000881-100126, November 2026. As a regulatory agency, the OEMS does not validate results
derived from the use of the raw data.

## What comes next
- Giving the map to the Minnesota Epilepsy Program at MDH as a candidate "area of need."
- Pharmacy distance is now in the same file and the lookup tool, so one map shows the
  whole picture. The next pass swaps the federal registry for the Minnesota Board of
  Pharmacy list to drop closed stores.

## Check yourself
??? quiz "1. What is a Level 4 epilepsy center?"
    The highest designation from the National Association of Epilepsy Centers: a center that
    can do full monitoring, complex drug management, and epilepsy surgery. Minnesota has four.

??? quiz "2. Why are border-state clinics included in the map?"
    A family in Luverne is about 28 miles from Sioux Falls and about 170 from Minneapolis, in a straight line. Leaving out
    Sioux Falls would overstate the gap in southwest Minnesota by more than 100 miles.

??? quiz "3. Does 'nearest child neurologist' mean they are taking new patients?"
    No. The federal registry shows who holds the credential and a practice address, not
    availability, so the distances are a best case.

## Who uses this data
The map is meant for the Minnesota Department of Health, the Epilepsy Foundation of Minnesota
and legislators working on rural care. Families looking for a specialist can find
Minnesota's pediatric epilepsy programs in [Resources & Support](../resources/index.md).
