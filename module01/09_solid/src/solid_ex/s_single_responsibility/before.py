import json


class OrderReport:
    def __init__(self, orders):
        self.orders = orders

    def show_table(self):
        total = 0
        lines = []
        for order in self.orders:
            amount = order["price"] * order["qty"]
            if order["qty"] >= 10:
                amount = int(amount * 0.9)
            total += amount
            lines.append(f"{order['name']:<10} {amount:>6}")
        lines.append(f"{'total':<10} {total:>6}")
        print("\n".join(lines))

    def show_json(self):
        total = 0
        for order in self.orders:
            total += order["price"] * order["qty"]
        print(json.dumps({"total": total}))


if __name__ == "__main__":
    orders = [
        {"name": "keyboard", "price": 1200, "qty": 1},
        {"name": "cable", "price": 80, "qty": 20},
    ]
    report = OrderReport(orders)
    report.show_table()
    report.show_json()
