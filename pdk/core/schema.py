import re
from addict import Dict


SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

REQUIRED_MANIFEST_KEYS = (
    "pdk_id",
    "foundry",
    "line",
    "version",
    "schema_version",
    "compatibility",
    "files",
)

REQUIRED_FILE_KEYS = (
    "layers",
    "design_rules",
    "process_flow",
    "routing_profile",
    "device_presets",
)


def validate_manifest(manifest):
    manifest = Dict(manifest)
    errors = []

    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            errors.append(f"Missing manifest key: {key}")

    version = manifest.get("version")
    if version and not SEMVER_PATTERN.match(str(version)):
        errors.append(f"Invalid version format: {version}")

    schema_version = manifest.get("schema_version")
    if schema_version and not SEMVER_PATTERN.match(str(schema_version)):
        errors.append(f"Invalid schema_version format: {schema_version}")

    files = Dict(manifest.get("files", {}))
    for key in REQUIRED_FILE_KEYS:
        if key not in files:
            errors.append(f"Missing files.{key} entry in manifest")

    compatibility = Dict(manifest.get("compatibility", {}))
    if not compatibility:
        errors.append("Missing compatibility object")
    else:
        if "edaq_min" not in compatibility:
            errors.append("Missing compatibility.edaq_min")
        if "edaq_max" not in compatibility:
            errors.append("Missing compatibility.edaq_max")

    return Dict(valid=(len(errors) == 0), errors=errors)
