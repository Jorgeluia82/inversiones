PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  phone TEXT,
  created_at TEXT,
  capital_available REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS investments (
  id INTEGER PRIMARY KEY,
  client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  company TEXT NOT NULL,
  -- NUEVO CAMPO 'category'
  category TEXT NOT NULL DEFAULT 'Volatile' CHECK(category IN ('Stable', 'Volatile', 'ETF', 'Liquidez')),
  avg_price REAL NOT NULL DEFAULT 0,
  shares REAL NOT NULL DEFAULT 0,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS cash_movements (
  id INTEGER PRIMARY KEY,
  client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  type TEXT CHECK(type IN ('DEPOSIT','WITHDRAW')) NOT NULL,
  amount REAL NOT NULL,
  note TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS investment_trades (
  id INTEGER PRIMARY KEY,
  investment_id INTEGER NOT NULL REFERENCES investments(id) ON DELETE CASCADE,
  type TEXT CHECK(type IN ('BUY','SELL','PRICE_UPDATE')) NOT NULL,
  shares REAL DEFAULT 0,
  price REAL NOT NULL,
  amount REAL NOT NULL,
  created_at TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS price_history (
  id INTEGER PRIMARY KEY,
  investment_id INTEGER NOT NULL REFERENCES investments(id) ON DELETE CASCADE,
  price REAL NOT NULL,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_cash_movements_client_date ON cash_movements(client_id, created_at);
CREATE INDEX IF NOT EXISTS idx_trades_investment_date ON investment_trades(investment_id, created_at);
CREATE INDEX IF NOT EXISTS idx_investments_client ON investments(client_id);