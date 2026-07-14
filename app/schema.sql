CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT,
  region TEXT,
  joined_date DATE,
  age INT,
  income DECIMAL(10,2),
  occupation TEXT,
  phone TEXT
);

CREATE TABLE logins (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
  last_login TIMESTAMP,
  login_count INT
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT,
  category TEXT
);

CREATE TABLE customer_products (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
  product_id INT REFERENCES products(id) ON DELETE SET NULL,
  enrolled_date DATE,
  status TEXT DEFAULT 'active'
);

CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
  product_id INT REFERENCES products(id) ON DELETE SET NULL,
  amount DECIMAL(12,2),
  type TEXT,
  method TEXT,
  description TEXT,
  created_at TIMESTAMP,
  status TEXT DEFAULT 'completed'
);

CREATE TABLE tickets (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
  product_id INT REFERENCES products(id) ON DELETE SET NULL,
  category TEXT,
  issue TEXT,
  status TEXT,
  priority TEXT DEFAULT 'medium',  -- low, medium, high, critical
  created_at TIMESTAMP,
  resolved_at TIMESTAMP,
  assigned_to TEXT,
  app_version TEXT  -- Track which app version when ticket was created
);

CREATE TABLE escalations (
  id SERIAL PRIMARY KEY,
  ticket_id INT REFERENCES tickets(id) ON DELETE SET NULL,
  escalated_to TEXT,
  reason TEXT,
  escalated_at TIMESTAMP,
  resolved_at TIMESTAMP
);

CREATE TABLE kb_embeddings (
  id SERIAL PRIMARY KEY,
  doc_name TEXT,
  content TEXT,
  embedding vector(1024)  -- Jina jina-embeddings-v3 default dim; must match app.config JINA_EMBEDDING_DIMENSION
);

-- Performance indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_product_id ON tickets(product_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_app_version ON tickets(app_version);

CREATE INDEX IF NOT EXISTS idx_logins_customer_id ON logins(customer_id);

CREATE INDEX IF NOT EXISTS idx_customer_products_customer_id ON customer_products(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_products_product_id ON customer_products(product_id);
CREATE INDEX IF NOT EXISTS idx_customer_products_status ON customer_products(status);

CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

CREATE INDEX IF NOT EXISTS idx_escalations_ticket_id ON escalations(ticket_id);

-- pgvector index for cosine similarity search
CREATE INDEX IF NOT EXISTS idx_kb_embeddings_embedding
ON kb_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Request audit log
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    question TEXT,
    tool_used TEXT,
    latency_ms INT,
    success BOOLEAN,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_request_logs_created ON request_logs(created_at);


