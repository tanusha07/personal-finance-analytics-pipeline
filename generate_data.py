import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

START = date(2025, 12, 1)
END = date(2026, 9, 30)

rows = []


def add(d, category, description, amount):
    rows.append([d.isoformat(), category, description, round(amount, 2)])


day = START
while day <= END:
    # Paychecks (income, positive) every other Friday from three fake jobs
    if day.weekday() == 4 and ((day - START).days // 7) % 2 == 0:
        add(day, "income", "Brightside Cafe Payroll", random.uniform(350, 520))
        if random.random() < 0.6:
            add(day, "income", "Northwind Retail Payroll", random.uniform(200, 380))
        if random.random() < 0.4:
            add(day, "income", "Campus Tutoring Pay", random.uniform(120, 260))

    # Rent and phone bill
    if day.day == 1:
        add(day, "rent", "Monthly Rent", -random.uniform(850, 900))
    if day.day == 15:
        add(day, "utilities", "Phone Bill", -random.uniform(35, 45))

    # Rideshare driving income
    if random.random() < 0.35:
        add(day, "gig_income", random.choice(["Uber Driver Payout", "Lyft Driver Payout"]),
            random.uniform(40, 140))

    # Food delivery income
    if random.random() < 0.30:
        add(day, "gig_income", random.choice(["DoorDash Payout", "Uber Eats Payout"]),
            random.uniform(25, 90))

    # Groceries
    if random.random() < 0.25:
        add(day, "groceries", random.choice(["Walmart", "Publix", "Aldi", "Indian Grocery Store"]),
            -random.uniform(18, 95))

    # Gas
    if random.random() < 0.15:
        add(day, "transport", "Gas Station", -random.uniform(25, 55))

    # Eating out
    if random.random() < 0.20:
        add(day, "dining", random.choice(["Chipotle", "Local Restaurant", "Coffee Shop"]),
            -random.uniform(8, 35))

    # Friend loan repayments
    if day.day == 20 and random.random() < 0.7:
        add(day, "debt", random.choice(["Loan Repayment - Friend A", "Loan Repayment - Friend B"]),
            -random.uniform(50, 200))

    day += timedelta(days=1)

rows.sort(key=lambda r: r[0])

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_transactions.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "category", "description", "amount"])
    writer.writerows(rows)

print(f"Generated {len(rows)} fake transactions -> {out_path}")