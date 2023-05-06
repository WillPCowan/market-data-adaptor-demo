import time

import demo.connectivity.common.json as json
import demo.connectivity.binance_md.utils as utils

def test_make_order_book_subscription_payload() -> None:
    id = time.time_ns()
    assert utils.make_order_book_subscription_payload("BNBBTC", id) == json.dumps({
        "method": "SUBSCRIBE",
        "params": [
            "bnbbtc@depth@100ms",
        ],
        "id": id
    })