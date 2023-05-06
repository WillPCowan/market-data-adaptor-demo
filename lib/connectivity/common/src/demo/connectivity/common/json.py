from typing import Any, Dict
import simplejson

def dumps(
        obj: Dict[Any, Any]
) -> str:
    return simplejson.dumps(obj, use_decimal=True)

def loads(
        s: str
) -> object:
    return simplejson.loads(s, use_decimal=True)