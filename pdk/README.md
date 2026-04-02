# EDA-Q PDK Platform User Manual

This directory is the extensible PDK platform for EDA-Q, designed to decouple "foundry process facts" from "EDA design invocation", achieving the following capabilities:

1. Version-controlled process management (by foundry/line/version).
2. Reuse the same process across multiple projects.
3. Onboard new production lines with minimal core code changes, only adding PDK data packages.

## 1. Overall Architecture

The current design uses a three-layer model:

1. **Foundry PDK**: Foundry process facts, generally append-only.
2. **Platform PDK**: Mapping to EDA-Q default types, routing strategies, and rule validation.
3. **Project Overlay**: Project-level parameter overrides (loading and merging supported).

## 2. Directory Structure

```text
pdk/
  core/
    __init__.py
    schema.py              # manifest structure validation
    registry.py            # PDK discovery and version resolution
    loader.py              # PDK loading and context assembly
    overlay.py             # Project Overlay discovery, loading, merging
    adapter.py             # Default parameter adaptation (generation/routing)
    validator.py           # Design and PDK consistency validation
  tools/
    convert_line1_process_json.py  # Process JSON -> Standard PDK package
    pdk_doctor.py                  # PDK package health check tool
  foundries/
    sc_flipchip/
      line1/
        1.0.0/
          manifest.json
          layers.json
          design_rules.json
          process_flow.json
          routing_profile.json
          device_presets.json
          source/
            process_raw.json
  projects/
    demo_flipchip_project/
      overlay.json
```

## 3. Current Implemented Capabilities

### 3.1 API Integration

The PDK platform is integrated into the `Design` class, providing the following methods:

- `load_pdk(pdk_id, version=None, profile="default")`: Load a PDK package and return manifest information.
- `get_pdk_generation_defaults(component)`: Get default parameters for generating specific components (qubits, readout_lines, chips, etc.).
- `validate_pdk(stage="pre_layout")`: Validate design consistency with PDK at different stages (pre_layout, pre_route, pre_tapeout).
- `show_available_overlays()`: List all available project overlays.
- `load_project_overlay(overlay_id)`: Load and apply a project overlay.

### 3.2 Default Parameter Injection Strategy

- **Generation defaults**: Currently recommend explicit parameter passing. Use `get_pdk_generation_defaults(component)` to retrieve defaults, then pass them explicitly to `generate_*` methods.
- **Routing defaults**: Automatically merged when calling `gds.routing()`. The system internally calls `_merge_pdk_routing_defaults()` to inject PDK-defined routing parameters.

### 3.3 Validation Capabilities

The `validate_pdk(stage)` method supports three validation stages:

1. **pre_layout**: Checks if qubits and chips exist.
2. **pre_route**: Additionally checks if readout lines exist and validates routing default chip_name.
3. **pre_tapeout**: Additionally checks if JJ and indium bump components match process requirements.

Validation reports include:
- `valid`: Boolean indicating overall validation status.
- `errors`: List of error messages (validation fails if non-empty).
- `warnings`: List of warning messages (does not affect validation status).
- `infos`: List of informational messages.

### 3.4 PDK Doctor Tool

`pdk_doctor.py` is a standalone command-line tool for batch checking PDK package integrity:

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id sc_flipchip_line1 \
  --version 1.0.0 \
  --overlay-id demo_flipchip_project \
  --json-out reports/doctor_report.json
```

## 4. pyoccenv Standard Execution Method

All PDK-related code should be executed in the `pyoccenv` environment:

```bash
# Activate environment
conda activate pyoccenv

# Run conversion tool
python pdk/tools/convert_line1_process_json.py \
  --source source_process.json \
  --target pdk/foundries/sc_flipchip/line1/1.0.0

# Run PDK doctor
python pdk/tools/pdk_doctor.py --pdk-id sc_flipchip_line1
```

For Jupyter Notebooks, select `pyoccenv` as the kernel.

## 5. Process JSON to PDK Package Conversion

Use `convert_line1_process_json.py` to convert foundry-provided process JSON files into standard PDK packages:

```bash
python pdk/tools/convert_line1_process_json.py \
  --source 产线一期倒装芯片流程_按工序分组.json \
  --target pdk/foundries/sc_flipchip/line1/1.0.0
