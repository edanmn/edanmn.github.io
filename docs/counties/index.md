# Epilepsy by County

One row for each of Minnesota's 87 counties: how many residents are estimated to have
epilepsy, whether the school districts post a seizure plan, how close specialist care is,
and how many deaths mention epilepsy or seizures.

<iframe src="county_table.html" width="100%" height="900" style="border:1px solid #e0e0e0;border-radius:8px" title="Epilepsy by Minnesota county" loading="lazy"></iframe>

!!! warning "These are estimates"
    No Minnesota agency counts people with epilepsy by county. The figures apply published
    rates to census counts. A school district that posts no plan can still have one on file.

## Request the data

The full county file has 42 columns for each county, including the House and Senate
districts that cover it. It is available on request. Write to <edanmnorg@gmail.com> and tell us who you are and how you plan to use it.

## What stands out

- 79 of 87 counties have no child neurologist practicing in them. About 2.6 million
  Minnesotans live in those counties, and an estimated 3,500 of the children there have
  epilepsy.
- 70 counties have no neurologist of any kind.
- In 35 counties, no school district posts a seizure plan.
- In 18 counties the number of deaths that mention epilepsy or seizures over seven years is
  under 10, so the CDC does not release it.

## How the numbers are built

| Figure | Method | Source |
|---|---|---|
| Residents with epilepsy | 1.10 percent of residents 18 and over, plus 0.6 percent of residents under 18 | Centers for Disease Control and Prevention, active epilepsy estimates, 2015 (MMWR 2017) |
| Population by age | County estimates for July 1, 2025 | U.S. Census Bureau, Vintage 2025 population estimates |
| School districts and seizure plans | Each school district is counted in the county of its district office | [The Audit](../chapters/05-the-data-case-study/index.md); National Center for Education Statistics for enrollment |
| Neurologists and pharmacies in the county | Providers with a Minnesota practice address, placed in a county by ZIP code | Federal NPI registry |
| Nearest child neurologist | Straight-line miles from each school district office; the table shows the middle district | Federal NPI registry |
| Ambulance time | Minutes within which 9 in 10 emergency calls had an ambulance on scene, 2023 | Minnesota Office of Emergency Medical Services |
| Deaths | Death certificates that mention epilepsy or seizures (ICD-10 G40, G41, R56), Minnesota residents, 2018 to 2024 | CDC WONDER, Multiple Cause of Death |
| Type of county | Rural-Urban Continuum Codes, 2023 | U.S. Department of Agriculture |

## What to keep in mind

- A provider is counted where the practice ZIP code mostly lies. A ZIP code that crosses a
  county line is counted in one county only, and a specialist may see patients in clinics
  outside the listed address.
- A county with no child neurologist may sit next to one that has several. The distance
  column is the better guide to how far a family travels.
- Death counts depend on what certifiers write. They are counts of certificates and say
  nothing about how many deaths were sudden unexpected death in epilepsy. See
  [SUDEP](../initiatives/sudep.md).
- The audit covers the 329 regular school districts. Charter schools are not in it.
