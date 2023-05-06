class OutOfSequenceError(Exception):
    """Raised when an order book update is out of sequence relative to the prior update, suggesting missing data."""
    pass