```

This tool will generate:
- `manifest.json`: PDK metadata and file index
- `layers.json`: Layer definitions
- `design_rules.json`: Design rules (hard rules and guidance rules)
- `process_flow.json`: Process flow steps
- `routing_profile.json`: Routing profiles and generation defaults
- `device_presets.json`: Device preset parameters
- `source/`: Directory containing original source files

## 6. PDK Data File Descriptions

### 6.1 manifest.json

PDK package metadata and file index. Required fields:

- `pdk_id`: Unique PDK identifier (format: `{foundry}_{line}`)
- `foundry`: Foundry name
- `line`: Production line name
- `version`: Semantic version (e.g., "1.0.0")
- `schema_version`: PDK schema version
- `compatibility`: EDA-Q version compatibility range
  - `edaq_min`: Minimum compatible EDA-Q version
  - `edaq_max`: Maximum compatible EDA-Q version
- `files`: Mapping of data file types to relative paths

Example:
```json
{
  "pdk_id": "sc_flipchip_line1",
  "foundry": "sc_flipchip",
  "line": "line1",
  "version": "1.0.0",
  "schema_version": "1.0.0",
  "compatibility": {
    "edaq_min": "3.0.0",
    "edaq_max": "3.x"
  },
  "files": {
    "layers": "layers.json",
    "design_rules": "design_rules.json",
    "process_flow": "process_flow.json",
    "routing_profile": "routing_profile.json",
    "device_presets": "device_presets.json"
  }
}
```

### 6.2 layers.json

Layer definitions including layer IDs, names, purposes, and GDS mapping.

Structure:
- `schema_version`: Schema version
- `layers`: Array of layer objects
  - `layer_id`: Layer identifier
  - `name`: Layer name
  - `purpose`: Layer purpose/function
  - `process_range`: Applicable process range
  - `gds_layer`: GDS layer number
  - `gds_datatype`: GDS datatype number

### 6.3 design_rules.json

Design rules divided into hard rules and guidance rules.

- **hard_rules**: Mandatory rules that must be satisfied
  - `min_linewidth_um`: Minimum line width constraint
  - `min_spacing_um`: Minimum spacing constraint
  - Each rule includes: `scope`, `value`, `source`

- **guidance_rules**: Recommended rules and best practices
  - `metal_stack_relation`: Metal layer stacking relationships
  - `jj_size_rule`: Josephson junction size rules
  - `bridge_width_requirement`: Bridge width requirements
  - `alignment_mark`: Alignment mark requirements
  - `opc`: Optical proximity correction guidelines

### 6.4 process_flow.json

Complete process flow definition including all fabrication steps.

Structure:
- `schema_version`: Schema version
- `processes`: Array of process objects
  - `name`: Process name
  - `category`: Process category
  - `step_list`: Array of fabrication steps
    - `step_no`: Step number
    - `step_name`: Step name
    - `operation`: Operation description
    - `related_layer`: Related layer identifier
    - `parameters`: Process parameters

### 6.5 routing_profile.json

Routing profiles and generation default parameters.

Structure:
- `schema_version`: Schema version
- `profiles`: Dictionary of profile objects (e.g., "default")
  - `routing`: Routing default parameters
    - `method`: Routing method (e.g., "Flipchip_routing")
    - `chip_name`: Target chip name
    - `pins_type`: Pin type
    - `tmls_type`: Transmission line type
    - `ctls_type`: Control line type
    - `pins_geometric_ops`: Pin geometry parameters
  - `generation_defaults`: Component generation defaults
    - `qubits`: Qubit generation defaults
    - `readout_lines`: Readout line generation defaults
    - `chips`: Chip generation defaults

### 6.6 device_presets.json

Device preset parameters for common device types.

Structure:
- `schema_version`: Schema version
- `devices`: Dictionary of device preset objects
  - Device-specific parameters and configurations

## 7. Usage Examples in EDA-Q

### 7.1 Basic Workflow

```python
from api.design import Design

# Create design instance
design = Design()

# Load PDK
manifest = design.load_pdk("sc_flipchip_line1", version="1.0.0", profile="default")
print(f"Loaded: {manifest['pdk_id']} {manifest['version']}")

# Get generation defaults
q_defaults = dict(design.get_pdk_generation_defaults("qubits"))
rd_defaults = dict(design.get_pdk_generation_defaults("readout_lines"))
chip_defaults = dict(design.get_pdk_generation_defaults("chips"))

# Generate design components (explicitly pass defaults)
design.generate_topology(topo_col=6, topo_row=6)
design.generate_qubits(topology=True, **q_defaults)
design.generate_readout_lines(qubits=True, **rd_defaults)
design.generate_chip(qubits=True, **chip_defaults)

# Routing (auto-injects routing defaults)
design.gds.routing()

# Validate at different stages
pre_layout_report = design.validate_pdk(stage="pre_layout")
pre_route_report = design.validate_pdk(stage="pre_route")
pre_tapeout_report = design.validate_pdk(stage="pre_tapeout")

