from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    created_at: str
    capital_available: float

@dataclass
class Investment:
    id: int
    client_id: int
    company: str
    avg_price: float
    shares: float
    created_at: str
