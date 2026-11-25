-- Rollback: DROP TABLE orders;

CREATE TABLE orders (
    order_id      TEXT PRIMARY KEY,
    customer      TEXT NOT NULL,
    amount_cents  INTEGER NOT NULL,
    currency      TEXT NOT NULL DEFAULT 'USD',
    delivered_at  TIMESTAMP NOT NULL
);

CREATE INDEX idx_orders_customer ON orders (customer);
