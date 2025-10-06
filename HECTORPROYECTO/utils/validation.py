from datetime import datetime

def parse_float_or_none(s: str):
    try:
        s = (s or "").replace(",", "").strip()
        return float(s)
    except Exception:
        return None

def ensure_positive(value: float, msg: str):
    if value is None or value <= 0:
        raise ValueError(msg)

def ensure_non_negative(value: float, msg: str):
    if value is None or value < 0:
        raise ValueError(msg)

def ensure_shares_positive(value: float, msg: str):
    ensure_positive(value, msg)

def is_valid_date(s: str) -> bool:
    if not s: return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def validate_date_str(s: str):
    if not is_valid_date(s):
        raise ValueError("Fecha inválida. Use YYYY-MM-DD")
