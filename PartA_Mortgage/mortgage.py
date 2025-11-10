#FINE3300 - Assignment 1 (Part 1)
#MortgagePayment class + user prompts
#The program asks for principal, quoted annual rate (5), and amortization years
#and prints all required payment options.

class MortgagePayment:
    def __init__ (self, quoted_rate_percent, years):
        # Store nominal quoted annual rate (semi-annual compounding, per Canadian convention)
        self.nominal_rate = quoted_rate_percent / 100
        self.years = years

    def _periodic_rate(self, payments_per_year):
        # Convert semi-annual compounding to an effective annual rate
        semi = self.nominal_rate / 2
        effective_annual = (1 + semi) ** 2 - 1
        # Then convert to the periodic rate for the chosen payment frequency
        return (1 + effective_annual) ** (1 / payments_per_year) - 1
    
    def _payment(self, principal, payments_per_year):
        r = self._periodic_rate(payments_per_year)
        n = self.years * payments_per_year
        # Present value of an annuity factor
        pvaf = (1 - (1 + r) ** (-n)) / r
        return principal / pvaf
    
    def payments(self, principal):
        monthly = self._payment(principal, 12)
        semi_monthly = self._payment(principal, 24)
        bi_weekly = self._payment(principal, 26)
        weekly = self._payment(principal, 52)

        # Accelerated / Rapid payments
        rapid_biweekly = monthly / 2
        rapid_weekly = monthly / 4

        return tuple(round(x, 2) for x in
                     (monthly, semi_monthly, bi_weekly, weekly, rapid_biweekly, rapid_weekly))
    
if __name__ == "__main__":
    principal = float(input("Enter the mortgage principal ($): "))
    rate = float(input("Enter the quoted annual rate (%): "))
    years = int(input("Enter the amortization period (years): "))

    mortgage = MortgagePayment(rate, years)
    monthly, semi_monthly, bi_weekly, weekly, rapid_biweekly, rapid_weekly = mortgage.payments(principal)

def run_mortgage():
    print("\nMortgage payment options:")
    print(f"Monthly Payment: ${monthly}")
    print(f"Semi-monthly Payment: ${semi_monthly}")
    print(f"Bi-weekly Payment: ${bi_weekly}")
    print(f"Weekly Payment: ${weekly}")
    print(f"Rapid Bi-weekly Payment: ${rapid_biweekly}")
    print(f"Rapid Weekly Payment: ${rapid_weekly}")

# ------------------------------
# Assignment 1 Above
# ------------------------------

from typing import Dict, List, TypedDict


class ScheduleRow(TypedDict):
    Period: int
    StartBalance: float
    Interest: float
    Payment: float
    EndBalance: float

def periods_per_year(name: str) -> int:
    """Payment frequency → periods per year."""
    return {
        "Monthly": 12,
        "SemiMonthly": 24,
        "BiWeekly": 26,
        "Weekly": 52,
        "RapidBiWeekly": 26,  # same timing as bi-weekly; payment = half monthly
        "RapidWeekly": 52,    # same timing as weekly;  payment = quarter monthly
    }[name]

def payment_amounts(mortgage: MortgagePayment, principal: float) -> Dict[str, float]:
    """
    Use Assignment 1's .payments(principal) to get the six amounts in order.
    Returns a dict keyed by plan name.
    """
    monthly, semi_m, bi_w, weekly, rapid_bi, rapid_w = mortgage.payments(principal)
    return {
        "Monthly": monthly,
        "SemiMonthly": semi_m,
        "BiWeekly": bi_w,
        "Weekly": weekly,
        "RapidBiWeekly": rapid_bi,
        "RapidWeekly": rapid_w,
    }

def periodic_rate_for(mortgage: MortgagePayment, plan_name: str) -> float:
    """
    Use Assignment 1's periodic rate conversion (semi-annual quoted → effective periodic).
    """
    ppy = periods_per_year(plan_name)
    return mortgage._periodic_rate(ppy)

def build_schedule(
    mortgage: MortgagePayment,
    principal: float,
    term_years: int,
    plan_name: str,
    pay_amounts: Dict[str, float],
    force_payoff: bool = False,
) -> List[ScheduleRow]:
    """
    Build a schedule (list of dict rows) for one plan.
    Columns: Period, StartBalance, Interest, Payment, EndBalance
    Set force_payoff=True to guarantee the last row finishes at $0.
    """
    r = periodic_rate_for(mortgage, plan_name)
    n_term = term_years * periods_per_year(plan_name)
    pay = pay_amounts[plan_name]

    rows = []
    bal = float(principal)

    t = 1
    while t <= n_term:
        start = bal
        interest = start * r
        payment = pay
        end = start + interest - payment
        is_final_period = t == n_term

        # Prevent drift: adjust final payment if we overshoot or still owe a few dollars.
        if end < 0 or (force_payoff and is_final_period and end > 0):
            payment = start + interest
            end = 0.0

        rows.append(
            ScheduleRow(
                Period=t,
                StartBalance=round(start, 2),
                Interest=round(interest, 2),
                Payment=round(payment, 2),
                EndBalance=round(end, 2),
            )
        )

        bal = end
        t += 1

    return rows
