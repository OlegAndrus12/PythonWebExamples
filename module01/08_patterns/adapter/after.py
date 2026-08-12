"""Adapter — after.

One adapter per carrier, each translating that carrier's payload into a
ShippingQuote. Checkout only ever sees that one shape.

Run: python3 after.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True, order=True)
class ShippingQuote:
    amount: Decimal
    carrier: str
    currency: str
    eta_days: int


class RateAdapter(ABC):
    carrier: str

    @abstractmethod
    def fetch(self, origin: str, destination: str, kg: float) -> ShippingQuote: ...


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
        return {"delivery_price": 8450, "delivery_time_days": 5}


class NovaPoshtaAdapter(RateAdapter):
    carrier = "Nova Poshta"

    def __init__(self, api: NovaPoshtaApi) -> None:
        self.api = api

    def fetch(self, origin: str, destination: str, kg: float) -> ShippingQuote:
        raw = self.api.get_price(origin, destination, kg)
        if not raw.get("success"):
            raise RuntimeError("Nova Poshta rejected the request")
        row = raw["data"][0]
        return ShippingQuote(Decimal(row["Cost"]), self.carrier,
                              row["Currency"], int(row["DeliveryDays"]))


class DhlAdapter(RateAdapter):
    carrier = "DHL"

    def __init__(self, api: DhlApi) -> None:
        self.api = api

    def fetch(self, origin: str, destination: str, kg: float) -> ShippingQuote:
        raw = self.api.rates({"from": origin, "to": destination, "weight": kg})
        product = raw["products"][0]
        price = product["totalPrice"][0]
        return ShippingQuote(Decimal(str(price["price"])), self.carrier,
                              price["currency"],
                              product["deliveryCapabilities"]["totalTransitDays"])


class UkrposhtaAdapter(RateAdapter):
    carrier = "Ukrposhta"

    def __init__(self, api: UkrposhtaApi) -> None:
        self.api = api

    def fetch(self, origin: str, destination: str, kg: float) -> ShippingQuote:
        raw = self.api.calculate(origin, destination, grams=int(kg * 1000))
        return ShippingQuote(Decimal(raw["delivery_price"]) / 100, self.carrier,
                              "UAH", raw["delivery_time_days"])


def main() -> None:
    adapters: list[RateAdapter] = [
        NovaPoshtaAdapter(NovaPoshtaApi()),
        DhlAdapter(DhlApi()),
        UkrposhtaAdapter(UkrposhtaApi()),
    ]
    quotes = sorted(adapter.fetch("Kyiv", "Lviv", 2.5) for adapter in adapters)
    for quote in quotes:
        print(f"{quote.carrier:<12} {quote.amount:>8.2f} {quote.currency}  {quote.eta_days} day(s)")


if __name__ == "__main__":
    main()
