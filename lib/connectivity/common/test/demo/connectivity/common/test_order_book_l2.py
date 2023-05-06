import decimal
from demo.connectivity.common.order_book_l2 import Order, OrderBookL2, TopOfBookPair 

def test_add_bid():
    book = OrderBookL2()

    book.add_bid(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    book.add_bid(decimal.Decimal('9.0'), decimal.Decimal('2.0'))
    book.add_bid(decimal.Decimal('11.0'), decimal.Decimal('3.0'))

    assert len(book._bids) == 3
    assert book._bids[0] == Order(decimal.Decimal('11.0'), decimal.Decimal('3.0'))
    assert book._bids[1] == Order(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    assert book._bids[2] == Order(decimal.Decimal('9.0'), decimal.Decimal('2.0'))

def test_add_ask():
    book = OrderBookL2()

    book.add_ask(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    book.add_ask(decimal.Decimal('9.0'), decimal.Decimal('2.0'))
    book.add_ask(decimal.Decimal('11.0'), decimal.Decimal('3.0'))

    assert len(book._asks) == 3
    assert book._asks[0] == Order(decimal.Decimal('9.0'), decimal.Decimal('2.0'))
    assert book._asks[1] == Order(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    assert book._asks[2] == Order(decimal.Decimal('11.0'), decimal.Decimal('3.0'))

def test_remove_bid():
    book = OrderBookL2()
    book.add_bid(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    book.add_bid(decimal.Decimal('9.0'), decimal.Decimal('2.0'))

    book.remove_bid(decimal.Decimal('10.0'))

    assert len(book._bids) == 1
    assert book._bids[0] == Order(decimal.Decimal('9.0'), decimal.Decimal('2.0'))

def test_remove_ask():
    book = OrderBookL2()
    book.add_ask(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    book.add_ask(decimal.Decimal('9.0'), decimal.Decimal('2.0'))

    book.remove_ask(decimal.Decimal('10.0'))

    assert len(book._asks) == 1
    assert book._asks[0] == Order(decimal.Decimal('9.0'), decimal.Decimal('2.0'))

def test_clear():
    book = OrderBookL2()
    book.add_bid(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    book.add_ask(decimal.Decimal('9.0'), decimal.Decimal('2.0'))

    book.clear()

    assert len(book._bids) == 0
    assert len(book._asks) == 0

def test_get_top_pair():
    book = OrderBookL2()
    book.add_bid(decimal.Decimal('10.0'), decimal.Decimal('1.0'))
    book.add_ask(decimal.Decimal('11.0'), decimal.Decimal('2.0'))

    top_pair = book.get_top_pair()

    assert top_pair == TopOfBookPair(Order(decimal.Decimal('10.0'), decimal.Decimal('1.0')),
                                      Order(decimal.Decimal('11.0'), decimal.Decimal('2.0')))