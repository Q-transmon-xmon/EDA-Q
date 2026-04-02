from pathlib import Path
import copy
import json
from addict import Dict

from pdk.core.loader import apply_overlay


OVERLAY_RESERVED_KEYS = {
    "overlay_id",
    "description",
    "base_pdk",
    "target_profile",
    "overrides",
}


def _default_overlay_root():
    return Path(__file__).resolve().parents[1] / "projects"


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_overlays(overlay_root=None):
    root = Path(overlay_root) if overlay_root else _default_overlay_root()
    out = {}
    if not root.exists():
        return out

    for overlay_path in root.glob("*/overlay.json"):
        try:
            overlay_doc = _load_json(overlay_path)
        except (OSError, json.JSONDecodeError):
            continue
        overlay_id = overlay_doc.get("overlay_id") or overlay_path.parent.name
        out[overlay_id] = overlay_path
    return out


def resolve_overlay_path(overlay_id, overlay_root=None):
    discovered = discover_overlays(overlay_root=overlay_root)
    if overlay_id not in discovered:
        available = ", ".join(sorted(discovered.keys()))
        raise ValueError(f"Overlay '{overlay_id}' not found. Available: {available}")
    return discovered[overlay_id]


def load_overlay_from_path(overlay_path):
    overlay_path = Path(overlay_path)
    if not overlay_path.exists():
        raise ValueError(f"Overlay file not found: {overlay_path}")
    return Dict(_load_json(overlay_path))


def load_overlay(overlay_id, overlay_root=None):
    overlay_path = resolve_overlay_path(overlay_id=overlay_id, overlay_root=overlay_root)
    return load_overlay_from_path(overlay_path)


def _extract_overlay_payload(overlay_doc):
    overlay_doc = Dict(copy.deepcopy(overlay_doc))
    if "overrides" in overlay_doc and isinstance(overlay_doc.overrides, dict):
        return Dict(copy.deepcopy(overlay_doc.overrides))

    payload = Dict()
    for key, value in overlay_doc.items():
        if key in OVERLAY_RESERVED_KEYS:
            continue
        payload[key] = copy.deepcopy(value)
    return payload


def apply_overlay_doc(pdk_context, overlay_doc, strict_base=True):
    pdk_context = Dict(copy.deepcopy(pdk_context))
    overlay_doc = Dict(copy.deepcopy(overlay_doc))

    if strict_base and "base_pdk" in overlay_doc:
        base = Dict(overlay_doc.base_pdk)
        if "pdk_id" in base:
            if pdk_context.manifest.get("pdk_id") != base.pdk_id:
                raise ValueError(
                    f"Overlay base_pdk.pdk_id={base.pdk_id} does not match "
                    f"loaded pdk_id={pdk_context.manifest.get('pdk_id')}"
                )
        if "version" in base:
            if pdk_context.manifest.get("version") != base.version:
                raise ValueError(
                    f"Overlay base_pdk.version={base.version} does not match "
                    f"loaded version={pdk_context.manifest.get('version')}"
                )

    payload = _extract_overlay_payload(overlay_doc)
    merged = apply_overlay(pdk_context=pdk_context, overlay=payload)
    return Dict(merged)
