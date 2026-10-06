# Data and Methods

We publish the method with the data, so you can check it. This page is where to download the
district audit, see what each column means, and tell us when something is wrong.

## Download the audit

[Download the district audit (CSV)](mn_seizure_plan_audit.csv){ .md-button .md-button--primary download="mn_seizure_plan_audit.csv" }

One row for each of the 329 Minnesota school districts we checked, as of June 2026. It is the
same data behind [Find Your District](../find-your-district/index.md) and
[The Audit](../chapters/05-the-data-case-study/index.md).

| Column | What it holds |
|--------|---------------|
| `isd` | District number |
| `district`, `county`, `city` | Name and location |
| `locale` | District type: City, Suburb, Town or Rural |
| `enrollment` | Students enrolled, blank where we have no figure |
| `classification`, `classification_label` | The audit result, one of the four categories below |
| `what_we_saw` | Our note on what the district's website showed |
| `source_url` | The page we checked |
| `checked` | When we checked it |
| `posted_since_check` | "yes" where a later re-check found a plan form or handbook section posted after the June audit |
| `district_reply` | `confirmed`, `in_progress` or `pending` where a district has replied to us by email |
| `district_reply_summary` | What the district told us, with the role of the person who replied and never their name |

The file leaves out phone numbers and the names of district contacts.

## County profiles

[Epilepsy by County](../counties/index.md) joins the county-level data into one row for each
of the 87 counties, with the file to download and the method.

## Legislative district profiles

[Epilepsy by Legislative District](../legislative-districts/index.md) has an estimate for each of
the 134 House and 67 Senate districts, with the school districts that serve each one. Both
files can be downloaded there, with the method.

## What the categories mean

| `classification` | `classification_label` | Meaning |
|------------------|------------------------|---------|
| `FOUND_SEIZURE_SPECIFIC` | Seizure plan posted | A seizure-specific plan or page is publicly findable |
| `FOUND_MED_POLICY_ONLY` | Medication policy only | A general medication policy exists, but never mentions seizures |
| `NOT_FOUND` | Nothing found | No relevant policy posted online |
| `NOT_VERIFIABLE` | Could not check | Site or policies were inaccessible |

!!! warning "What this measures"
    We measured **public findability**, not legal compliance. A district with nothing posted
    may still have an internal plan.

How we checked each district, and how reliable the check is, is written up in
[The Audit: Mapping the Gaps](../chapters/05-the-data-case-study/index.md).

## Code

The scripts that build the district lookup, the district table and the charts are in the
site's repository: <https://github.com/edanmn/edanmn.github.io>.

## Corrections

We correct mistakes and say that we did.

- **September 25, 2026.** A re-check found a seizure action plan form on Paynesville Area
  Schools' health services page that the June check missed. The count of districts with a
  posted plan moved from 97 to 98.

Found an error or an out-of-date entry? Write to <edanmnorg@gmail.com>. A district can also
[tell us what it has in place](../programs/report-your-district/index.md).

## Using this data

Everything we produce is free to use and adapt.
