from typing import Optional, List, Dict, Any, Tuple
import sqlite3

# ==== Clients ====

def list_clients(conn: sqlite3.Connection, q: Optional[str] = None) -> List[sqlite3.Row]:
    if q:
        return conn.execute(
            "SELECT * FROM clients WHERE name LIKE ? ORDER BY created_at DESC",
            (f"%{q}%",),
        ).fetchall()
    return conn.execute(
        "SELECT * FROM clients ORDER BY created_at DESC"
    ).fetchall()

def create_client(conn: sqlite3.Connection, name: str, email: Optional[str], phone: Optional[str], initial_capital: float) -> int:
    from utils.format import now_iso
    now = now_iso()
    cur = conn.execute(
        "INSERT INTO clients (name, email, phone, created_at, capital_available) VALUES (?,?,?,?,?)",
        (name, email, phone, now, float(initial_capital or 0.0)),
    )
    return cur.lastrowid

def get_client(conn: sqlite3.Connection, client_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()

def update_client_capital(conn: sqlite3.Connection, client_id: int, delta: float):
    conn.execute("UPDATE clients SET capital_available = capital_available + ? WHERE id=?", (delta, client_id))

# ==== Investments ====

def get_investments_by_client(conn: sqlite3.Connection, client_id: int) -> List[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM investments WHERE client_id=? ORDER BY created_at DESC", (client_id,)
    ).fetchall()

def get_all_investments(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """Obtiene todas las inversiones de todos los clientes."""
    return conn.execute("SELECT * FROM investments").fetchall()

def get_investment_by_company(conn: sqlite3.Connection, client_id: int, company: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM investments WHERE client_id=? AND company=?",
        (client_id, company),
    ).fetchone()

def get_investment(conn: sqlite3.Connection, investment_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM investments WHERE id=?", (investment_id,)).fetchone()

def create_investment(conn: sqlite3.Connection, client_id: int, company: str, category: str, avg_price: float, shares: float) -> int:
    from utils.format import now_iso
    now = now_iso()
    cur = conn.execute(
        "INSERT INTO investments (client_id, company, category, avg_price, shares, created_at) VALUES (?,?,?,?,?,?)",
        (client_id, company, category, avg_price, shares, now),
    )
    return cur.lastrowid

def update_investment(conn: sqlite3.Connection, investment_id: int, *, avg_price: Optional[float]=None, shares: Optional[float]=None):
    if avg_price is not None and shares is not None:
        conn.execute("UPDATE investments SET avg_price=?, shares=? WHERE id=?", (avg_price, shares, investment_id))
    elif avg_price is not None:
        conn.execute("UPDATE investments SET avg_price=? WHERE id=?", (avg_price, investment_id))
    elif shares is not None:
        conn.execute("UPDATE investments SET shares=? WHERE id=?", (shares, investment_id))

# ==== Movements / Trades / Prices ====

def insert_cash_movement(conn: sqlite3.Connection, client_id: int, mtype: str, amount: float, note: Optional[str]):
    from utils.format import now_iso
    now = now_iso()
    conn.execute(
        "INSERT INTO cash_movements (client_id, type, amount, note, created_at) VALUES (?,?,?,?,?)",
        (client_id, mtype, amount, note, now),
    )

def insert_trade(conn: sqlite3.Connection, investment_id: int, ttype: str, shares: float, price: float, amount: float, note: Optional[str]):
    from utils.format import now_iso
    now = now_iso()
    conn.execute(
        "INSERT INTO investment_trades (investment_id, type, shares, price, amount, created_at, note) VALUES (?,?,?,?,?,?,?)",
        (investment_id, ttype, shares, price, amount, now, note),
    )

def insert_price_history(conn: sqlite3.Connection, investment_id: int, price: float):
    from utils.format import now_iso
    now = now_iso()
    conn.execute(
        "INSERT INTO price_history (investment_id, price, created_at) VALUES (?,?,?)",
        (investment_id, price, now),
    )

def get_price_history(conn: sqlite3.Connection, investment_id: int) -> List[sqlite3.Row]:
    return conn.execute(
        "SELECT price, created_at FROM price_history WHERE investment_id=? ORDER BY created_at DESC",
        (investment_id,),
    ).fetchall()

def get_last_price(conn: sqlite3.Connection, investment_id: int) -> Optional[float]:
    row = conn.execute(
        "SELECT price FROM price_history WHERE investment_id=? ORDER BY created_at DESC LIMIT 1",
        (investment_id,),
    ).fetchone()
    return row["price"] if row else None

# ==== History queries (raw) ====

def fetch_cash_movements(conn: sqlite3.Connection, client_id: int, start_iso: Optional[str], end_iso: Optional[str]) -> List[sqlite3.Row]:
    base = "SELECT id, type, amount, note, created_at FROM cash_movements WHERE client_id=?"
    params = [client_id]
    if start_iso and end_iso:
        base += " AND created_at BETWEEN ? AND ?"
        params += [start_iso, end_iso]
    return conn.execute(base + " ORDER BY created_at DESC", tuple(params)).fetchall()

def fetch_trades_with_company(conn: sqlite3.Connection, client_id: int, start_iso: Optional[str], end_iso: Optional[str]) -> List[sqlite3.Row]:
    base = """
    SELECT it.id, it.type, it.shares, it.price, it.amount, it.created_at, it.note,
           inv.company, inv.id as investment_id
    FROM investment_trades it
    JOIN investments inv ON inv.id = it.investment_id
    WHERE inv.client_id=?
    """
    params = [client_id]
    if start_iso and end_iso:
        base += " AND it.created_at BETWEEN ? AND ?"
        params += [start_iso, end_iso]
    base += " ORDER BY it.created_at DESC"
    return conn.execute(base, tuple(params)).fetchall()