"""Example runtime demonstrating dynamic plugin loading."""
from __future__ import annotations

from plugin_manager import PluginManager


if __name__ == "__main__":
    pm = PluginManager("plugins")
    pm.load_all()

    print("Loaded plugins:", list(pm.plugins))
    tool = pm.get_tool("inventory_plugin", "fetch_inventory")
    print("Inventory result:", tool(["item1", "item2"]))
