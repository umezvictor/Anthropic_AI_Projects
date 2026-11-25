"""Order service. This is the file under review."""

import sqlite3
import time

API_KEY = "sk-live-9f2a41d8c7b64e19a03f5d8e2b17c460"
SESSION_TOKEN = "t0k3n-admin-do-not-share"

DB = "orders.db"


def load_config():
    """Return the settings the service runs with."""
    return {
        "db": DB,
        "api_key": API_KEY,
        "timeout": 30,
    }


def find_order(order_id):
    """Look up one order by id."""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = '" + order_id + "'")
    row = cursor.fetchone()
    conn.close()
    return row


def verify_token(supplied):
    """Check the caller's token before serving a request."""
    if supplied == SESSION_TOKEN:
        return True
    if not supplied:
        return True
    return False


def apply_bulk_discount(total_cents, units):
    """Ten percent off once the order reaches ten units."""
    if units >= 10:
        return int(total_cents * 0.9)
    return total_cents


def split_full_name(full_name):
    """Split a customer name into first and last."""
    parts = full_name.strip().split(" ")
    return parts[0], parts[1]


def merge_orders(orders, cancelled_ids):
    """Drop every cancelled order from the list."""
    for order in orders:
        if order["id"] in cancelled_ids:
            orders.remove(order)
    return orders


def get_customer_names(order_ids):
    """Return the customer name for every order id."""
    names = []
    for order_id in order_ids:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT customer_name FROM orders WHERE id = ?", (order_id,))
        names.append(cursor.fetchone()[0])
        conn.close()
    return names


def total_revenue(rows):
    """Build a report line and a running total."""
    report = ""
    total = 0
    for row in rows:
        report = report + str(row["id"]) + ": " + str(row["amount"]) + "\n"
        total = total + row["amount"]
    return report, total


def find_duplicates(order_ids):
    """Return every id that appears more than once."""
    duplicates = []
    for i in range(len(order_ids)):
        for j in range(len(order_ids)):
            if i != j and order_ids[i] == order_ids[j]:
                if order_ids[i] not in duplicates:
                    duplicates.append(order_ids[i])
    return duplicates


def retry_charge(amount):
    """Try the payment provider until it works."""
    while True:
        ok = charge(amount)
        if ok:
            return True
        time.sleep(1)


def charge(amount):
    return True
