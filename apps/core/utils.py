from typing import Optional


def get_attr_or_none(obj, name: str) -> Optional:
    try:
        attr = getattr(obj, name)
    except AttributeError:
        return
    return attr
