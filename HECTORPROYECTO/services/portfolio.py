from typing import Optional, List, Dict, Any
import sqlite3
from data import repositorios as repo
from utils.validation import ensure_positive, ensure_non_negative, ensure_shares_positive
from utils.format import now_iso
from datetime import datetime, timedelta

class PortfolioService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---- Cash ----
    def deposit(self, client_id: int, amount: float, note: Optional[str] = None):
        ensure_positive(amount, "El depósito debe ser > 0")
        try:
            self.conn.execute("BEGIN")
            repo.update_client_capital(self.conn, client_id, amount)
            repo.insert_cash_movement(self.conn, client_id, "DEPOSIT", amount, note)
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def withdraw(self, client_id: int, amount: float, note: Optional[str] = None):
        ensure_positive(amount, "El retiro debe ser > 0")
        client = repo.get_client(self.conn, client_id)
        if not client:
            raise ValueError("Cliente no existe")
        if client["capital_available"] < amount:
            raise ValueError("Fondos insuficientes para retirar")
        try:
            self.conn.execute("BEGIN")
            repo.update_client_capital(self.conn, client_id, -amount)
            repo.insert_cash_movement(self.conn, client_id, "WITHDRAW", amount, note)
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    # ---- Trades ----
    def buy(self, client_id: int, company: str, amount: float, price: float, note: Optional[str] = None):
        ensure_positive(amount, "El monto debe ser > 0")
        ensure_positive(price, "El precio debe ser > 0")
        client = repo.get_client(self.conn, client_id)
        if not client:
            raise ValueError("Cliente no existe")
        if client["capital_available"] < amount:
            raise ValueError("Capital insuficiente")
        shares = amount / price
        try:
            self.conn.execute("BEGIN")
            inv = repo.get_investment_by_company(self.conn, client_id, company)
            if inv:
                # nuevo promedio ponderado
                new_shares = inv["shares"] + shares
                new_avg = ((inv["avg_price"] * inv["shares"]) + amount) / new_shares
                repo.update_investment(self.conn, inv["id"], avg_price=new_avg, shares=new_shares)
                inv_id = inv["id"]
            else:
                inv_id = repo.create_investment(self.conn, client_id, company, price, shares)
            # capital down
            repo.update_client_capital(self.conn, client_id, -amount)
            # trade + price history
            repo.insert_trade(self.conn, inv_id, "BUY", shares, price, amount, note)
            repo.insert_price_history(self.conn, inv_id, price)
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def sell(self, investment_id: int, shares_to_sell: float, price: float, note: Optional[str] = None):
        ensure_positive(shares_to_sell, "Las acciones a vender deben ser > 0")
        ensure_positive(price, "El precio debe ser > 0")
        inv = repo.get_investment(self.conn, investment_id)
        if not inv:
            raise ValueError("Inversión no existe")
        if shares_to_sell > inv["shares"]:
            raise ValueError("No hay suficientes acciones")
        amount = shares_to_sell * price
        try:
            self.conn.execute("BEGIN")
            # actualizar inversión
            remaining = inv["shares"] - shares_to_sell
            new_avg = inv["avg_price"] if remaining > 0 else 0.0
            repo.update_investment(self.conn, investment_id, avg_price=new_avg, shares=remaining)
            # abonar capital
            client_id = inv["client_id"]
            repo.update_client_capital(self.conn, client_id, amount)
            # trade (SELL) y price_history (opcional mantener precio de venta solo como trade)
            repo.insert_trade(self.conn, investment_id, "SELL", shares_to_sell, price, amount, note)
            repo.insert_price_history(self.conn, investment_id, price)
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def update_price(self, investment_id: int, price: float, note: Optional[str] = None):
        ensure_positive(price, "El precio debe ser > 0")
        inv = repo.get_investment(self.conn, investment_id)
        if not inv:
            raise ValueError("Inversión no existe")
        try:
            self.conn.execute("BEGIN")
            # PRICE_UPDATE no cambia shares/capital
            repo.insert_trade(self.conn, investment_id, "PRICE_UPDATE", 0.0, price, 0.0, note)
            repo.insert_price_history(self.conn, investment_id, price)
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    # ---- Queries ----
    def get_last_price(self, investment_id: int) -> Optional[float]:
        return repo.get_last_price(self.conn, investment_id)

    def get_client_portfolio(self, client_id: int) -> List[Dict[str, Any]]:
        investments = repo.get_investments_by_client(self.conn, client_id)
        rows = []
        for inv in investments:
            current_price = repo.get_last_price(self.conn, inv["id"]) or inv["avg_price"]
            current_value = current_price * inv["shares"]
            pnl = (current_price - inv["avg_price"]) * inv["shares"]
            rows.append({
                "investment_id": inv["id"],
                "company": inv["company"],
                "shares": inv["shares"],
                "avg_price": inv["avg_price"],
                "current_price": current_price,
                "current_value": current_value,
                "pnl": pnl,
            })
        return rows

    def _range_from_day(self, day: str) -> tuple[str, str]:
        # day: "YYYY-MM-DD"
        start = f"{day} 00:00:00"
        end = f"{day} 23:59:59"
        return start, end

    def get_client_history(self, client_id: int, day: Optional[str] = None,
                           date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        start_iso = end_iso = None
        if day:
            start_iso, end_iso = self._range_from_day(day)
        elif date_from and date_to:
            start_iso = f"{date_from} 00:00:00"
            end_iso = f"{date_to} 23:59:59"

        cash = repo.fetch_cash_movements(self.conn, client_id, start_iso, end_iso)
        trades = repo.fetch_trades_with_company(self.conn, client_id, start_iso, end_iso)

        unified: List[Dict[str, Any]] = []
        # Cash
        for m in cash:
            delta = m["amount"] if m["type"] == "DEPOSIT" else -m["amount"]
            unified.append({
                "fecha": m["created_at"],
                "tipo_general": "EFECTIVO",
                "tipo": m["type"],
                "empresa": "",
                "detalle": f"{m['type']} ${m['amount']:.2f}" + (f" ({m['note']})" if m['note'] else ""),
                "monto_cambio_capital": delta,
                "shares": "",
                "price": "",
            })
        # Trades
        for t in trades:
            empresa = t["company"]
            tipo = t["type"]
            if tipo == "BUY":
                detalle = f"BUY {t['shares']:.4f} @ ${t['price']:.2f} de {empresa}"
                delta = -t["amount"]
            elif tipo == "SELL":
                detalle = f"SELL {t['shares']:.4f} @ ${t['price']:.2f} de {empresa}"
                delta = t["amount"]
            else:  # PRICE_UPDATE
                detalle = f"PRICE_UPDATE @ ${t['price']:.2f} de {empresa}"
                delta = 0.0
            unified.append({
                "fecha": t["created_at"],
                "tipo_general": "INVERSIÓN" if tipo in ("BUY", "SELL") else "PRECIO",
                "tipo": tipo,
                "empresa": empresa,
                "detalle": detalle + (f" ({t['note']})" if t['note'] else ""),
                "monto_cambio_capital": delta,
                "shares": t["shares"] if t["shares"] else "",
                "price": t["price"],
            })

        # Orden desc por fecha
        unified.sort(key=lambda r: r["fecha"], reverse=True)
        return unified
