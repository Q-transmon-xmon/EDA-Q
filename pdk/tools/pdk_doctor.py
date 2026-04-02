import argparse
import json
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from pdk.core.registry import discover_pdks
from pdk.core.loader import load_pdk
from pdk.core.validator import validate_pdk_context
from pdk.core.overlay import load_overlay, load_overlay_from_path, apply_overlay_doc


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


def _build_targets(discovered, pdk_id=None, version=None):
    targets = []
    if pdk_id is not None:
        if pdk_id not in discovered:
            raise ValueError(f"PDK not found: {pdk_id}")
        versions = discovered[pdk_id]
        if version is not None:
            if version not in versions:
                available = ", ".join(sorted(versions.keys(), key=_version_key))
                raise ValueError(f"Version {version} not found for {pdk_id}. Available: {available}")
            targets.append((pdk_id, version))
        else:
            for v in sorted(versions.keys(), key=_version_key):
                targets.append((pdk_id, v))
        return targets

    for pid in sorted(discovered.keys()):
        for v in sorted(discovered[pid].keys(), key=_version_key):
            targets.append((pid, v))
    return targets


def _load_overlay_doc(overlay_id=None, overlay_path=None):
    if overlay_id is None and overlay_path is None:
        return None
    if overlay_id is not None and overlay_path is not None:
        raise ValueError("Only one of --overlay-id or --overlay-path can be provided.")
    if overlay_id is not None:
        return load_overlay(overlay_id=overlay_id)
    return load_overlay_from_path(overlay_path=overlay_path)


def run_doctor(args):
    discovered = discover_pdks(registry_root=args.registry_root)
    if not discovered:
        raise ValueError("No PDK package found under registry root.")

    overlay_doc = _load_overlay_doc(overlay_id=args.overlay_id, overlay_path=args.overlay_path)
    targets = _build_targets(discovered, pdk_id=args.pdk_id, version=args.version)

    summary = {
        "ok": 0,
        "failed": 0,
        "targets": [],
    }

    for pid, ver in targets:
        item = {
            "pdk_id": pid,
            "version": ver,
            "status": "ok",
            "errors": [],
            "warnings": [],
            "infos": [],
        }
        try:
            context = load_pdk(pdk_id=pid, version=ver, registry_root=args.registry_root)
            report = validate_pdk_context(context)
            item["errors"].extend(report.errors)
            item["warnings"].extend(report.warnings)
            item["infos"].extend(report.infos)

            if overlay_doc is not None:
                try:
                    merged_context = apply_overlay_doc(
                        pdk_context=context,
                        overlay_doc=overlay_doc,
                        strict_base=not args.no_strict_base,
                    )
                    merged_report = validate_pdk_context(merged_context)
                    item["errors"].extend(merged_report.errors)
                    item["warnings"].extend(merged_report.warnings)
                    item["infos"].append("Overlay applied successfully.")
                except Exception as exc:
                    item["errors"].append(f"Overlay apply failed: {exc}")

            if item["errors"]:
                item["status"] = "failed"
            elif args.fail_on_warning and item["warnings"]:
                item["status"] = "failed"
            else:
                item["status"] = "ok"
        except Exception as exc:
            item["status"] = "failed"
            item["errors"].append(str(exc))

        if item["status"] == "ok":
            summary["ok"] += 1
        else:
            summary["failed"] += 1
        summary["targets"].append(item)

    return summary


def _print_summary(summary):
    print("== PDK Doctor Summary ==")
    print(f"Total: {len(summary['targets'])}, OK: {summary['ok']}, Failed: {summary['failed']}")
    print("")
    for item in summary["targets"]:
        print(f"[{item['status'].upper()}] {item['pdk_id']}@{item['version']}")
        if item["errors"]:
            for err in item["errors"]:
                print(f"  - ERROR: {err}")
        if item["warnings"]:
            for warn in item["warnings"]:
                print(f"  - WARN: {warn}")
        if item["infos"]:
            for info in item["infos"]:
                print(f"  - INFO: {info}")


def main():
    parser = argparse.ArgumentParser(description="PDK package doctor for integrity and loadability checks.")
    parser.add_argument("--registry-root", default=None, help="PDK registry root path. Default: pdk/foundries")
    parser.add_argument("--pdk-id", default=None, help="Only check one pdk_id")
    parser.add_argument("--version", default=None, help="Only check one version")
    parser.add_argument("--overlay-id", default=None, help="Apply and validate one project overlay by overlay_id")
    parser.add_argument("--overlay-path", default=None, help="Apply and validate one project overlay by file path")
    parser.add_argument("--no-strict-base", action="store_true", help="Do not enforce overlay base_pdk strict checks")
    parser.add_argument("--fail-on-warning", action="store_true", help="Treat warnings as failure")
    parser.add_argument("--json-out", default=None, help="Write full summary to a json file")
    args = parser.parse_args()

    try:
        summary = run_doctor(args)
        _print_summary(summary)

        if args.json_out:
            out_path = Path(args.json_out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"\nJSON report written to: {out_path}")

        if summary["failed"] > 0:
            return 2
        return 0
    except Exception as exc:
        print(f"PDK doctor failed: {exc}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
