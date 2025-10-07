import os
import sqlite3
from pathlib import Path

# La ruta a la base de datos se construye relativa a la carpeta del proyecto
# para que funcione sin importar desde dónde se ejecute el script.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_ROOT / "investments.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def run_schema(conn: sqlite3.Connection):
    # Construir la ruta al schema.sql de forma robusta
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn:
        conn.executescript(sql)

def ensure_schema_and_seed(conn: sqlite3.Connection):
    # Create schema
    run_schema(conn)
    # Seed demo
    cur = conn.execute("SELECT COUNT(*) AS c FROM clients;")
    c = cur.fetchone()["c"]
    if c == 0:
        from utils.format import now_iso
        now = now_iso()
        with conn:
            conn.execute(
                "INSERT INTO clients (name, email, phone, created_at, capital_available) VALUES (?,?,?,?,?)",
                ("Cliente Demo", "demo@example.com", "555-000-0000", now, 12000.0),
            )
            client_id = conn.execute("SELECT id FROM clients WHERE email = ?", ("demo@example.com",)).fetchone()["id"]
            # Opcional: crear inversiones ejemplo
            conn.execute(
                "INSERT INTO investments (client_id, company, avg_price, shares, created_at) VALUES (?,?,?,?,?)",
                (client_id, "ACME", 100.0, 20.0, now),
            )
            inv_id = conn.execute("SELECT id FROM investments WHERE client_id=? AND company=?", (client_id, "ACME")).fetchone()["id"]
            conn.execute(
                "INSERT INTO price_history (investment_id, price, created_at) VALUES (?,?,?)",
                (inv_id, 105.0, now),
            )
            conn.execute(
                "INSERT INTO investment_trades (investment_id, type, shares, price, amount, created_at, note) VALUES (?,?,?,?,?,?,?)",
                (inv_id, "BUY", 20.0, 100.0, 2000.0, now, "Seed"),
            )
            # Registrar salida de capital por compra
            conn.execute(
                "INSERT INTO cash_movements (client_id, type, amount, note, created_at) VALUES (?,?,?,?,?)",
                (client_id, "WITHDRAW", 2000.0, "Compra inicial ACME", now),
            )
            conn.execute(
                "UPDATE clients SET capital_available = capital_available - ? WHERE id=?",
                (2000.0, client_id)
            )