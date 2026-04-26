CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT,
  region TEXT,
  joined_date DATE
);

CREATE TABLE logins (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
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
  customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
  product_id INT REFERENCES products(id) ON DELETE CASCADE,
  enrolled_date DATE,
  status TEXT DEFAULT 'active'
);

CREATE TABLE tickets (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
  product_id INT REFERENCES products(id) ON DELETE CASCADE,
  category TEXT,
  issue TEXT,
  status TEXT,
  priority TEXT DEFAULT 'medium',  -- low, medium, high, critical
  created_at TIMESTAMP,
  resolved_at TIMESTAMP,
  assigned_to TEXT,
  app_version TEXT  -- Track which app version when ticket was created
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

-- pgvector index for cosine similarity search
CREATE INDEX IF NOT EXISTS idx_kb_embeddings_embedding
ON kb_embeddings USING ivfflat (embedding vector_cosine_ops);


