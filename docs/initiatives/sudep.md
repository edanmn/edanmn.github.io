# 5. SUDEP

Status: started September 2026. This page and the device guide are student-written from
public sources and have not yet been reviewed by a clinician or the Epilepsy Foundation of
Minnesota; we are seeking that review. Nothing here is medical advice.

## The gap
Sudden Unexpected Death in Epilepsy is rare, about one in a thousand adults with epilepsy a
year and far lower in children, and it is the outcome every family fears. The Minnesota
Department of Health reports around 1,000 deaths a year in the state related to epilepsy or
seizures. How many are SUDEP, nobody knows: it has no diagnostic code, and death certificates
record it as "epilepsy" or "undetermined." Illinois, New Jersey, and North Carolina require
medical examiners to look for it and report it. Minnesota does not.

The best-supported ways to lower risk are good seizure control, taking medication as
prescribed, and supervision at night. Since January 2024 Minnesota Medical Assistance has
covered seizure detection devices, wearables that alert a caregiver to a convulsive seizure.
Minnesota was the first state to do this. Most eligible families have not heard of it.

## What the death data shows
We pulled every Minnesota death certificate from 2018 to 2024 that mentions epilepsy or
seizures, from the CDC's multiple cause of death files.

<iframe src="../../charts/mortality_by_year.html" class="microsim" width="100%" height="480" title="Minnesota deaths mentioning epilepsy or seizures by year" loading="lazy"></iframe>

| 2018 to 2024, Minnesota residents | Deaths | Per year |
|---|---|---|
| Any mention of epilepsy or seizures on the certificate (G40, G41, R56) | 6,077 | about 870 |
| Any mention of epilepsy (G40, G41) | 1,404 | about 200 |
| Epilepsy as the underlying cause of death | 415 | about 60 |

Both counts rose across the seven years, from 728 to 967 for any seizure mention and from
153 to 233 for epilepsy. Rates are low through childhood, rise steadily through adulthood,
and climb steeply after 65, when seizures ride along with strokes, dementia, and other
conditions. The epilepsy-specific count peaks at ages 65 to 74.

<iframe src="../../charts/mortality_by_age.html" class="microsim" width="100%" height="480" title="Rate by age" loading="lazy"></iframe>

SUDEP is inside the epilepsy count and cannot be separated from it. That is the whole
problem. Only 27 of 87 counties had enough epilepsy-specific deaths in seven years to
report a number at all; the other 60 are suppressed as fewer than 10, and those are
the same counties with the smallest districts, the longest ambulance runs, and the farthest
specialists. Source and method:
`data/mn_epilepsy_mortality_summary.md`.

## Where these deaths happen, and how Minnesota compares

SUDEP usually happens at home, often during sleep, and often with nobody present. Death
certificates almost never say so. The closest public measure is where people died, and for
younger Minnesotans that pattern is stark.

| Minnesota, 2018 to 2024 | Died at home | Total |
|---|---|---|
| Epilepsy mentioned anywhere on the certificate, all ages | 458 (33%) | 1,404 |
| Epilepsy mentioned anywhere, ages 1 to 44 | 169 (54%) | 311 |
| Epilepsy as the underlying cause, ages 1 to 44 | 98 (64%) | 152 |

Nearly two in three young Minnesotans whose deaths were caused by epilepsy died at home. That
is the population where SUDEP is most likely and least likely to be recorded as such. It is a
proxy, not a count: dying at home is not proof of SUDEP, and some SUDEP deaths happen
elsewhere.

Minnesota's epilepsy death rate also runs above the national one. Age-adjusted, 2018 to 2024,
Minnesota is 3.0 deaths per 100,000 against 2.4 nationally, about 25 percent higher. We are
clearly above Wisconsin, North Dakota and the United States. Iowa and South Dakota overlap
with us, so there is no real difference there.

![Minnesota's epilepsy death rate against neighboring states](../img/epilepsy_mortality_neighbors.png)

One caution before reading too much into that gap. A state's rate depends partly on how often
doctors write epilepsy on a death certificate, which varies. A higher rate may mean more
deaths, better recording, or both. Source and method:
`data/mn_epilepsy_mortality_place_summary.md`.

## What we are doing this year
- A plain-language family guide to the seizure detection device benefit: who qualifies, how
  to ask, what to do if denied. Distributed through EFMN care coordinators and the pediatric
  epilepsy clinics.
- A public-records request to find out how many devices Medical Assistance has covered, so
  the benefit can be measured.
- Keeping the death analysis above current each year as CDC releases data, and adding
  regional groupings so rural rates can be shown without breaking suppression rules.
- A draft Minnesota SUDEP investigation and reporting law, modeled on Illinois, for the
  Epilepsy Foundation of Minnesota and the authors of the 2025 epilepsy program law. Its
  data would feed the mortality count the state is now required to publish.

## Try it: could a seizure detection device be covered?
Four yes-or-no questions. It explains the Medical Assistance criteria; only the plan and the
neurologist can decide.

<iframe src="../../sims/device-benefit-check/main.html" class="microsim" width="100%" height="480" title="Seizure detection device benefit check" loading="lazy"></iframe>

[Open full screen](../sims/device-benefit-check/main.html){ .md-button }

## Myth or fact
??? quiz "1. SUDEP is common."
    Myth. About 1 in 1,000 adults with epilepsy per year, and about 1 in 4,500 children. It
    is rare, and rarer still when seizures are controlled.

??? quiz "2. A seizure alert watch prevents SUDEP."
    Myth. No device has been proven to prevent it. Devices detect convulsive seizures and
    bring a caregiver faster, which supports nighttime supervision, a recognized risk reducer.

??? quiz "3. Minnesota counts SUDEP deaths."
    Myth, for now. SUDEP has no diagnostic code and Minnesota has no reporting rule, so the
    number is unknown. Illinois, New Jersey, and North Carolina require examiners to report it.

??? quiz "4. Taking medication as prescribed lowers the risk."
    Fact. Uncontrolled generalized tonic-clonic seizures are the main risk factor; adherence
    and good seizure control are the most consistent protective steps.

## Talking about SUDEP
A calm explanation for families is in [Resources & Support](../resources/index.md), and
recent research on lowering risk is in [Research, Translated](../research-translated/index.md).

!!! note
    Ask your neurologist about your own or your child's risk. Most people with epilepsy have
    a low risk, and it is lower still when seizures are controlled.
