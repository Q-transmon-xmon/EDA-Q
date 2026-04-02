import copy
from addict import Dict

from pdk.core.schema import validate_manifest
from pdk.core.adapter import get_routing_defaults


def _append_level(report, level, msg):
    report[level].append(msg)


def validate_pdk_context(context):
    context = Dict(context)
    report = Dict(
        valid=True,
        errors=[],
        warnings=[],
        infos=[],
    )

    if "manifest" not in context:
        _append_level(report, "errors", "PDK context missing manifest")
    else:
        manifest_report = validate_manifest(context.manifest)
        if not manifest_report.valid:
            report.errors.extend(manifest_report.errors)

    required_sections = ["layers", "design_rules", "process_flow", "routing_profile", "device_presets"]
    for section in required_sections:
        if section not in context:
            _append_level(report, "errors", f"PDK context missing section: {section}")

    report.valid = len(report.errors) == 0
    return report


def validate_gds_against_pdk(gds_ops, context, stage="pre_layout"):
    gds_ops = Dict(copy.deepcopy(gds_ops))
    context = Dict(copy.deepcopy(context))
    report = Dict(
        valid=True,
        stage=stage,
        pdk_id=context.manifest.get("pdk_id", ""),
        pdk_version=context.manifest.get("version", ""),
        errors=[],
        warnings=[],
        infos=[],
    )

    context_report = validate_pdk_context(context)
    if not context_report.valid:
        report.errors.extend(context_report.errors)
        report.valid = False
        return report

    qubits_ops = Dict(gds_ops.get("qubits", {}))
    chips_ops = Dict(gds_ops.get("chips", {}))
    readout_ops = Dict(gds_ops.get("readout_lines", {}))
    jj_ops = Dict(gds_ops.get("jj_jodan", {}))
    indium_ops = Dict(gds_ops.get("indium_bumps", {}))

    if not qubits_ops:
        _append_level(report, "errors", "No qubits found in current design.")
    if not chips_ops:
        _append_level(report, "errors", "No chips found in current design.")

    if stage in ("pre_route", "pre_tapeout") and not readout_ops:
        _append_level(report, "warnings", "No readout lines found before routing/tapeout.")

    process_names = [item.get("name", "") for item in context.process_flow.get("processes", [])]
    process_text = " ".join(process_names)
    if ("Josephson Junction" in process_text) and not jj_ops and stage == "pre_tapeout":
        _append_level(report, "warnings", "PDK process includes JJ, but design has no jj_jodan components.")
    if ("Indium Bump" in process_text) and not indium_ops and stage == "pre_tapeout":
        _append_level(report, "warnings", "PDK process includes indium bump, but design has no indium_bumps.")

    routing_defaults = get_routing_defaults(context=context, profile="default")
    default_chip = routing_defaults.get("chip_name")
    if default_chip and default_chip not in chips_ops:
        _append_level(
            report,
            "warnings",
            f"Default routing chip_name '{default_chip}' not found in current chips.",
        )

    hard_rules = Dict(context.design_rules.get("hard_rules", {}))
    if "min_linewidth_um" in hard_rules:
        _append_level(
            report,
            "infos",
            f"Hard rule min_linewidth_um={hard_rules.min_linewidth_um.get('value')} requires geometry-level DRC.",
        )
    if "min_spacing_um" in hard_rules:
        _append_level(
            report,
            "infos",
            f"Hard rule min_spacing_um={hard_rules.min_spacing_um.get('value')} requires geometry-level DRC.",
        )

    report.valid = len(report.errors) == 0
    return report
