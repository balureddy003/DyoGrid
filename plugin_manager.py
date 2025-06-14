"""Plugin management utilities for DyoGrid.

This module handles discovery, validation, and loading of plugins that expose
agent tools to the platform. Plugins are packaged as directories containing a
``plugin_manifest.json`` file describing the plugin metadata and an entrypoint
Python module.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional

from pydantic import BaseModel, ValidationError


class PluginManifest(BaseModel):
    """Pydantic model representing the plugin manifest."""

    name: str
    version: str
    description: Optional[str] = None
    entrypoint: str
    tags: List[str] = []
    dependencies: List[str] = []
    inputs: Dict[str, str] = {}
    outputs: Dict[str, str] = {}


@dataclass
class Plugin:
    """Internal representation of a loaded plugin."""

    manifest: PluginManifest
    module: ModuleType


class PluginInstallationError(Exception):
    """Raised when a plugin cannot be installed."""


class PluginManager:
    """Loads and validates plugins at runtime."""

    def __init__(self, plugins_dir: str | Path) -> None:
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: Dict[str, Plugin] = {}

    def load_all(self) -> None:
        """Discover and load all plugins from ``self.plugins_dir``."""
        for manifest_path in self.plugins_dir.glob("*/plugin_manifest.json"):
            try:
                plugin = self._load_plugin(manifest_path)
            except Exception as exc:  # pragma: no cover - logging only
                print(f"Failed to load plugin at {manifest_path}: {exc}")
                continue
            self._plugins[plugin.manifest.name] = plugin

    @property
    def plugins(self) -> Dict[str, Plugin]:
        return dict(self._plugins)

    # ------------------------------------------------------------------
    # Installation helpers
    # ------------------------------------------------------------------

    def install_from_directory(self, src: Path) -> Plugin:
        """Install a plugin located in a local directory."""
        manifest = self.validate_manifest(src / "plugin_manifest.json")
        dest = self.plugins_dir / manifest.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        plugin = self._load_plugin(dest / "plugin_manifest.json")
        self._plugins[plugin.manifest.name] = plugin
        return plugin

    def install_from_zip(self, zip_path: Path) -> Plugin:
        """Install a plugin from a ZIP archive."""
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(td)
            return self.install_from_directory(Path(td))

    def install_from_git(self, repo_url: str, branch: str | None = None) -> Plugin:
        """Clone a plugin from GitHub and install it."""
        with tempfile.TemporaryDirectory() as td:
            cmd = ["git", "clone", repo_url, td]
            subprocess.run(cmd, check=True)
            if branch:
                subprocess.run(["git", "checkout", branch], cwd=td, check=True)
            return self.install_from_directory(Path(td))

    def _load_plugin(self, manifest_path: Path) -> Plugin:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        manifest = PluginManifest(**data)
        plugin_dir = manifest_path.parent
        module = self._import_module(plugin_dir / manifest.entrypoint)
        self._install_dependencies(manifest, plugin_dir)
        return Plugin(manifest=manifest, module=module)

    def _import_module(self, module_path: Path) -> ModuleType:
        """Dynamically import ``module_path`` as a module."""
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path.stem] = module
        spec.loader.exec_module(module)
        return module

    def _install_dependencies(self, manifest: PluginManifest, plugin_dir: Path) -> None:
        """Install plugin dependencies using ``pip`` if necessary."""
        if not manifest.dependencies:
            return

        requirements = " ".join(manifest.dependencies)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", requirements],
            cwd=plugin_dir,
            check=True,
        )

    def get_tool(self, plugin_name: str, tool_name: str):
        """Retrieve a callable tool from a loaded plugin."""
        plugin = self._plugins[plugin_name]
        return getattr(plugin.module, tool_name)

    def validate_manifest(self, manifest_path: Path) -> PluginManifest:
        """Validate a plugin manifest and return the parsed model."""
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return PluginManifest(**data)


__all__ = [
    "PluginManager",
    "PluginManifest",
    "Plugin",
    "PluginInstallationError",
]
