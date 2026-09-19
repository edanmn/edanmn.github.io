# 3. Medication access

Status: data published September 2026; family guide in review.

## The gap
For most conditions a missed dose is a nuisance. For epilepsy, going without medicine for a
stretch is what causes harm. In a study of 33,658 adults with epilepsy on Medicaid, the
periods when people were not taking their medicine carried about three times the death rate,
one and a half times the emergency visits, and twice the rate of injury-causing crashes. A
single forgotten dose is a different thing, and a 2026 study found it did not raise seizure
risk in the hours after. Nationally, among adults with active epilepsy, about 13 percent say
they could not afford their prescription and about 9 percent skip doses to save money. Adults
without epilepsy report 6 to 8 percent on the same questions. Two other things stand between a Minnesota family and
the pill: supply problems (FDA currently lists a valproate injection shortage open since
2020, and discontinuations of several other seizure products) and distance.
Minnesota has lost 13 percent of its community pharmacies since 2009, and about one in five
residents now lives in a low-access area.

## What the data shows
We pulled every Minnesota Medicaid antiseizure prescription from 2019 through early 2026
from the federal State Drug Utilization Data.

![Minnesota Medicaid antiseizure prescriptions and spending, 2019 to 2026](../img/medicaid_asm_trend.png)

| 2025 | Value |
|---|---|
| Antiseizure prescriptions paid by Minnesota Medicaid | about 335,000 |
| Total reimbursed | $44 million |
| Average cost, lamotrigine (most common) | $24 per prescription |
| Average cost, rescue diazepam | $1,444 |
| Average cost, cannabidiol (Epidiolex) | $3,739 |
| Average cost, vigabatrin | $13,724 |

Clobazam prescriptions fell 34 percent between the first and second quarters of 2024. We
first read that as a shortage, and we were wrong. We checked both national shortage trackers
as they stood during 2024, using archived snapshots of the FDA list and the ASHP list, and
neither recorded a clobazam shortage that year. The only clobazam entry anywhere is one
company discontinuing its 20 mg tablet. Sixteen other seizure medicines fell by a fifth or
more in the same quarter, and a shortage hits one drug at a time. Minnesota's Medicaid
renewals after the pandemic ran through mid-2024, which fits the pattern better. Medicaid covers
at most a third of Minnesotans with epilepsy; commercial claims are held by MDH and we have
asked for them.

## What a Minnesota family actually pays

Medicaid prices are not what a working family sees. In September 2026 we pulled the federal
drug pricing file, checked which seizure medicines have a generic, priced ten real Minnesota
insurance plans, and read the state's own claims data. Four things stand out.

**Six seizure medicines have no generic at all.** Epidiolex, Fintepla, Xcopri, Ztalmy,
Diacomit and nasal midazolam. In Minnesota Medicaid they are 1.5 percent of seizure
prescriptions and 32 percent of the spending.

![Six seizure medicines have no generic and take a third of the spending](../img/asm_brandonly_share.png)

**Where a generic exists, the gap is enormous.** A month of generic clobazam costs a pharmacy
about $15. The brand, Onfi, costs about $1,795. Generic levetiracetam is $4.43 against $595
for Keppra. Some children cannot switch between versions without losing seizure control.

![What a month of seizure medicine costs a pharmacy](../img/asm_brand_vs_generic.png)

**Minnesotans on commercial insurance pay far more than people on public programs.** From the
Minnesota All Payer Claims Database for 2022: $18.48 out of pocket per fill on a commercial
plan, against $9.30 on Medicare and $1.31 on Medical Assistance. For the expensive drugs the
median payment is $0.00 and the average is hundreds, which is the deductible pattern. Across a
year, commercial members taking fenfluramine paid $1,822 on average, eslicarbazepine $1,460,
and cannabidiol $1,073.

