from abc import ABC, abstractmethod


class Discount(ABC):
    label = "no discount"

    @abstractmethod
    def apply(self, amount): ...


class PercentDiscount(Discount):
    def __init__(self, name, rate):
        self.label = f"{name} -{int(rate * 100)}%"
        self.rate = rate

    def apply(self, amount):
        return amount * (1 - self.rate)


class BulkDiscount(Discount):
    label = "bulk -10% over 1000"

    def apply(self, amount):
        return amount * 0.90 if amount > 1000 else amount


def receipt_line(discount, amount):
    return f"{discount.label:<20} {discount.apply(amount):>6.0f}"


if __name__ == "__main__":
    discounts = [
        PercentDiscount("regular", 0.05),
        PercentDiscount("vip", 0.20),
        BulkDiscount(),
    ]
    for discount in discounts:
        print(receipt_line(discount, 2000))
