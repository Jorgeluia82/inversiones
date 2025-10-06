import csv
from typing import List, Dict, Any

def export_history_csv(path: str, rows: List[Dict[str, Any]]):
    fieldnames = ["fecha","tipo_general","tipo","empresa","detalle","monto_cambio_capital","shares","price"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({
                "fecha": r.get("fecha",""),
                "tipo_general": r.get("tipo_general",""),
                "tipo": r.get("tipo",""),
                "empresa": r.get("empresa",""),
                "detalle": r.get("detalle",""),
                "monto_cambio_capital": r.get("monto_cambio_capital",""),
                "shares": r.get("shares",""),
                "price": r.get("price",""),
            })
