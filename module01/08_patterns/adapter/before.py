"""Adapter — before.

Three carrier APIs, three incompatible payload shapes. Checkout branches on
carrier and unpacks each one inline.

Run: python3 before.py
"""

from decimal import Decimal
from typing import Any


class NovaPoshtaApi:
    def get_price(self, city_from: str, city_to: str, weight: float) -> dict[str, Any]:
        return {"success": True,
                "data": [{"Cost": "120.00", "Currency": "UAH", "DeliveryDays": "2"}]}


class DhlApi:
    def rates(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"products": [{"totalPrice": [{"price": 24.90, "currency": "EUR"}],
                              "deliveryCapabilities": {"totalTransitDays": 3}}]}


class UkrposhtaApi:
    def calculate(self, frm: str, to: str, grams: int) -> dict[str, Any]:
        return {"delivery_price": 8450, "delivery_time_days": 5}  # kopiykas


def get_quote(carrier: str, origin: str, destination: str, kg: float) -> tuple[Decimal, str, str, int]:
    if carrier == "novaposhta":
        raw = NovaPoshtaApi().get_price(origin, destination, kg)
        row = raw["data"][0]
        return Decimal(row["Cost"]), "Nova Poshta", row["Currency"], int(row["DeliveryDays"])
    elif carrier == "dhl":
        raw = DhlApi().rates({"from": origin, "to": destination, "weight": kg})
        product = raw["products"][0]
        price = product["totalPrice"][0]
        return (Decimal(str(price["price"])), "DHL", price["currency"],
                product["deliveryCapabilities"]["totalTransitDays"])
    elif carrier == "ukrposhta":
        raw = UkrposhtaApi().calculate(origin, destination, grams=int(kg * 1000))
        return Decimal(raw["delivery_price"]) / 100, "Ukrposhta", "UAH", raw["delivery_time_days"]
    raise ValueError(carrier)


def main() -> None:
    quotes = [get_quote(c, "Kyiv", "Lviv", 2.5) for c in ("novaposhta", "dhl", "ukrposhta")]
    for amount, carrier, currency, eta in sorted(quotes):
        print(f"{carrier:<12} {amount:>8.2f} {currency}  {eta} day(s)")


if __name__ == "__main__":
    main()
