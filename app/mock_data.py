import random, datetime
from faker import Faker
from sqlalchemy import create_engine, text
from app.config import settings

fake = Faker()
engine = create_engine(settings.DATABASE_URL)

def generate_mock_data():
    with engine.begin() as conn:
        conn.execute(text(open("app/schema.sql").read()))

        # Insert customers
        for _ in range(100):
            conn.execute(
                text("INSERT INTO customers (name, email, region, joined_date) VALUES (:n, :e, :r, :d)"),
                {"n": fake.name(), "e": fake.email(), "r": fake.country(), "d": fake.date_this_decade()},
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
                    text("INSERT INTO customer_products (customer_id, product_id, enrolled_date, status) VALUES (:cid, :pid, :ed, :status)"),
                    {
                        "cid": cid,
                        "pid": pid,
                        "ed": fake.date_between(start_date='-2y', end_date='today'),
                        "status": random.choice(["active", "active", "active", "suspended"]),  # 75% active
                    },
                )

        # Tickets - Simulate v1.2 release spike scenario
        categories = ["App Crash", "Login Fail", "Slow Transaction", "Payment Error", "Notification Delay", "UI Confusion", "Mobile Deposit Issue"]
        priorities = ["low", "medium", "high", "critical"]
        agents = ["Agent_A", "Agent_B", "Agent_C", "Agent_D", "Agent_E"]
        
        # Pre-v1.2 tickets (Jan 1-14): Normal volume ~10/day
        from datetime import datetime, timedelta
        v12_release = datetime(2025, 1, 15)
        
        # Jan 1-14: 140 tickets (baseline)
        for day in range(14):
            date = datetime(2025, 1, 1) + timedelta(days=day)
            tickets_per_day = random.randint(8, 12)  # Normal volume
            
            for _ in range(tickets_per_day):
                created = date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
                status = random.choice(["open", "closed", "closed", "closed"])  # 75% closed
                
                ticket = {
                    "cid": random.randint(1, 100),
                    "pid": random.randint(1, len(products)),
                    "cat": random.choice(["App Crash", "Login Fail", "Slow Transaction", "Payment Error"]),
                    "issue": fake.sentence(),
                    "status": status,
                    "priority": random.choice(["low", "medium", "medium", "high"]),
                    "created": created,
                    "resolved": created + timedelta(hours=random.randint(1, 6)) if status == "closed" else None,
                    "agent": random.choice(agents),
                    "version": "v1.1"
                }
                
                conn.execute(
                    text("""INSERT INTO tickets (customer_id, product_id, category, issue, status, priority, created_at, resolved_at, assigned_to, app_version)
                            VALUES (:cid, :pid, :cat, :issue, :status, :priority, :created, :resolved, :agent, :version)"""),
                    ticket
                )
        
        # Jan 15-25: POST v1.2 SPIKE - 35% increase + new issue types
        for day in range(11):  # 10 days post-release
            date = v12_release + timedelta(days=day)
            tickets_per_day = random.randint(16, 22)  # 35-50% increase
            
            for _ in range(tickets_per_day):
                created = date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
                
                # Higher proportion of new v1.2 specific issues
                if day < 3:  # First 3 days: lots of new issues
                    cat = random.choice(["Notification Delay", "UI Confusion", "Mobile Deposit Issue", 
                                       "App Crash", "Login Fail", "Slow Transaction"])
                else:  # Stabilizing
                    cat = random.choice(categories)
                
                status = random.choice(["open", "open", "closed", "closed"])  # More open tickets initially
                
                ticket = {
                    "cid": random.randint(1, 100),
                    "pid": random.randint(1, len(products)),
                    "cat": cat,
                    "issue": fake.sentence(),
                    "status": status,
                    "priority": random.choice(["low", "medium", "medium", "high", "high"]),  # More high priority
                    "created": created,
                    "resolved": created + timedelta(hours=random.randint(2, 8)) if status == "closed" else None,
                    "agent": random.choice(agents),
                    "version": "v1.2"
                }
                
                conn.execute(
                    text("""INSERT INTO tickets (customer_id, product_id, category, issue, status, priority, created_at, resolved_at, assigned_to, app_version)
                            VALUES (:cid, :pid, :cat, :issue, :status, :priority, :created, :resolved, :agent, :version)"""),
                    ticket
                )
