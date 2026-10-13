-- ============================================================================
-- Default E-Commerce Schema for agentic-sql
-- Dialect: SQLite (also valid PostgreSQL with minor type adjustments)
-- Used by: schema discovery, SQL generation, validation, benchmarking
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Reference tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    city        TEXT,
    country     TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    category_id     INTEGER NOT NULL,
    price           REAL    NOT NULL CHECK (price >= 0),
    stock_quantity  INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- ----------------------------------------------------------------------------
-- Transaction tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    order_date      TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending',
    total_amount    REAL    NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    shipping_city   TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id              INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      REAL    NOT NULL CHECK (unit_price >= 0),
    line_total      REAL    NOT NULL CHECK (line_total >= 0),
    FOREIGN KEY (order_id)   REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id              INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    payment_date    TEXT    NOT NULL,
    amount          REAL    NOT NULL CHECK (amount >= 0),
    method          TEXT    NOT NULL,  -- 'credit_card', 'debit_card', 'paypal', 'cash'
    FOREIGN KEY (order_id)  REFERENCES orders(id)
);

-- ----------------------------------------------------------------------------
-- Enrichment tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    review_date TEXT    NOT NULL,
    FOREIGN KEY (product_id)  REFERENCES products(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS shipping (
    id              INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL UNIQUE,
    carrier         TEXT    NOT NULL,
    tracking_number TEXT,
    shipped_date    TEXT,
    delivered_date  TEXT,
    FOREIGN KEY (order_id)  REFERENCES orders(id)
);

-- ----------------------------------------------------------------------------
-- Indexes for query performance (cost-aware planning)
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_customer ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_shipping_order ON shipping(order_id);