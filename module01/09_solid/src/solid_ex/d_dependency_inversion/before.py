class SmtpClient:
    def send_email(self, to, text):
        print(f"SMTP -> {to}: {text}")


class PostgresOrders:
    def __init__(self):
        self.count = 0

    def add(self, item):
        self.count += 1
        print(f"INSERT INTO orders ('{item}')")
        return self.count


class OrderService:
    def __init__(self):
        self.db = PostgresOrders()
        self.smtp = SmtpClient()

    def place_order(self, email, item):
        order_id = self.db.add(item)
        self.smtp.send_email(email, f"order #{order_id}: {item}")


if __name__ == "__main__":
    service = OrderService()
    service.place_order("olena@example.com", "keyboard")
    service.place_order("olena@example.com", "mouse")
