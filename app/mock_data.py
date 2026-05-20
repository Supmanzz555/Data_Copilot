import random, datetime
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import text
from app.database import engine

fake = Faker()

OCCUPATIONS = [
    "Engineer", "Teacher", "Nurse", "Shop Owner", "Accountant",
    "Software Developer", "Driver", "Civil Servant", "Retail Worker",
    "Hotel Staff", "Restaurant Manager", "Doctor", "Lawyer", "Farmer",
    "Freelancer", "Student", "Flight Attendant", "Police Officer",
]

REALISTIC_ISSUES = {
    "App Crash": [
        "App crashes when viewing transaction history on older devices",
        "App closes immediately after opening on startup",
        "App freezes during navigation to Digital Lending page",
        "App crashes when trying to upload documents for loan application",
        "App crashes on iPhone 12 when opening monthly statement",
        "App repeatedly crashes after 2 minutes of use",
        "White screen appears after login, app becomes unresponsive",
    ],
    "Login Fail": [
        "Password rejected despite correct credentials after app update",
        "Account locked after 3 failed login attempts, need immediate unlock",
        "Face ID not working after app update, forced password re-entry",
        "Forgot password reset email not arriving in inbox",
        "Biometric authentication fails after iOS update",
        "Cannot login on new phone, SMS verification not sent",
        "Account shows locked after automatic logout from v1.2 update",
    ],
    "Slow Transaction": [
        "Transfer showing pending for over 30 minutes to other bank",
        "Transaction status stuck on processing after 1 hour",
        "Payment delayed, money deducted but beneficiary not credited",
        "International transfer not reflected after 3 business days",
        "Auto-debit for loan repayment showing pending for 2 days",
        "Deposit via PromptPay not credited to account after 2 hours",
        "Transfer between own accounts taking more than 10 minutes",
    ],
    "Payment Error": [
        "Payment failed with insufficient balance error despite sufficient funds",
        "QR code payment declined at 7-Eleven counter with sufficient balance",
        "International transfer rejected due to daily limit miscalculation",
        "Loan repayment payment deducted twice from account",
        "Standing order not executed on scheduled date",
        "Transaction failed with generic error code, no details provided",
        "Card payment at merchant declined due to unknown reason",
    ],
    "Notification Delay": [
        "Loan approval notification not received, checked app manually after 6 hours",
        "Deposit confirmation email delayed by 45 minutes after transaction",
        "Push notifications not arriving for transactions since v1.2 update",
        "EMI reminder notification not received 3 days before due date",
        "Login alert notification came 2 hours after the actual login",
        "Transaction OTP SMS delayed by over 10 minutes",
    ],
    "UI Confusion": [
        "Cannot find mobile deposit feature after v1.2 update, menu reorganized",
        "New dashboard layout confusing, unable to locate account balance",
        "Dark mode toggle not working on Android phone",
        "Navigation menu changed, cannot find transaction history anymore",
        "Font size too small after update, accessibility settings do not help",
        "Search function not finding products that exist under different category",
    ],
    "Mobile Deposit Issue": [
        "Check image rejected due to poor lighting, unclear what acceptable quality is",
        "Camera will not focus on check, all 4 corners not visible in frame",
        "Mobile deposit rejected, check older than 6 months not accepted",
        "Deposit confirmation not received after successful check scan",
        "Cannot capture check image on iPhone 14 Pro Max, camera glitch",
        "Mobile deposit limit warning unclear, amount exceeds daily limit",
        "Check endorsement required but no clear instruction in app",
    ],
}

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_mock_data():
    with engine.begin() as conn:
        conn.execute(text(open("app/schema.sql").read()))

        # Insert customers with demographics
        for _ in range(100):
            age = random.randint(18, 75)
            income = random.choice([
                random.randint(15000, 50000),
                random.randint(50001, 100000),
                random.randint(100001, 200000),
            ])
            conn.execute(
                text("""INSERT INTO customers (name, email, region, joined_date, age, income, occupation, phone)
                        VALUES (:n, :e, :r, :d, :age, :inc, :occ, :ph)"""),
                {
                    "n": fake.name(),
                    "e": fake.email(),
                    "r": fake.country(),
                    "d": fake.date_this_decade(),
                    "age": age,
                    "inc": income,
                    "occ": random.choice(OCCUPATIONS),
                    "ph": fake.phone_number(),
                },
            )

        # Products
        products = ["Digital Saving", "Digital Lending", "Investment", "Insurance"]
        for p in products:
            conn.execute(text("INSERT INTO products (name, category) VALUES (:n, :c)"), {"n": p, "c": "Finance"})

        # Logins
        for cid in range(1, 101):
            conn.execute(
                text("INSERT INTO logins (customer_id, last_login, login_count) VALUES (:cid, :ll, :lc)"),
                {
                    "cid": cid,
                    "ll": fake.date_time_this_year(),
                    "lc": random.randint(1, 500),
                },
            )

        # Customer Products (each customer has 1-3 products)
        for cid in range(1, 101):
            num_products = random.randint(1, 3)
            product_ids = random.sample(range(1, len(products) + 1), num_products)
            for pid in product_ids:
                conn.execute(
                    text("""INSERT INTO customer_products (customer_id, product_id, enrolled_date, status)
                            VALUES (:cid, :pid, :ed, :status)"""),
                    {
                        "cid": cid,
                        "pid": pid,
                        "ed": fake.date_between(start_date='-2y', end_date='today'),
                        "status": random.choice(["active", "active", "active", "suspended"]),
                    },
                )

        # Transactions (800 rows across 13 months)
        tx_types = ["deposit", "withdrawal", "transfer", "payment"]
        tx_methods = ["PromptPay", "app_transfer", "ATM", "counter", "auto_debit"]
        tx_statuses = ["completed", "completed", "completed", "completed", "completed",
                       "completed", "completed", "completed", "pending", "failed"]
        tx_start = datetime(2024, 1, 1)
        tx_end = datetime(2025, 1, 31)

        for _ in range(800):
            cid = random.randint(1, 100)
            pid = random.randint(1, len(products))
            amount = random.choice([
                random.randint(100, 10000),
                random.randint(10001, 100000),
                random.randint(100001, 500000),
            ])
            conn.execute(
                text("""INSERT INTO transactions (customer_id, product_id, amount, type, method, description, created_at, status)
                        VALUES (:cid, :pid, :amt, :type, :method, :desc, :ca, :status)"""),
                {
                    "cid": cid,
                    "pid": pid,
                    "amt": amount,
                    "type": random.choice(tx_types),
                    "method": random.choices(tx_methods, weights=[40, 30, 10, 10, 10])[0],
                    "desc": fake.sentence(),
                    "ca": random_date(tx_start, tx_end),
                    "status": random.choice(tx_statuses),
                },
            )

        # Tickets with realistic issues
        categories = ["App Crash", "Login Fail", "Slow Transaction", "Payment Error",
                      "Notification Delay", "UI Confusion", "Mobile Deposit Issue"]
        priorities = ["low", "medium", "high", "critical"]
        agents = ["Agent_A", "Agent_B", "Agent_C", "Agent_D", "Agent_E"]
        v12_release = datetime(2025, 1, 15)

        # Pre-v1.2 tickets (Jan 1-14): Baseline volume
        v11_categories = ["App Crash", "Login Fail", "Slow Transaction", "Payment Error"]
        for day in range(14):
            date = datetime(2025, 1, 1) + timedelta(days=day)
            tickets_per_day = random.randint(8, 12)

            for _ in range(tickets_per_day):
                created = date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
                cat = random.choice(v11_categories)
                status = random.choice(["open", "closed", "closed", "closed"])

                conn.execute(
                    text("""INSERT INTO tickets (customer_id, product_id, category, issue, status, priority, created_at, resolved_at, assigned_to, app_version)
                            VALUES (:cid, :pid, :cat, :issue, :status, :priority, :created, :resolved, :agent, :version)"""),
                    {
                        "cid": random.randint(1, 100),
                        "pid": random.randint(1, len(products)),
                        "cat": cat,
                        "issue": random.choice(REALISTIC_ISSUES[cat]),
                        "status": status,
                        "priority": random.choice(["low", "medium", "medium", "high"]),
                        "created": created,
                        "resolved": created + timedelta(hours=random.randint(1, 6)) if status == "closed" else None,
                        "agent": random.choice(agents),
                        "version": "v1.1",
                    },
                )

        # Post-v1.2 tickets (Jan 15-25): Spike + new issue types
        for day in range(11):
            date = v12_release + timedelta(days=day)
            tickets_per_day = random.randint(16, 22)

            for _ in range(tickets_per_day):
                created = date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))

                if day < 3:
                    cat = random.choice(["Notification Delay", "UI Confusion", "Mobile Deposit Issue",
                                       "App Crash", "Login Fail", "Slow Transaction"])
                else:
                    cat = random.choice(categories)

                status = random.choice(["open", "open", "closed", "closed"])

                conn.execute(
                    text("""INSERT INTO tickets (customer_id, product_id, category, issue, status, priority, created_at, resolved_at, assigned_to, app_version)
                            VALUES (:cid, :pid, :cat, :issue, :status, :priority, :created, :resolved, :agent, :version)"""),
                    {
                        "cid": random.randint(1, 100),
                        "pid": random.randint(1, len(products)),
                        "cat": cat,
                        "issue": random.choice(REALISTIC_ISSUES.get(cat, REALISTIC_ISSUES["App Crash"])),
                        "status": status,
                        "priority": random.choice(["low", "medium", "medium", "high", "high"]),
                        "created": created,
                        "resolved": created + timedelta(hours=random.randint(2, 8)) if status == "closed" else None,
                        "agent": random.choice(agents),
                        "version": "v1.2",
                    },
                )

        # Escalations (15-20% of tickets)
        escalation_reasons = [
            "Requires engineering investigation",
            "Customer requested manager escalation",
            "Potential security issue needs compliance review",
            "Complex issue beyond L1 scope",
            "Regulatory compliance concern",
            "Multiple failed resolution attempts",
            "High-value transaction dispute",
        ]
        escalation_teams = ["L2_Support", "Engineering", "Compliance", "Security"]

        total_tickets = conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar()
        escalation_count = int(total_tickets * random.uniform(0.15, 0.20))

        ticket_ids = list(range(1, total_tickets + 1))
        selected_tickets = random.sample(ticket_ids, min(escalation_count, total_tickets))

        for tid in selected_tickets:
            created_at = conn.execute(
                text("SELECT created_at FROM tickets WHERE id = :id"), {"id": tid}
            ).scalar()
            if created_at:
                escalated_at = created_at + timedelta(hours=random.randint(1, 48))
                resolved = random.choice([True, False])
                conn.execute(
                    text("""INSERT INTO escalations (ticket_id, escalated_to, reason, escalated_at, resolved_at)
                            VALUES (:tid, :to, :reason, :ea, :ra)"""),
                    {
                        "tid": tid,
                        "to": random.choice(escalation_teams),
                        "reason": random.choice(escalation_reasons),
                        "ea": escalated_at,
                        "ra": escalated_at + timedelta(hours=random.randint(2, 72)) if resolved else None,
                    },
                )
