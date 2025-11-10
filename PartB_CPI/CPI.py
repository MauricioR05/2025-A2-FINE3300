# cpi.py
# FINE3300 - Assignment 2, Part B (Data/Logic)
# Reads CPI CSVs (2024 monthly) for Canada + provinces, plus MinimumWages.csv
# Produces combined tidy DataFrame and required computations.

from __future__ import annotations
import os
from typing import List, Dict, Tuple
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

# ---- Configuration / helpers ----

PROVINCE_NAME = {
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "ON": "Ontario",
    "PEI": "Prince Edward Island",
    "QC": "Quebec",
    "SK": "Saskatchewan",
    "CANADA": "Canada",
}

# expected file name patterns (you can put the files in the same folder as this script)
DEFAULT_FILES = [
    ("Canada", "Canada.CPI.1810000401.csv"),
    ("Alberta", "AB.CPI.1810000401.csv"),
    ("British Columbia", "BC.CPI.1810000401.csv"),
    ("Manitoba", "MB.CPI.1810000401.csv"),
    ("New Brunswick", "NB.CPI.1810000401.csv"),
    ("Newfoundland and Labrador", "NL.CPI.1810000401.csv"),
    ("Nova Scotia", "NS.CPI.1810000401.csv"),
    ("Ontario", "ON.CPI.1810000401.csv"),
    ("Prince Edward Island", "PEI.CPI.1810000401.csv"),
    ("Quebec", "QC.CPI.1810000401.csv"),
    ("Saskatchewan", "SK.CPI.1810000401.csv"),
]

MONTH_ORDER = ["24-Jan","24-Feb","24-Mar","24-Apr","24-May","24-Jun",
               "24-Jul","24-Aug","24-Sep","24-Oct","24-Nov","24-Dec"]

ITEMS_FOR_AVG_CHANGE = [
    "Food",
    "Shelter",
    "All-items excluding food and energy",
]

def _melt_one(df: pd.DataFrame, jurisdiction: str) -> pd.DataFrame:
    """
    Input wide dataframe like:
      Item, 24-Jan, 24-Feb, ..., 24-Dec
    Output long tidy:
      Item, Month, Jurisdiction, CPI
    """
    # Keep only known month columns plus "Item"
    keep_cols = ["Item"] + [m for m in MONTH_ORDER if m in df.columns]
    df2 = df[keep_cols].copy()

    long_df = df2.melt(id_vars=["Item"],
                       value_vars=[c for c in df2.columns if c != "Item"],
                       var_name="Month",
                       value_name="CPI")
    long_df["Jurisdiction"] = jurisdiction
    # Ensure CPI numeric
    long_df["CPI"] = pd.to_numeric(long_df["CPI"], errors="coerce")
    # Order months
    long_df["Month"] = pd.Categorical(long_df["Month"],
                                      categories=MONTH_ORDER,
                                      ordered=True)
    return long_df[["Item","Month","Jurisdiction","CPI"]]


