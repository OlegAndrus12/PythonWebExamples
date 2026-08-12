import json


def line_total(order):
    amount = order["price"] * order["qty"]
    if order["qty"] >= 10:
        amount = int(amount * 0.9)
    return amount


def order_total(orders):
    return sum(line_total(order) for order in orders)


def render_table(orders):
    lines = [f"{order['name']:<10} {line_total(order):>6}" for order in orders]
    lines.append(f"{'total':<10} {order_total(orders):>6}")
    return "\n".join(lines)


def render_json(orders):
    return json.dumps({"total": order_total(orders)})


def send_to_console(text):
    print(text)


if __name__ == "__main__":
    orders = [
        {"name": "keyboard", "price": 1200, "qty": 1},
        {"name": "cable", "price": 80, "qty": 20},
    ]
    send_to_console(render_table(orders))
    send_to_console(render_json(orders))
