from abc import ABC, abstractmethod


class OrderRepo(ABC):
    @abstractmethod
    def add(self, item): ...


class Notifier(ABC):
    @abstractmethod
    def notify(self, recipient, text): ...


class PostgresOrders(OrderRepo):
    def __init__(self):
        self.count = 0

    def add(self, item):
        self.count += 1
        print(f"INSERT INTO orders ('{item}')")
        return self.count


class InMemoryOrders(OrderRepo):
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
        return len(self.items)


class EmailNotifier(Notifier):
    def notify(self, recipient, text):
        print(f"SMTP -> {recipient}: {text}")


class TelegramNotifier(Notifier):
    def notify(self, recipient, text):
        print(f"telegram -> {recipient}: {text}")


class OrderService:
    def __init__(self, repo, notifier):
        self.repo = repo
        self.notifier = notifier

    def place_order(self, recipient, item):
        order_id = self.repo.add(item)
        self.notifier.notify(recipient, f"order #{order_id}: {item}")


if __name__ == "__main__":
    prod = OrderService(PostgresOrders(), EmailNotifier())
    prod.place_order("olena@example.com", "keyboard")

    dev = OrderService(InMemoryOrders(), TelegramNotifier())
    dev.place_order("@olena", "keyboard")