**Prices keep rising, and Minnesota knows it.** Under the state's 2023 transparency law,
manufacturers have reported 50 price increases on seizure drugs since 2022. Sabril rose about
15 percent in twelve months, to $20,182 for a bottle of 100 tablets. Onfi rose about 24
percent over three January increases. Anticonvulsants have been a top-ten class in every
reporting period, and the median two-year increase for the class has climbed from 15 percent
to 31 percent. The reasons manufacturers give are boilerplate, and in two cases the reason was
withheld as a trade secret.

Bills before the legislature (HF 3652 and SF 3786) would add epilepsy to Minn. Stat. 62Q.481,
which since 2023 has capped what a Minnesotan pays for diabetes, asthma and severe allergy
medicine at $25 a month. The Department of Commerce estimates current epilepsy cost sharing at
$44.71 a month, with $17.35 of that above the $25 line, and prices the change at four cents
per member per month. Both bills died with this legislature and would need to be reintroduced
in 2027.

Sources and methods: `data/mn_apcd_rx_asm_summary.md`, `data/nadac_asm_summary.md`,
`data/mn_brandonly_asm_summary.md`, `data/mn_plan_cost_sharing_summary.md` and
`data/mn_rx_price_transparency_summary.md` in our public repository.

## Explore: which drugs, and what they cost
Click a drug name in the legend to show or hide it. The most common drugs are cheap generics.
The drugs a child with hard-to-control epilepsy needs are the expensive ones.

<iframe src="../../charts/asm_by_molecule.html" class="microsim" width="100%" height="540" title="Medicaid antiseizure prescriptions by drug" loading="lazy"></iframe>

<iframe src="../../charts/asm_cost_per_rx.html" class="microsim" width="100%" height="700" title="Cost per prescription by drug" loading="lazy"></iframe>

## Try it: the pharmacy problem solver
Answer three questions and get the next step for today.

<iframe src="../../sims/pharmacy-problem/main.html" class="microsim" width="100%" height="520" title="Pharmacy problem solver" loading="lazy"></iframe>

[Open full screen](../sims/pharmacy-problem/main.html){ .md-button }

## Check yourself
??? quiz "1. A pharmacy is out of your seizure medicine. What is the first question to ask?"
    "Is this a national shortage or just your stock?" A stock problem is fixed by a transfer
    or an independent pharmacy; a national shortage needs the prescriber the same day.

??? quiz "2. You have two days of pills left and the plan wants prior authorization. What do you say?"
    "Emergency supply." Medical Assistance and most plans allow a 72-hour fill while the
    authorization is processed. Never skip doses while waiting.

??? quiz "3. Why does a broad drop across many drugs in one quarter probably not mean a shortage?"
    Shortages hit one molecule. A drop across unrelated drugs at once points to fewer people
    enrolled or late reporting. In 2024 Minnesota's Medicaid renewals fit that pattern.

## What we are doing this year
- Keeping this dashboard current each quarter and flagging shortage signals.
- Mapping distance from every school district to the nearest retail pharmacy. First pass,
  September 2026: 15 districts are more than 15 miles from any retail pharmacy, and 14 of
  those also post no findable seizure plan. Grygla, Red Lake, Floodwood, and Nett Lake are
  farthest. Look up any district in the [Distance to Care Lookup](../sims/distance-lookup/index.md).
- Publishing a one-page family guide, "When the pharmacy can't fill your seizure medicine,"
  in English, Spanish, Hmong, and Somali, distributed through the Epilepsy Foundation of
  Minnesota's care coordinators and the pediatric epilepsy clinics.
- Supporting HF 3652 / SF 3786, which would cap what commercial plans can charge for
  epilepsy drugs at $25 a month, the same protection diabetes and asthma already have. The
  state's own actuaries priced it at four cents per member per month. Students are ready to
  testify when it is heard.

## Help affording medication now
See [Resources & Support](../resources/index.md) for assistance programs, Medical
Assistance, and MA-TEFRA.
