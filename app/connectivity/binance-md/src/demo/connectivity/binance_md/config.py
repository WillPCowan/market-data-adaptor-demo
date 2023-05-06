from typing import Dict


class BinanceMdConfig:

  def __init__(self, config: Dict[str,str]) -> None:
    self.http_uri = config.get('http_uri')
    self.ws_uri = config.get('ws_uri')
    self.symbol = config.get('symbol')
    self.depth = config.get('depth')