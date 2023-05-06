import time

import demo.connectivity.common.json as json


def make_order_book_subscription_payload(symbol: str, req_id: int = time.time_ns()) -> str:
    return json.dumps({
        "method": "SUBSCRIBE",
        "params": [
            f"{symbol.lower()}@depth@100ms",
        ],
        "id": req_id
    })