print(f"pre_layout valid: {pre_layout_report['valid']}")
print(f"pre_route valid: {pre_route_report['valid']}")
print(f"pre_tapeout valid: {pre_tapeout_report['valid']}")

# Export GDS
design.gds.save_gds("output.gds")
```

### 7.2 Using Project Overlays

```python
from api.design import Design

design = Design()

# Load base PDK
design.load_pdk("sc_flipchip_line1", version="1.0.0")

# List available overlays
available_overlays = design.show_available_overlays()
print("Available overlays:", list(available_overlays.keys()))

# Load and apply project overlay
overlay_doc = design.load_project_overlay("demo_flipchip_project")
print(f"Loaded overlay: {overlay_doc['overlay_id']}")

# Overlay parameters are now merged with base PDK
# Routing defaults will reflect overlay modifications
routing_defaults = dict(design._merge_pdk_routing_defaults({}))
print("Routing defaults after overlay:", routing_defaults)

# Continue with design workflow
design.generate_topology(topo_col=6, topo_row=6)
# ... rest of design flow
```

## 8. pdk doctor Usage Examples

### 8.1 Check Single PDK Package

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id sc_flipchip_line1 \
  --version 1.0.0
```

### 8.2 Check All Versions of a PDK

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id sc_flipchip_line1
```

### 8.3 Check All PDK Packages

```bash
python pdk/tools/pdk_doctor.py
```

### 8.4 Check with Project Overlay

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id sc_flipchip_line1 \
  --version 1.0.0 \
  --overlay-id demo_flipchip_project
```

### 8.5 Output JSON Report

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id sc_flipchip_line1 \
  --version 1.0.0 \
  --json-out reports/doctor_report.json
```

### 8.6 Treat Warnings as Failures

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id sc_flipchip_line1 \
  --fail-on-warning
```

## 9. Validation Report Interpretation

### 9.1 Report Structure

```python
{
  "valid": True,           # Overall validation status
  "stage": "pre_route",    # Validation stage
  "pdk_id": "sc_flipchip_line1",
  "pdk_version": "1.0.0",
  "errors": [],            # Error messages (validation fails if non-empty)
  "warnings": [],          # Warning messages (does not affect validation)
  "infos": []              # Informational messages
}
```

### 9.2 Common Error Messages

- `"No qubits found in current design."`: Must generate qubits before validation.
- `"No chips found in current design."`: Must generate chips before validation.
- `"PDK context missing manifest"`: PDK package is corrupted or incomplete.
- `"Missing manifest key: {key}"`: Required manifest field is missing.

### 9.3 Common Warning Messages

- `"No readout lines found before routing/tapeout."`: Readout lines should be generated before routing.
- `"Default routing chip_name '{name}' not found in current chips."`: The chip specified in routing defaults does not exist.
- `"PDK process includes JJ, but design has no jj_jodan components."`: Process supports JJ but design doesn't use it.
- `"PDK process includes indium bump, but design has no indium_bumps."`: Process supports indium bumps but design doesn't use them.

### 9.4 Common Info Messages

- `"Hard rule min_linewidth_um={value} requires geometry-level DRC."`: Indicates that geometry-level DRC checking is needed.
- `"Hard rule min_spacing_um={value} requires geometry-level DRC."`: Indicates that spacing DRC checking is needed.

## 10. Recommended Workflow for Adding New Foundries/Production Lines

### 10.1 Prepare Source Data

Obtain the foundry's process flow JSON file, typically containing:
- Layer information
- Design rules
- Process flow steps
- Device parameters

### 10.2 Run Conversion Tool

```bash
python pdk/tools/convert_line1_process_json.py \
  --source path/to/foundry_process.json \
  --target pdk/foundries/{foundry}/{line}/{version}
```

### 10.3 Review Generated Files

Check the generated PDK package files:
- Verify `manifest.json` metadata is correct
- Review `layers.json` layer definitions
- Validate `design_rules.json` rules are complete
- Check `process_flow.json` process steps
- Adjust `routing_profile.json` defaults as needed
- Configure `device_presets.json` device parameters

### 10.4 Run PDK Doctor

```bash
python pdk/tools/pdk_doctor.py \
  --pdk-id {foundry}_{line} \
  --version {version}
```

Fix any errors or warnings reported by the doctor tool.

### 10.5 Create Test Design

Create a test design using the new PDK:

```python
from api.design import Design

design = Design()
design.load_pdk("{foundry}_{line}", version="{version}")
# ... generate test design
report = design.validate_pdk(stage="pre_tapeout")
assert report["valid"], f"Validation failed: {report['errors']}"
```

### 10.6 Create Project Overlay (Optional)

