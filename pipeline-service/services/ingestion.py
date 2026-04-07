import httpx
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models.customer import Customer

MOCK_SERVER_URL = "http://mock-server:5000"


def fetch_all_customers() -> list[dict]:
    """Fetch all customers from Flask mock server, handling pagination automatically."""
    all_customers = []
    page = 1
    limit = 50

    with httpx.Client(timeout=30.0) as client:
        while True:
            resp = client.get(
                f"{MOCK_SERVER_URL}/api/customers",
                params={"page": page, "limit": limit},
            )
            resp.raise_for_status()
            payload = resp.json()

            data = payload.get("data", [])
            total = payload.get("total", 0)

            all_customers.extend(data)

            if len(all_customers) >= total or len(data) == 0:
                break

            page += 1

    return all_customers


def upsert_customers(db: Session, customers: list[dict]) -> int:
    """Upsert customer records into PostgreSQL. Returns count of processed records."""
    if not customers:
        return 0

    records = []
    for c in customers:
        record = {
            "customer_id": c["customer_id"],
            "first_name": c["first_name"],
            "last_name": c["last_name"],
            "email": c["email"],
            "phone": c.get("phone"),
            "address": c.get("address"),
            "date_of_birth": (
                date.fromisoformat(c["date_of_birth"])
                if c.get("date_of_birth")
                else None
            ),
            "account_balance": (
                Decimal(str(c["account_balance"]))
                if c.get("account_balance") is not None
                else None
            ),
            "created_at": (
                datetime.fromisoformat(c["created_at"])
                if c.get("created_at")
                else None
            ),
        }
        records.append(record)

    stmt = pg_insert(Customer).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["customer_id"],
        set_={
            "first_name": stmt.excluded.first_name,
            "last_name": stmt.excluded.last_name,
            "email": stmt.excluded.email,
            "phone": stmt.excluded.phone,
            "address": stmt.excluded.address,
            "date_of_birth": stmt.excluded.date_of_birth,
            "account_balance": stmt.excluded.account_balance,
            "created_at": stmt.excluded.created_at,
        },
    )
    db.execute(stmt)
    db.commit()

    return len(records)
