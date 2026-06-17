# 5. The Data: Mapping the Gaps

This chapter is the research heart of the book. We asked a simple question with a measurable
answer: **how many Minnesota school districts post a seizure plan that families and staff can
actually find?** The charts below are interactive, hover, zoom, and explore.

!!! tip "Want to check your own district?"
    Jump to [Explore the Data](../../explore/index.md) and search your district by name.

## How we measured it
For **328 of Minnesota's ~329 regular public school districts**, we reviewed the official
district website: the school-board policy page (MSBA Policy 516, Student Medication), the
health-services page, and the student/parent handbook. We classified each district into one of
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
plan (231 of 328). Only about 30% do. Most districts post only a general medication policy that
never mentions seizures.

<iframe src="../../charts/classification_breakdown.html" class="microsim" width="100%" height="380" title="What Minnesota districts post" loading="lazy"></iframe>

## The gap follows a strong gradient by district type
City and suburban districts are far more likely to post a plan than town and rural districts.
A statistical test confirms this is not chance (chi-square p < 0.0001).

<iframe src="../../charts/gap_by_locale.html" class="microsim" width="100%" height="430" title="Plan rate by district type" loading="lazy"></iframe>

## Where the gaps are, county by county
Darker counties have a higher share of districts with no public seizure plan. Hover any county
for its numbers. The gap covers most of Greater Minnesota, with the metro area lighter.

<iframe src="../../charts/gap_map.html" class="microsim" width="100%" height="540" title="Interactive map of seizure-plan gaps by county" loading="lazy"></iframe>

## The real driver is size, not "rural"
We built a logistic regression to ask what predicts a public plan. The dominant factor was
**district enrollment**, bigger districts are far more likely to post a plan. Once we
accounted for size, "rural" was no longer a significant predictor on its own. You can see the
size effect directly:

<iframe src="../../charts/size_effect.html" class="microsim" width="100%" height="430" title="Plan rate by enrollment" loading="lazy"></iframe>

The honest interpretation: this is a **capacity** problem. Small districts, most of which are
rural, simply do not have the nursing and administrative staff to write and post a current
plan. Minnesota's own data backs this up: about **half of districts have no licensed school
nurse**, and the smallest districts are worst off.

And the gap tends to be largest exactly where community health needs are highest, hover the
bubbles (size = number of districts in that county):

<iframe src="../../charts/county_need_vs_gap.html" class="microsim" width="100%" height="430" title="County need versus gap" loading="lazy"></iframe>

This changes how we help: do not lecture small districts, **do the work for them** with a
ready-to-use packet.

## What this means for you

=== "If you are a parent"
    Your district showing "no plan posted" does not mean your child cannot get one, it means
    you may need to ask. The law (Minn. Stat. 121A.24) is on your side. Look up your district
    in [Explore the Data](../../explore/index.md), then use the
    [family guide and copy-paste email](../06-how-to-help/index.md) to request a plan.

=== "If you are a school or district"
    If your district is in the ~70%, closing the gap can take about 30 minutes. See the free
    [drop-in packet](../06-how-to-help/index.md): a seizure action plan template, policy
    language that cites 121A.24, and a printable poster. The single biggest step is simply
    **posting a seizure action plan template on your health-services page**.

## How reliable is this?
We re-checked a random sample of 30 districts with independent reviewers who did not see the
first ratings. They agreed **90% of the time** (Cohen's kappa = 0.82, "almost perfect"). When
they disagreed, the second reviewer usually found *more* seizure content, which means our 70%
figure may slightly **overstate** the gap, an error in the safe direction.

---
*Data sources: NCES/Urban Institute district roster, CDC PLACES county health data, MDH
school-nurse report. Full methods and reliability details are summarized on the
[Explore the Data](../../explore/index.md) page.*
