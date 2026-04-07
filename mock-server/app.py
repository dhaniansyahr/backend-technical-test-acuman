import json
import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.json")


def load_customers():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/customers", methods=["GET"])
def get_customers():
    customers = load_customers()

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    page = max(1, page)
    limit = max(1, min(limit, 100))

    total = len(customers)
    start = (page - 1) * limit
    end = start + limit
    paginated = customers[start:end]

    return jsonify({
        "data": paginated,
        "total": total,
        "page": page,
        "limit": limit,
    })


@app.route("/api/customers/<string:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customers = load_customers()

    customer = next(
        (c for c in customers if c["customer_id"] == customer_id), None
    )

    if customer is None:
        abort(404, description=f"Customer '{customer_id}' not found")

    return jsonify({"data": customer})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error.description)}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
