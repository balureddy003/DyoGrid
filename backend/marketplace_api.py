"""FastAPI service exposing the DyoGrid plugin marketplace."""
from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile, Query
from pydantic import BaseModel

from plugin_manager import PluginManager

PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

app = FastAPI(title="DyoGrid Plugin Marketplace")

pm = PluginManager(PLUGINS_DIR)
pm.load_all()


class PluginInfo(BaseModel):
    """Serializable plugin metadata."""

    name: str
    version: str
    description: str | None = None
    tags: List[str] = []


@app.get("/plugins", response_model=List[PluginInfo])
def list_plugins(tag: str | None = Query(None)) -> List[PluginInfo]:
    """Return installed plugins, optionally filtering by tag."""
    pm.load_all()
    manifests = [p.manifest for p in pm.plugins.values()]
    if tag:
        manifests = [m for m in manifests if tag in m.tags]
    return [PluginInfo(**m.model_dump()) for m in manifests]


@app.post("/plugins/upload")
async def upload_plugin(file: UploadFile = File(...)) -> dict:
    """Upload and install a plugin ZIP archive."""
    if file.content_type not in {"application/zip", "application/x-zip-compressed"}:
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")
    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    tmp_path = Path("/tmp") / file.filename
    tmp_path.write_bytes(data)
    try:
        plugin = pm.install_from_zip(tmp_path)
    except Exception as exc:  # pragma: no cover - simple error handling
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        tmp_path.unlink(missing_ok=True)
    return {"status": "installed", "plugin": plugin.manifest.name}

