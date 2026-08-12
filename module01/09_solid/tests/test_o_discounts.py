from solid_ex.o_open_closed.after import BulkDiscount, Discount, PercentDiscount, receipt_line


def test_percent_discount():
    assert PercentDiscount("vip", 0.20).apply(1000) == 800
    assert PercentDiscount("vip", 0.20).label == "vip -20%"


def test_bulk_discount_only_over_threshold():
    assert BulkDiscount().apply(2000) == 1800
    assert BulkDiscount().apply(500) == 500


def test_new_discount_needs_no_edits_to_existing_code():
    class BlackFriday(Discount):
        label = "black friday -70%"

        def apply(self, amount):
            return amount * 0.30

    assert BlackFriday().apply(1000) == 300
    assert "black friday" in receipt_line(BlackFriday(), 1000)
