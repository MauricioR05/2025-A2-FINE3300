# 2025-A2-FINE3300
# FINE3300 - Assignment 2

This project is divided into two major components: **Part A** (mortgage payment schedules) and **Part B** (CPI and cost-of-living analysis across Canadian provinces). The goal is to apply interest rate and inflation concepts in real financial planning and regional purchasing power comparisons.

---

## Part A: Mortgage Payment Schedules

### Overview
Part A calculates mortgage payment amounts under different payment frequency structures using the standard **Canadian semi-annual compounding convention**. When provided:

- Mortgage principal ($)
- Quoted annual interest rate (%)
- Amortization period (years)
- Term length (years)

The program then generates full amortization schedules for the following payment plans:

- Monthly
- Semi-Monthly
- Bi-Weekly
- Weekly
- Rapid Bi-Weekly (half of monthly payment, same frequency as bi-weekly)
- Rapid Weekly (quarter of monthly payment, same frequency as weekly)

### Files
- `mortgage.py` — Contains the `MortgagePayment` class (carried forward from Assignment 1 without modification).
- `MortgageMain.py` — User interface script that collects input, computes schedules, and generates output files.

### Output
| File | Description |
|------|-------------|
| **LoanSchedules.xlsx** | Each payment schedule is stored on a separate worksheet. |
| **LoanBalanceDecline.png** | A comparative line graph showing how the remaining balance decreases under each schedule over the term. |

Part B: CPI & Cost of Living Analysis
Overview
Part B analyzes inflation data across Canada and the provinces using Consumer Price Index (CPI) data for 2024. The project consolidates monthly CPI values into one standardized dataset and uses it to compare:

Inflation differences across regions
Nominal vs. real minimum wage levels
Cost of services inflation (Jan → Dec)

This allows to evaluate which provinces experienced the highest inflation, and how inflation affects purchasing power and wage comparisons.

### Files
**cpi.py** — Contains all CPI calculations, data cleaning functions, and economic analytics.
**cpi_main.py** — User interface script that prints results and saves output files.