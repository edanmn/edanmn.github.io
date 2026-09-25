# 2. The state's epilepsy data

Status: started September 2026.

## The gap
Until 2025, no Minnesota agency was responsible for counting epilepsy. That changed with a
2025 law championed by the Epilepsy Foundation of Minnesota, which created a Minnesota
Epilepsy Program at the Department of Health. Its data section, Minn. Stat. 145.9231, requires
the commissioner to collect and report, every year, the number of diagnoses, clinical outcomes, mortality, and related
population health data, to make deidentified data public, and to identify areas of need.

The program is new. It has not yet published. And the one dataset that shows need at the
school district level, ours, is not something a state agency has.

## What we are doing this year
- Offering the district audit, the nurse-staffing analysis, and the ambulance response layer
  to the program as an input to its first coordination plan, with the code and a data
  dictionary, under an open license.
- Building the plain-language layer on top of whatever the state publishes: county maps, a
  "what this means for your family" page, a students' summary.
- Requesting public data that exists but is not posted, through the Minnesota Government
  Data Practices Act: per-district school nurse staffing, counts of seizure alert devices
  covered by Medical Assistance, and first-responder seizure training records.
- Re-running the school audit each spring so the state has a yearly readiness measure.

## Explore: the four layers we are handing the state
Each bubble is a county. Left to right is how long the slowest ambulance calls take; bottom
to top is the share of districts with no findable seizure plan; color is how likely a
district there has no school nurse; size is students. The upper right is where the state's
first "area of need" probably is.

<iframe src="../../charts/county_four_layers.html" class="microsim" width="100%" height="540" title="Four layers by county" loading="lazy"></iframe>

The county choropleth from the audit is in [The Data: Mapping the Gaps](../chapters/05-the-data-case-study/index.md).

## Check yourself
??? quiz "1. What does Minn. Stat. 145.9231 require MDH to do each year?"
    Collect, analyze, and report the number of epilepsy and seizure disorder diagnoses,
    clinical outcomes, mortality rates, and related population health data, make
    deidentified data public, and identify areas of need with strategies to address them.

??? quiz "2. Which of the four layers did a state agency already hold before EDAN?"
    None at the district level. Ambulance times (OEMS) and nurse staffing (MDH, aggregate)
    exist as state reports; the seizure-plan audit and the district-level join are EDAN's.

??? quiz "3. How does a student organization get data into a state plan?"
    By offering it early, in a format the agency can use (CSV, data dictionary, open
    license), through the partner that carried the law, and by asking for something specific.

## Why it matters
A student project ends when the student graduates. A state program does not. The point of
this initiative is to make sure the work outlives us.

## Sources
- Minn. Stat. 145.9231: https://www.revisor.mn.gov/statutes/cite/145.9231
- MDH Epilepsy program: https://www.health.state.mn.us/diseases/epilepsy/index.html
