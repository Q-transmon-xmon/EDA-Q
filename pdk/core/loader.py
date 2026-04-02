from pathlib import Path
import copy
import json
from addict import Dict

from pdk.core.registry import resolve_pdk_path
from pdk.core.schema import validate_manifest


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _deep_update(base, overlay):
    base = copy.deepcopy(base)
    overlay = Dict(overlay)
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = _deep_update(base[key], value)
        else:
            base[key] = copy.deepcopy(value)
    return base


def load_pdk(pdk_id, version=None, registry_root=None):
    pdk_path = resolve_pdk_path(pdk_id=pdk_id, version=version, registry_root=registry_root)
    return load_pdk_from_path(pdk_path)


def load_pdk_from_path(pdk_path):
    pdk_path = Path(pdk_path)
    manifest_path = pdk_path / "manifest.json"
    if not manifest_path.exists():
        raise ValueError(f"manifest.json not found in: {pdk_path}")

    manifest = Dict(_load_json(manifest_path))
    validation = validate_manifest(manifest)
    if not validation.valid:
        raise ValueError("Invalid PDK manifest: " + "; ".join(validation.errors))

    files = Dict(manifest.files)
    context = Dict()
    context.manifest = copy.deepcopy(manifest)
    context.path = str(pdk_path)

    for key in files.keys():
        rel_path = files[key]
        full_path = pdk_path / rel_path
        if not full_path.exists():
            raise ValueError(f"PDK file not found: {full_path}")
        context[key] = Dict(_load_json(full_path))

    return context


def apply_overlay(pdk_context, overlay):
    pdk_context = Dict(copy.deepcopy(pdk_context))
    overlay = Dict(copy.deepcopy(overlay))

    for key, value in overlay.items():
        if key in pdk_context and isinstance(pdk_context[key], dict) and isinstance(value, dict):
            pdk_context[key] = Dict(_deep_update(pdk_context[key], value))
        else:
            pdk_context[key] = copy.deepcopy(value)
    return pdk_context
