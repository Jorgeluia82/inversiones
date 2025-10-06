from datetime import datetime

def money(x: float) -> str:
    return f"$ {x:,.2f}"

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
