from typing import List


def fetch_inventory(item_ids: List[str]) -> dict:
    """Sample plugin tool that returns dummy inventory data for the given item IDs."""
    return {item_id: {"qty": 42, "status": "in stock"} for item_id in item_ids}


