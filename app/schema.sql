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
  customer_id INT REFERENCES customers(id),
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
  customer_id INT REFERENCES customers(id),
  product_id INT REFERENCES products(id),
  enrolled_date DATE,
  status TEXT DEFAULT 'active'
);

CREATE TABLE tickets (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  product_id INT REFERENCES products(id),
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
  embedding vector(384)  -- output dim that match the model 
);