def read_cpi_file(path: str, jurisdiction: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return _melt_one(df, jurisdiction)


def combine_cpi(files: List[Tuple[str,str]], folder: str = ".") -> pd.DataFrame:
    """
    files: list of (Jurisdiction, filename)
    folder: directory where CSVs live
    """
    frames = []
    for jur, fname in files:
        full = os.path.join(folder, fname)
        if not os.path.exists(full):
            raise FileNotFoundError(f"Missing file: {full}")
        frames.append(read_cpi_file(full, jur))
    out = pd.concat(frames, ignore_index=True)
    # Sort
    out = out.sort_values(["Item","Jurisdiction","Month"]).reset_index(drop=True)
    return out


def print_first_rows(df: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    """Return first n rows to display/print upstream."""
    return df.head(n)


def average_month_to_month_change(df: pd.DataFrame,
                                  items: List[str]) -> pd.DataFrame:
    """
    For Canada and each province, compute avg month-to-month % change
    for each requested Item over 2024 (Feb..Dec vs prior month).
    Returns a DataFrame indexed by Jurisdiction with columns per Item.
    """
    # Filter to items of interest
    dfi = df[df["Item"].isin(items)].copy()
    # For each Jurisdiction+Item, sort by Month and compute pct change
    dfi = dfi.sort_values(["Jurisdiction","Item","Month"])
    pct = dfi.groupby(["Jurisdiction","Item"])["CPI"].pct_change() * 100.0
    dfi = dfi.assign(pct_change=pct)

    # Exclude first month (NaN change), average the rest
    avg = dfi.groupby(["Jurisdiction","Item"])["pct_change"].mean().unstack("Item")
    # Round to 1 decimal
    avg = avg.round(1)
    return avg


def highest_avg_change(summary: pd.DataFrame) -> pd.Series:
    """
    From the summary table (Jurisdiction x Item), compute which province
    had the highest avg change for each Item. Returns a Series indexed by Item
    with Jurisdiction names as values.
    """
    return summary.idxmax()


def equivalent_salary(df: pd.DataFrame,
                      base_jurisdiction: str = "Ontario",
                      base_amount: float = 100000.0,
                      month: str = "24-Dec",
                      item: str = "All-items") -> pd.DataFrame:
    """
    Using All-items CPI (Dec 2024), compute salary equivalents so that real
    purchasing power matches the base jurisdiction’s $100,000 (default Ontario).
    Formula: Salary_P = base_amount * (CPI_P / CPI_base)
    """
    base_cpi = df[(df["Jurisdiction"] == base_jurisdiction) &
                  (df["Item"] == item) &
                  (df["Month"] == month)]["CPI"].iloc[0]

    dec = df[(df["Item"] == item) & (df["Month"] == month)]
    dec = dec[["Jurisdiction","CPI"]].drop_duplicates()
    dec["Equivalent Salary"] = base_amount * (dec["CPI"] / base_cpi)
    dec["Equivalent Salary"] = dec["Equivalent Salary"].round(2)
    dec["CPI"] = dec["CPI"].round(1)
    out = dec.sort_values("Equivalent Salary", ascending=False).reset_index(drop=True)
    return out


def load_min_wages(path: str) -> pd.DataFrame:
    """
    Expect a CSV with at least: Jurisdiction (province names) and MinimumWage (nominal).
    If your CSV has different column names, tweak mapping below.
    """
    w = pd.read_csv(path)
    # Try to standardize likely column names
    cols = {c.lower(): c for c in w.columns}
    # Heuristics
    jcol = cols.get("jurisdiction") or cols.get("province") or cols.get("region") or list(w.columns)[0]
    wcol = cols.get("minimumwage") or cols.get("minwage") or cols.get("wage") or list(w.columns)[1]
    w2 = w.rename(columns={jcol: "Jurisdiction", wcol: "MinimumWage"})
    w2["Jurisdiction"] = w2["Jurisdiction"].apply(
        lambda val: PROVINCE_NAME.get(str(val).upper(), val)
    )
    return w2[["Jurisdiction","MinimumWage"]]


def real_min_wage_by_province(df: pd.DataFrame,
                              wages_df: pd.DataFrame,
                              month: str = "24-Dec",
                              item: str = "All-items") -> Tuple[pd.DataFrame, str, str, str]:
    """
    Compute nominal highest/lowest and highest real minimum wage (using Dec All-items CPI).
    Real wage ~ nominal / CPI (rank consistent up to a constant base).
    Returns (joined DataFrame, highest_nominal, lowest_nominal, highest_real)
    """
    # Dec CPI per Jurisdiction
    dec = df[(df["Item"] == item) & (df["Month"] == month)][["Jurisdiction","CPI"]].drop_duplicates()
    j = wages_df.merge(dec, on="Jurisdiction", how="left")
    j["RealWage_IndexDollar"] = j["MinimumWage"] * 100.0 / j["CPI"]

    # Identify winners
    highest_nominal = j.sort_values("MinimumWage", ascending=False)["Jurisdiction"].iloc[0]
    lowest_nominal = j.sort_values("MinimumWage", ascending=True)["Jurisdiction"].iloc[0]
    highest_real = j.sort_values("RealWage_IndexDollar", ascending=False)["Jurisdiction"].iloc[0]

    j = j.sort_values("Jurisdiction").reset_index(drop=True)
    j["MinimumWage"] = j["MinimumWage"].round(2)
    j["RealWage_IndexDollar"] = j["RealWage_IndexDollar"].round(2)

    return j, highest_nominal, lowest_nominal, highest_real


def services_annual_change(df: pd.DataFrame) -> pd.Series:
    """
    Compute annual % change for Services in 2024 as (Dec - Jan) / Jan * 100.
    Returns Series indexed by Jurisdiction.
    """
    jan = df[(df["Item"] == "Services") & (df["Month"] == "24-Jan")][["Jurisdiction","CPI"]].set_index("Jurisdiction")
    dec = df[(df["Item"] == "Services") & (df["Month"] == "24-Dec")][["Jurisdiction","CPI"]].set_index("Jurisdiction")
    aligned = jan.join(dec, lsuffix="_Jan", rsuffix="_Dec").dropna()
    out = (aligned["CPI_Dec"] - aligned["CPI_Jan"]) / aligned["CPI_Jan"] * 100.0
    return out.round(1)


def plot_services_annual_change(series: pd.Series, outfile: str = "Services_Annual_Change.png") -> None:
    """
    Save a simple bar chart of annual Services inflation by jurisdiction.
    """
    plt.figure()
    series.sort_values(ascending=False).plot(kind="bar")
    plt.title("Annual CPI Change (2024) - Services")
    plt.ylabel("Percent")
    plt.xlabel("Jurisdiction")
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
