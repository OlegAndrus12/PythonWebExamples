def final_price(customer_type, amount):
    if customer_type == "regular":
        return amount * 0.95
    if customer_type == "vip":
        return amount * 0.80
    if customer_type == "staff":
        return amount * 0.50
    return amount


def receipt_line(customer_type, amount):
    if customer_type == "regular":
        label = "regular -5%"
    elif customer_type == "vip":
        label = "vip -20%"
    elif customer_type == "staff":
        label = "staff -50%"
    else:
        label = "no discount"
    return f"{label:<14} {final_price(customer_type, amount):>6.0f}"


if __name__ == "__main__":
    for customer in ("regular", "vip", "staff", "partner"):
        print(receipt_line(customer, 1000))
