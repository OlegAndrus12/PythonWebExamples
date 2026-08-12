from solid_ex.d_dependency_inversion.after import InMemoryOrders, Notifier, OrderService


class FakeNotifier(Notifier):
    def __init__(self):
        self.sent = []

    def notify(self, recipient, text):
        self.sent.append((recipient, text))


def test_order_is_stored_and_confirmation_sent():
    repo = InMemoryOrders()
    notifier = FakeNotifier()
    service = OrderService(repo, notifier)

    service.place_order("olena@example.com", "keyboard")
    service.place_order("olena@example.com", "mouse")

    assert repo.items == ["keyboard", "mouse"]
    assert notifier.sent == [
        ("olena@example.com", "order #1: keyboard"),
        ("olena@example.com", "order #2: mouse"),
    ]
