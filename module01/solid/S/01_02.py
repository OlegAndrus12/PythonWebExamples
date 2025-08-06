import requests

def pretty_view(data: list[dict]):
    pattern = "|{:^10}|{:^10}|{:^10}|"
    for el in data:
        currency, *_ = el.keys()
        buy = el.get(currency).get("buy")
        sale = el.get(currency).get("sale")
        print(pattern.format(currency, sale, buy))


def data_adapter(data: dict) -> list[dict]:
    return [
        {
            f"{el.get('ccy')}": {
                "buy": float(el.get("buy")),
                "sale": float(el.get("sale")),
            }
        }
        for el in data
    ]


if __name__ == "__main__":
    data = requests.get(
        "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=11"
    )
    pretty_view(data_adapter(data))
