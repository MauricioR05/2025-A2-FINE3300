# MortgageMain.py
# Interface/runner for Assignment 2, Part A
# Uses: mortgage.MortgagePayment (from A1, unchanged) + Assignment 2 helper functions.

from typing import Dict, List
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import xlsxwriter

from mortgage import (
    MortgagePayment,
    payment_amounts,
    build_schedule,
    ScheduleRow,
)

PLAN_NAMES = ["Monthly", "SemiMonthly", "BiWeekly", "Weekly", "RapidBiWeekly", "RapidWeekly"]
SCHEDULE_COLUMNS = ["Period", "StartBalance", "Interest", "Payment", "EndBalance"]
SAMPLE_PLAN = "Monthly"


Schedules = Dict[str, List[ScheduleRow]]


def currency(value: float) -> str:
    """Return a currency string with comma separators."""
    return f"${value:,.2f}"


def prompt_float(message: str) -> float:
    """Prompt for a float until the user provides a valid number."""
    while True:
        raw = input(message)
        try:
            return float(raw)
        except ValueError:
            print(f"Invalid number '{raw}'. Please enter a numeric value.")


def prompt_int(message: str) -> int:
    """Prompt for an integer until the user provides a valid number."""
    while True:
        raw = input(message)
        try:
            return int(raw)
        except ValueError:
            print(f"Invalid whole number '{raw}'. Please enter an integer.")


def write_excel_file(schedules: Schedules, excel_path: Path) -> None:
    """Write all schedules into a single Excel workbook (one sheet per plan)."""
    with xlsxwriter.Workbook(str(excel_path)) as workbook:
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#D9D9D9", "border": 1})
        money_fmt = workbook.add_format({"num_format": "$#,##0.00"})
        number_fmt = workbook.add_format({"num_format": "0"})

        for name, rows in schedules.items():
            sheet_name = name[:31]  # Excel limit safeguard
            worksheet = workbook.add_worksheet(sheet_name)
            worksheet.write_row(0, 0, SCHEDULE_COLUMNS, header_fmt)

            for r_idx, row in enumerate(rows, start=1):
                worksheet.write_number(r_idx, 0, row["Period"], number_fmt)
                worksheet.write_number(r_idx, 1, row["StartBalance"], money_fmt)
                worksheet.write_number(r_idx, 2, row["Interest"], money_fmt)
                worksheet.write_number(r_idx, 3, row["Payment"], money_fmt)
                worksheet.write_number(r_idx, 4, row["EndBalance"], money_fmt)

            worksheet.autofilter(0, 0, max(len(rows), 1), len(SCHEDULE_COLUMNS) - 1)
            worksheet.freeze_panes(1, 0)
            worksheet.set_column("A:A", 10)
            worksheet.set_column("B:E", 16)


def plot_balances(schedules: Schedules, png_path: Path) -> None:
    """Plot ending balances over the term for every plan."""
    plt.figure()
    for name in PLAN_NAMES:
        rows = schedules[name]
        periods = [row["Period"] for row in rows]
        balances = [row["EndBalance"] for row in rows]
        plt.plot(periods, balances, label=name)
    plt.title("Loan Balance Decline (Term)")
    plt.xlabel("Period")
    plt.ylabel("Ending Balance ($)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(png_path, dpi=200)
    plt.close()


def print_sample_schedule(schedule: List[ScheduleRow], limit: int = 5) -> None:
    print("\nSample schedule (term-based, first 5 rows):")
    headers = ("Period", "Starting Balance", "Interest", "Payment", "Ending Balance")
    widths = (6, 18, 10, 10, 16)
    print(
        f"{headers[0]:>{widths[0]}} "
        f"{headers[1]:>{widths[1]}} "
        f"{headers[2]:>{widths[2]}} "
        f"{headers[3]:>{widths[3]}} "
        f"{headers[4]:>{widths[4]}}"
    )
    for row in schedule[:limit]:
        print(
            f"{row['Period']:>{widths[0]}} "
            f"{row['StartBalance']:>{widths[1]},.2f} "
            f"{row['Interest']:>{widths[2]},.2f} "
            f"{row['Payment']:>{widths[3]},.2f} "
            f"{row['EndBalance']:>{widths[4]},.2f}"
        )


def print_principal_remaining(schedules: Schedules) -> None:
    print("\nPrincipal remaining at the end of the chosen term:")
    for name in PLAN_NAMES:
        last = schedules[name][-1]
        print(f"  {name:<12}: {currency(last['EndBalance'])}")


def print_amortization_summary(full_schedules: Schedules) -> None:
    print("\nFinal row from the full amortization schedules (should be $0 balance):")
    for name in PLAN_NAMES:
        last = full_schedules[name][-1]
        print(f"  {name:<12}: Period {last['Period']:>4}, Ending Balance {currency(last['EndBalance'])}")

def main():
    print("=== FINE3300 - A2 Part A: Loan Amortization & Schedules ===")
    principal = prompt_float("Enter mortgage principal ($): ")
    rate_pct = prompt_float("Enter quoted annual rate (%): ")
    amort_years = prompt_int("Enter amortization period (years): ")
    term_years = prompt_int("Enter term (years): ")

    # Build the class from A1 (unchanged)
    m = MortgagePayment(rate_pct, amort_years)

    # Get six payment amounts once
    pays = payment_amounts(m, principal)

    # Build six schedules
    term_schedules: Schedules = {}
    for name in PLAN_NAMES:
        term_schedules[name] = build_schedule(m, principal, term_years, name, pays)

    full_amort_schedules: Schedules = {}
    for name in PLAN_NAMES:
        full_amort_schedules[name] = build_schedule(
            m, principal, m.years, name, pays, force_payoff=True
        )

    # Write one Excel file with 6 sheets (no pandas dependency)
    excel_path = Path("LoanSchedules.xlsx").resolve()
    write_excel_file(full_amort_schedules, excel_path)
    print(f"Saved Excel schedules (full amortization) -> {excel_path}")

    # Plot ending balances across the term
    png_path = Path("LoanBalanceDecline.png").resolve()
    plot_balances(term_schedules, png_path)
    print(f"Saved balance decline plot -> {png_path}")

    print_sample_schedule(term_schedules[SAMPLE_PLAN])
    print_principal_remaining(term_schedules)
    print(
        "\nPart A complete -- upload: Mortgage.py, MortgageMain.py, "
        "LoanSchedules.xlsx, LoanBalanceDecline.png"
    )

if __name__ == "__main__":
    main()
