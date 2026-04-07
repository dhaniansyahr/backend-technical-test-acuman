from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models.customer import Customer
from services.ingestion import fetch_all_customers, upsert_customers

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Pipeline Service")


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    try:
        customers = fetch_all_customers()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from mock server: {str(e)}",
        )

    try:
        count = upsert_customers(db, customers)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upsert data into database: {str(e)}",
        )

    return {"status": "success", "records_processed": count}


@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = (
        db.query(Customer)
        .order_by(Customer.customer_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "data": [c.to_dict() for c in customers],
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = (
        db.query(Customer).filter(Customer.customer_id == customer_id).first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404, detail=f"Customer '{customer_id}' not found"
        )

    return {"data": customer.to_dict()}
