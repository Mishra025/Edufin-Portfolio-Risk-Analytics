# EduFin Portfolio Intelligence

EduFin Portfolio Intelligence is a Streamlit analytics interface built from three EduFin notebooks and the `loans.csv` dataset. It converts the notebook work into an interactive dashboard for portfolio health, customer and segment risk, cohort analysis, loan exploration, and recovery/loss scenario planning.

## Repository Recommendation

Use **one GitHub repository** for this project.

Reason: the three notebooks are connected parts of one EduFin risk-analysis case study. Day 1 covers portfolio health, Day 2 covers customer/segment risk, and Day 3 covers timeline/cohort risk. Keeping them in one repo makes the project easier to explain, run, review, and deploy as a single portfolio application.

Suggested repo name:

```text
edufin-portfolio-intelligence
```

Suggested structure:

```text
edufin-portfolio-intelligence/
  app.py
  requirements.txt
  README.md
  data/
    loans.csv
  notebooks/
    ashishmishra_SAP174B9_PH_Day1.ipynb
    ashishmishra_SAP174B9_Day2.ipynb
    Ashish_Mishra_SAP174B9_Day3.ipynb
```

Separate repositories would only make sense if each notebook became a completely independent product with its own data, deployment, and documentation. For this case, one repo is the stronger choice.

## Project Objective

The project analyzes an education-finance loan portfolio and helps decision makers answer:

- What is the overall health of the portfolio?
- How much capital is exposed through defaulted and overdue loans?
- Which loan purposes, tenures, customers, institutions, and disbursement cohorts show higher risk?
- What is the likely loss under different recovery assumptions?
- What information is missing for deeper repayment and default-timeline analysis?

## Dataset Summary

Source file: `data/loans.csv`

Rows: **5,000 loans**

Columns: **12**

Key fields:

- `loan_id`
- `customer_id`
- `institution_id`
- `loan_amount`
- `loan_status`
- `interest_rate`
- `loan_tenure_months`
- `application_date`
- `disbursement_date`
- `maturity_date`
- `emi_amount`
- `purpose_of_loan`

Dataset scale:

- Unique customers: **3,000**
- Unique institutions: **3,183**
- Total portfolio value: **INR 204.82 Cr**
- Average loan size: **INR 4.10 L**
- Median loan size: **INR 3.67 L**
- Minimum loan amount: **INR 1.50 L**
- Maximum loan amount: **INR 9.87 L**
- Average interest rate: **12.77%**
- Average tenure: **66.43 months**
- Average EMI: **INR 9,351.16**
- Disbursement date range: **2021-08-07 to 2025-07-03**

## Portfolio Results

Status distribution:

| Status | Loans | Loan % | Amount | Amount % |
|---|---:|---:|---:|---:|
| Active | 3,965 | 79.30% | INR 162.41 Cr | 79.29% |
| Defaulted | 590 | 11.80% | INR 24.24 Cr | 11.83% |
| Overdue | 273 | 5.46% | INR 10.94 Cr | 5.34% |
| Closed | 172 | 3.44% | INR 7.24 Cr | 3.53% |

Risk metrics:

- Default rate: **11.80%**
- Portfolio-at-risk rate by loan count: **17.26%**
- Portfolio-at-risk exposure: **INR 35.18 Cr**
- At-risk exposure as amount share: **17.18%**
- Health classification: **HIGH RISK**

The health classification uses these thresholds:

- 0-5% default rate: `HEALTHY`
- 5-10% default rate: `MODERATE RISK`
- 10-15% default rate: `HIGH RISK`
- Greater than 15% default rate: `CRITICAL`

## Segment Facts

Purpose-level risk:

| Purpose | Loans | Default Rate | At-Risk Rate | Amount |
|---|---:|---:|---:|---:|
| Course Fees | 1,797 | 11.96% | 17.58% | INR 72.72 Cr |
| Course Fees + Living | 1,708 | 11.71% | 16.92% | INR 69.19 Cr |
| Living Expenses | 774 | 10.34% | 15.50% | INR 33.29 Cr |
| Equipment & Books | 486 | 13.37% | 19.14% | INR 20.18 Cr |
| Hostel Fees | 235 | 12.77% | 19.15% | INR 9.43 Cr |

Tenure-level risk:

- Highest default rate by tenure: **60 months at 13.17%**
- Highest at-risk rate by tenure: **60 months at 18.95%**
- Lowest at-risk rate by tenure: **96 months at 14.45%**

High-risk disbursement cohorts with at least 30 loans:

| Cohort | Loans | Default Rate | At-Risk Rate | Amount |
|---|---:|---:|---:|---:|
| 2023-09 | 94 | 19.15% | 27.66% | INR 3.73 Cr |
| 2024-11 | 100 | 16.00% | 24.00% | INR 4.06 Cr |
| 2022-06 | 106 | 13.21% | 23.58% | INR 4.27 Cr |
| 2023-10 | 128 | 14.06% | 22.66% | INR 5.52 Cr |
| 2025-01 | 137 | 11.68% | 21.90% | INR 5.35 Cr |

## App Features

- CSV upload for new EduFin-style datasets
- Sidebar filters for status, purpose, tenure, loan amount, and disbursement period
- Executive KPI cards for loan count, customer count, institution count, total exposure, defaults, and at-risk exposure
- Portfolio health classification based on default-rate thresholds
- Status distribution charts by loan count and loan amount
- Segment risk ranking by purpose, tenure, institution, or customer
- Disbursement cohort tracking by month
- Searchable loan explorer
- Download button for filtered data
- Recovery and expected-loss scenario simulator
- Notebook facts and data-limitation notes

## Technical Terms Used

- **Portfolio-at-risk (PAR):** loans that are already defaulted or overdue.
- **Default rate:** defaulted loans divided by total loans.
- **At-risk rate:** defaulted plus overdue loans divided by total loans.
- **Exposure:** total outstanding loan amount represented by a group of loans.
- **Cohort:** loans grouped by a shared period, here the disbursement month.
- **Risk segmentation:** dividing the portfolio by purpose, tenure, customer, or institution to identify concentrated risk.
- **Recovery rate:** expected percentage of overdue/defaulted exposure that may be collected.
- **Expected loss:** estimated unrecovered value after applying recovery assumptions.
- **Executive health classification:** automated portfolio status label derived from default-rate thresholds.

## Important Data Limitations

The provided CSV does not include:

- `default_date`
- repayment transaction table
- payment status history
- credit score
- borrower income
- institution names
- collateral information
- collection or recovery outcomes

Because of this, the app directly supports portfolio health, segmentation, disbursement-cohort analysis, and scenario planning. True repayment seasonality, exact days-to-default, and cumulative loss timeline analysis require additional repayment/default event fields.

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Notebook Mapping

- `ashishmishra_SAP174B9_PH_Day1.ipynb`: Portfolio Health Analysis
- `ashishmishra_SAP174B9_Day2.ipynb`: Customer Risk Analysis
- `Ashish_Mishra_SAP174B9_Day3.ipynb`: Crisis Timeline / Cohort Analysis

## Business Conclusion

The portfolio is currently **HIGH RISK** because the default rate is **11.80%**, which crosses the 10% threshold. The combined defaulted and overdue exposure is **INR 35.18 Cr** out of **INR 204.82 Cr**, meaning a significant share of the portfolio needs recovery focus, tighter underwriting, and closer segment monitoring.
