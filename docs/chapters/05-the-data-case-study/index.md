# The Audit: Mapping the Gaps

This is the study the rest of the schools work rests on. We asked a question with a measurable
answer: **how many Minnesota school districts post a seizure plan that families and staff can
actually find?** The charts below are interactive: hover over them, or tap, for the numbers.

!!! tip "Want to check your own district?"
    Jump to [Find Your District](../../find-your-district/index.md) and search your district by name.

## How we measured it
For all **329 of Minnesota's regular public school districts**, we reviewed the official
district website: the school-board policy page (MSBA Policy 516, Student Medication), the
health-services page, and the student/parent handbook. The first pass used AI-assisted web
searches to find these pages, applying a fixed rubric. We classified each district into one of
four categories:

| Category | Meaning |
|----------|---------|
| Seizure plan posted | A seizure-specific plan or page is publicly findable |
| Medication policy only | A general medication policy exists, but never mentions seizures |
| Nothing found | No relevant policy posted online |
| Could not check | Site or policies were inaccessible |

!!! warning "What this measures"
    We measured **public findability**, not legal compliance. A district with nothing posted
    may still have an internal plan. That is why this is a starting point for outreach, not a
    verdict on any school.

## What we found
<span class="edan-stat">~70%</span> of districts post **no** publicly findable seizure-specific
plan (231 of 329, including 18 we could not check). Only about 30% do (98 of 329). Most
districts post only a general medication policy that never mentions seizures.

*Corrected September 25, 2026: a re-check found a seizure action plan form on Paynesville Area
Schools' health services page that the June check missed. The count of districts with a posted
plan moved from 97 to 98.*

<iframe src="../../charts/classification_breakdown.html" class="microsim" width="100%" height="190" title="What Minnesota districts post" loading="lazy"></iframe>

??? note "The numbers in this chart"
    | What the district posts | Districts | Share of 329 |
    |-------------------------|-----------|--------------|
    | Seizure plan posted | 98 | 30% |
    | Medication policy only (no seizure mention) | 195 | 59% |
    | Nothing relevant found online | 18 | 5% |
    | Could not check | 18 | 5% |

## The gap follows a strong gradient by district type
City and suburban districts are far more likely to post a plan than town and rural districts.
A statistical test confirms this is not chance (chi-square p < 0.0001).

<iframe src="../../charts/gap_by_locale.html" class="microsim" width="100%" height="340" title="Plan rate by district type" loading="lazy"></iframe>

??? note "The numbers in this chart"
    | District type | Districts | Post a seizure plan |
    |---------------|-----------|---------------------|
    | City | 14 | 71% |
    | Suburb | 33 | 58% |
    | Town | 56 | 41% |
    | Rural | 226 | 20% |

## Where the gaps are, county by county
Each county is shaded by the share of its districts with no public seizure plan; the key beside
the map gives the scale. Hover any county for its numbers. The gap covers most of Greater
Minnesota and is smaller in the metro area.

<iframe src="../../charts/gap_map.html" class="microsim" width="100%" height="580" title="Interactive map of seizure-plan gaps by county" loading="lazy"></iframe>

The district-level data behind the map, with each district's county, is in the
[audit file, available on request](../../data/index.md).

## The real driver is size, not "rural"
We built a logistic regression to ask what predicts a public plan. The dominant factor was
**district enrollment**, bigger districts are far more likely to post a plan. Once we
accounted for size, "rural" was no longer a significant predictor on its own. You can see the
size effect directly:

<iframe src="../../charts/size_effect.html" class="microsim" width="100%" height="360" title="Plan rate by enrollment" loading="lazy"></iframe>

??? note "The numbers in this chart"
    | District enrollment | Districts | Post a seizure plan |
    |---------------------|-----------|---------------------|
    | Under 500 | 82 | 11% |
    | 500-999 | 96 | 19% |
    | 1,000-2,499 | 76 | 29% |
    | 2,500-9,999 | 58 | 67% |
    | 10,000+ | 15 | 67% |

The honest interpretation: this is a **capacity** problem. Small districts, most of which are
rural, simply do not have the nursing and administrative staff to write and post a current
plan. Minnesota's own data backs this up. About half of Minnesota school districts and charter
schools have no licensed school nurse. Among regular public districts more than 1 in 3 have none,
and in public districts under 500 students it is 79% (MDH, School Nurse Workforce: A 2022
Snapshot).

And the gap tends to be largest exactly where community health needs are highest, hover the
bubbles (size = number of districts in that county):

<iframe src="../../charts/county_need_vs_gap.html" class="microsim" width="100%" height="480" title="County need versus gap" loading="lazy"></iframe>

This changes how we help: do not lecture small districts, **do the work for them** with a
ready-to-use packet.

## What this means for you

=== "If you are a parent"
    "No plan posted" measures what a family can find online. A district may still have a
    plan on file. Look up your district in [Find Your District](../../find-your-district/index.md).
    For help with a child's plan, contact the
    [Epilepsy Foundation of Minnesota](https://www.epilepsyfoundationmn.org/).

=== "If you are a school or district"
    If your district is in the ~70%, closing the gap is straightforward with ready-to-use materials. See the free
    [drop-in packet](../../packet/EDAN-Seizure-Safe-Schools-Packet.pdf): a seizure action plan template, policy
    language that cites 121A.24, and a printable poster. The single biggest step is simply
    **posting a seizure action plan template on your health-services page**.

## How reliable is this?
We re-checked a stratified random sample of 30 districts in a separate pass that did not see the
first ratings. The two passes agreed **90% of the time** (Cohen's kappa 0.82 across the four
categories, "almost perfect", and 0.80 for plan versus no plan, "substantial"). When
they disagreed, the second pass usually found *more* seizure content, which means our 70%
figure may slightly **overstate** the gap, an error in the safe direction.

---
*Data sources: NCES and Urban Institute district roster, CDC PLACES county health data, and the
MDH school nurse workforce report. The campaign built on these findings is
[Seizure-Safe Schools](../../initiatives/seizure-safe-schools.md). Look up a single district in
[Find Your District](../../find-your-district/index.md).*
