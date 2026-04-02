from pathlib import Path
import json


def _default_registry_root():
    return Path(__file__).resolve().parents[1] / "foundries"


def _version_key(version):
    parts = str(version).split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    out = []
    for part in parts:
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out)


def discover_pdks(registry_root=None):
    root = Path(registry_root) if registry_root else _default_registry_root()
    out = {}
    if not root.exists():
        return out

    for manifest_path in root.glob("*/*/*/manifest.json"):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        pdk_id = manifest.get("pdk_id")
        version = manifest.get("version")
        if not pdk_id or not version:
            continue

        out.setdefault(pdk_id, {})
        out[pdk_id][version] = manifest_path.parent

    return out


def resolve_pdk_path(pdk_id, version=None, registry_root=None):
    discovered = discover_pdks(registry_root=registry_root)
    if pdk_id not in discovered:
        raise ValueError(f"PDK not found: {pdk_id}")

    versions = discovered[pdk_id]
    if not versions:
        raise ValueError(f"No versions available for PDK: {pdk_id}")

    if version is None:
        selected_version = sorted(versions.keys(), key=_version_key)[-1]
    else:
        if version not in versions:
            available = ", ".join(sorted(versions.keys(), key=_version_key))
            raise ValueError(f"Version {version} not found for {pdk_id}. Available: {available}")
        selected_version = version

    return versions[selected_version]
