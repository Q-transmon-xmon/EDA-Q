import argparse
import json
import re
from pathlib import Path


DEFAULT_SOURCE = Path("line1_flipchip_process_grouped_by_step.json")
DEFAULT_TARGET = Path("pdk/foundries/sc_flipchip/line1/1.0.0")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _parse_um(text):
    if not text:
        return None
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*um", str(text), re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


def _normalize_related_layer(raw):
    if not raw:
        return None
    text = str(raw)
    match = re.search(r"(layer\d+)", text, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return text


def convert(source_path, target_dir):
    source_path = Path(source_path)
    target_dir = Path(target_dir)

    data = _load_json(source_path)

    layers_in = data.get("layer_information", [])
    rules_in = data.get("design_rules", {})
    process_in = data.get("process_list", [])

    layers_out = {
        "schema_version": "1.0.0",
        "layers": [],
    }
    for idx, layer in enumerate(layers_in, start=1):
        layers_out["layers"].append(
            {
                "layer_id": layer.get("layer_id"),
                "name": layer.get("layer_name"),
                "purpose": layer.get("purpose"),
                "process_range": layer.get("process_range"),
                "gds_layer": idx,
                "gds_datatype": 0,
            }
        )

    dcr_rule = rules_in.get("DCR_rules", {})
    design_rules_out = {
        "schema_version": "1.0.0",
        "hard_rules": {
            "min_linewidth_um": {
                "scope": "layer1",
                "value": _parse_um(dcr_rule.get("minimum_linewidth")),
                "source": "Design Rules - DCR Rules - Minimum Linewidth",
            },
            "min_spacing_um": {
                "scope": "layer1",
                "value": _parse_um(dcr_rule.get("minimum_spacing")),
                "source": "Design Rules - DCR Rules - Minimum Spacing",
            },
        },
        "guidance_rules": {
            "metal_stack_relation": dcr_rule.get("metal_stack_relation"),
            "jj_size_rule": rules_in.get("JJ_size_rules"),
            "bridge_width_requirement": rules_in.get("bridge_width_requirement"),
            "alignment_mark": rules_in.get("required_alignment_marks"),
            "opc": rules_in.get("OPC"),
        },
    }

    process_flow_out = {
        "schema_version": "1.0.0",
        "processes": [],
    }
    for process in process_in:
        steps = []
        for step in process.get("step_list", []):
            steps.append(
                {
                    "step_no": str(step.get("step_no", "")),
                    "name": step.get("step_name"),
                    "equipment": step.get("equipment"),
                }
            )

        process_flow_out["processes"].append(
            {
                "process_no": int(process.get("process_no")),
                "name": process.get("process_name"),
                "related_layer_id": _normalize_related_layer(process.get("related_layer")),
                "target": process.get("process_target"),
                "steps": steps,
            }
        )

    routing_profile_out = {
        "schema_version": "1.0.0",
        "profiles": {
            "default": {
                "routing": {
                    "method": "Flipchip_routing",
                    "chip_name": "chip0",
                    "pins_type": "LaunchPad",
                    "tmls_type": "TransmissionPath",
                    "ctls_type": "ChargeLine",
                    "pins_geometric_ops": {
                        "trace_width": 0.0,
                        "trace_gap": 0.0,
                        "taper_height": 0.0,
                        "pad_width": 0.0,
                        "pad_height": 0.0,
                        "pad_gap": 0.0,
                        "orientation": 0,
                        "start_straight": 0.0,
                        "distance_to_chip": 0.0,
                        "distance_to_qubits": 0.0
                    }
                },
                "generation_defaults": {
                    "qubits": {
                        "qubits_type": "Transmon",
                        "chip_name": "chip0",
                        "dist": 0.0,
                    },
                    "coupling_lines": {
                        "cpls_type": "CouplingLineStraight",
                        "chip_name": "chip0",
                    },
                    "readout_lines": {
                        "rdls_type": "ReadoutCavityFlipchip",
                        "chip_name": "chip0",
                    },
                    "chips": {
                        "chip_name": "chip0",
                        "chip_type": "RecChip",
                    },
                },
            }
        },
    }

    device_presets_out = {
        "schema_version": "1.0.0",
        "layer_binding": {
            "qubits": "layer1",
            "coupling_lines": "layer1",
            "readout_lines": "layer1",
            "control_lines": "layer1",
            "transmission_lines": "layer1",
            "jj_jodan": "layer2",
            "air_bridges": "layer3",
            "cover_bridges": "layer4",
            "indium_bumps": "layer5",
        },
        "recommended_types": {
            "qubits": "Transmon",
            "readout_lines": "ReadoutCavityFlipchip",
            "pins": "LaunchPad",
            "control_lines": "ChargeLine",
            "transmission_lines": "TransmissionPath",
            "jj_jodan": "JjDolan1",
            "indium_bumps": "IndiumBump",
        },
    }

    manifest_out = {
        "pdk_id": "sc_flipchip_line1",
        "foundry": "sc_flipchip",
        "line": "line1",
        "version": "1.0.0",
        "schema_version": "1.0.0",
        "description": "Superconducting flipchip process line-1 PDK converted from foundry process flow.",
        "status": "draft",
        "compatibility": {
            "edaq_min": "3.0.0",
            "edaq_max": "3.x",
        },
        "files": {
            "layers": "layers.json",
            "design_rules": "design_rules.json",
            "process_flow": "process_flow.json",
            "routing_profile": "routing_profile.json",
            "device_presets": "device_presets.json",
        },
    }

    _write_json(target_dir / "manifest.json", manifest_out)
    _write_json(target_dir / "layers.json", layers_out)
    _write_json(target_dir / "design_rules.json", design_rules_out)
    _write_json(target_dir / "process_flow.json", process_flow_out)
    _write_json(target_dir / "routing_profile.json", routing_profile_out)
    _write_json(target_dir / "device_presets.json", device_presets_out)
    _write_json(target_dir / "source" / "process_raw.json", data)

    print(f"PDK package written to: {target_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--target", default=str(DEFAULT_TARGET))
    args = parser.parse_args()
    convert(source_path=args.source, target_dir=args.target)


if __name__ == "__main__":
    main()
