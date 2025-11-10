# cpi_main.py
# Simple menu interface to run Part B tasks using cpi.py

import os
from pathlib import Path
import pandas as pd
from CPI import (
    DEFAULT_FILES,
    combine_cpi,
    average_month_to_month_change,
    highest_avg_change,
    equivalent_salary,
    load_min_wages,
    real_min_wage_by_province,
    services_annual_change,
    plot_services_annual_change,
    ITEMS_FOR_AVG_CHANGE,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = (BASE_DIR / ".." / "Sources").resolve()
MIN_WAGE_FILE = "MinimumWages.csv"  # put this in the data folder


def sample_for_q2(df: pd.DataFrame) -> pd.DataFrame:
    """Return 12 rows similar to the reference screenshot (Canada, Jan)."""
    sample = df[(df["Jurisdiction"] == "Canada") & (df["Month"] == "24-Jan")].head(12)
    if sample.empty:
        sample = df.head(12)
    return sample[["Item", "Month", "Jurisdiction", "CPI"]]


def print_q2_table(df: pd.DataFrame) -> None:
    """Pretty print rows so columns match the reference format."""
    widths = {
        "Item": 55,
        "Month": 8,
        "Jurisdiction": 15,
        "CPI": 6,
    }
    header = (
        f"{'Item':<{widths['Item']}}"
        f"{'Month':<{widths['Month']}}"
        f"{'Jurisdiction':<{widths['Jurisdiction']}}"
        f"{'CPI':>{widths['CPI']}}"
    )
    print(header)
    print("-" * len(header))
    for row in df.itertuples(index=False):
        item = row.Item
        if len(item) > widths["Item"]:
            item = item[: widths["Item"] - 1] + "…"
        print(
            f"{item:<{widths['Item']}}"
            f"{row.Month:<{widths['Month']}}"
            f"{row.Jurisdiction:<{widths['Jurisdiction']}}"
            f"{row.CPI:>{widths['CPI']}.1f}"
        )

def load_all(folder: str) -> pd.DataFrame:
    return combine_cpi(DEFAULT_FILES, folder=folder)

def run_all(folder: str):
    df = load_all(folder)

    # Q2) First 12 lines
    print("\nQ2) First 12 lines of the combined DataFrame:")
    head12 = sample_for_q2(df)
    print_q2_table(head12)

    # Q3) Average month-to-month changes
    print("\nQ3) Average month-to-month % change (Food, Shelter, All-items excl. food & energy):")
    avgchg = average_month_to_month_change(df, ITEMS_FOR_AVG_CHANGE)
    print(avgchg.to_string())

    # Q4) Highest average change per category
    print("\nQ4) Province with highest average change in each category:")
    winners = highest_avg_change(avgchg)
    for item, jur in winners.items():
        value = avgchg.loc[jur, item]
        print(f"{item}: {jur} ({value:.1f}%)")

    # Q5) Equivalent salary to $100,000 in Ontario (Dec 2024, All-items)
    print("\nQ5) Equivalent salary to $100,000 received in Ontario (Dec-24, All-items):")
    eq = equivalent_salary(df, base_jurisdiction="Ontario", base_amount=100000.0,
                           month="24-Dec", item="All-items")
    print(eq.to_string())

    # Q6) Minimum wage analysis (nominal & real)
    print("\nQ6) Minimum wage analysis (nominal and real):")
    wage_path = os.path.join(folder, MIN_WAGE_FILE)
    if not os.path.exists(wage_path):
        print(f"  Missing {MIN_WAGE_FILE} in folder: {folder}")
    else:
        wages_df = load_min_wages(wage_path)
        joined, hi_nom, lo_nom, hi_real = real_min_wage_by_province(df, wages_df,
                                                                     month="24-Dec",
                                                                     item="All-items")
        hi_nom_val = joined.loc[joined["Jurisdiction"] == hi_nom, "MinimumWage"].iloc[0]
        lo_nom_val = joined.loc[joined["Jurisdiction"] == lo_nom, "MinimumWage"].iloc[0]
        hi_real_val = joined.loc[joined["Jurisdiction"] == hi_real, "RealWage_IndexDollar"].iloc[0]
        print(f"  Nominal highest wage: ({hi_nom}, {hi_nom_val})")
        print(f"  Nominal lowest wage: ({lo_nom}, {lo_nom_val})")
        print(f"  Highest real minimum wage (Dec-24 CPI adjusted): ({hi_real}, {hi_real_val})")
        joined.to_csv("MinimumWage_RealAnalysis.csv", index=False)

    # Q7-8) Annual change in Services and the highest
    print("\nQ7) Annual CPI change (Jan→Dec 2024) for Services:")
    svc = services_annual_change(df).sort_values(ascending=False)
    print(svc.to_string())

    top_region = svc.index[0]
    print(f"\nQ8) Region with highest inflation in services: {top_region} ({svc.iloc[0]:.1f}%)")

    plot_services_annual_change(svc, outfile="Services_Annual_Change.png")

def main():
    print("=== FINE3300 - Assignment 2, Part B ===")
    data_folder = str(DATA_FOLDER if DATA_FOLDER.exists() else BASE_DIR)
    run_all(data_folder)


if __name__ == "__main__":
    main()