If project-specific parameter overrides are needed, create an overlay:

```json
{
  "overlay_id": "my_project",
  "description": "Project-specific parameter overrides",
  "base_pdk": {
    "pdk_id": "{foundry}_{line}",
    "version": "{version}"
  },
  "target_profile": "default",
  "overrides": {
    "routing_profile": {
      "profiles": {
        "default": {
          "routing": {
            "chip_name": "custom_chip"
          }
        }
      }
    }
  }
}
```

Save to `pdk/projects/my_project/overlay.json`.

### 10.7 Document and Version Control

- Add documentation for the new PDK package
- Commit all PDK files to version control
- Tag the commit with the PDK version
- Update project documentation with usage examples

## 11. Known Boundaries and Future Plans

### 11.1 Current Limitations

1. **Generation defaults**: Currently require explicit parameter passing. Auto-injection is not yet implemented to avoid unexpected behavior.

2. **Validation scope**: Current validation focuses on component existence and basic consistency. Geometry-level DRC is not yet integrated.

3. **Profile switching**: While multiple profiles are supported in the data structure, runtime profile switching is not fully tested.

4. **Overlay merging**: Deep merging is supported, but complex nested structure conflicts may require manual resolution.

5. **Conversion tool specificity**: `convert_line1_process_json.py` is tailored for a specific JSON format. New foundries may require custom conversion scripts.

### 11.2 Planned Enhancements

1. **Enhanced validation**: Integrate geometry-level DRC checking with hard rules.

2. **Auto-injection for generation**: Implement safe auto-injection of generation defaults with explicit opt-out mechanism.

3. **Profile management**: Add runtime profile switching and profile inheritance capabilities.

4. **Conversion framework**: Develop a generic conversion framework to support multiple foundry data formats.

5. **Version migration**: Add tools for migrating designs between PDK versions.

6. **Documentation generation**: Auto-generate PDK documentation from package metadata.

7. **CI/CD integration**: Add automated PDK validation in continuous integration pipelines.

8. **Web interface**: Develop a web-based PDK browser and validator.

## 12. Troubleshooting

### 12.1 Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pdk'`

**Solution**: Ensure the current working directory is in the repository root or its subdirectory. The PDK module uses relative imports.

**Issue**: `validate_pdk` shows errors about missing components

**Solution**: Ensure all required components are generated before validation:
- `pre_layout`: Requires qubits and chips
- `pre_route`: Additionally requires readout lines
- `pre_tapeout`: May require JJ and indium bumps depending on process

**Issue**: Overlay application fails with base mismatch error

**Solution**: Check that `base_pdk.pdk_id` and `base_pdk.version` in the overlay match the currently loaded PDK. Use `--no-strict-base` flag to bypass this check if needed.

**Issue**: Routing fails with missing parameters

**Solution**: Ensure the PDK's `routing_profile.json` contains all required routing parameters. Check the routing method compatibility with your design.

**Issue**: `pdk_doctor` reports schema validation errors

**Solution**: Verify that all required fields are present in `manifest.json` and that version numbers follow semantic versioning (X.Y.Z format).

### 12.2 Getting Help

For additional support:
1. Check the demo notebook: `pdk/demo/pdk_full_workflow_demo.ipynb`
2. Review example PDK packages in `pdk/foundries/`
3. Examine example overlays in `pdk/projects/`
4. Run `pdk_doctor` with `--json-out` for detailed diagnostic information

## 13. References

- **Demo Notebook**: `pdk/demo/pdk_full_workflow_demo.ipynb` - Complete workflow demonstration
- **Example PDK**: `pdk/foundries/sc_flipchip/line1/1.0.0/` - Reference PDK package structure
- **Example Overlay**: `pdk/projects/demo_flipchip_project/overlay.json` - Reference overlay structure
- **Core Modules**:
  - `pdk/core/registry.py` - PDK discovery and version resolution
  - `pdk/core/loader.py` - PDK loading and context assembly
  - `pdk/core/validator.py` - Design validation logic
  - `pdk/core/adapter.py` - Default parameter adaptation
  - `pdk/core/overlay.py` - Project overlay management
  - `pdk/core/schema.py` - Manifest validation

## 14. Contributing

When contributing new PDK packages or enhancements:

1. Follow the established directory structure and naming conventions
2. Ensure all required files are present and valid
3. Run `pdk_doctor` to verify package integrity
4. Create test cases demonstrating the new functionality
5. Update documentation to reflect changes
6. Submit changes with clear commit messages

## 15. License and Contact

This PDK platform is part of the EDA-Q project. For questions, issues, or contributions, please contact the EDA-Q development team.

