import copy
from addict import Dict


def _get_profile(context, profile="default"):
    context = Dict(context)
    profiles = Dict(context.routing_profile.get("profiles", {}))
    if profile not in profiles:
        available = ", ".join(profiles.keys())
        raise ValueError(f"Routing profile '{profile}' not found. Available: {available}")
    return Dict(profiles[profile])


def get_generation_defaults(context, component, profile="default"):
    profile_obj = _get_profile(context=context, profile=profile)
    defaults = Dict(profile_obj.get("generation_defaults", {}))
    return copy.deepcopy(Dict(defaults.get(component, {})))


def apply_generation_defaults(gene_ops, context, component, profile="default"):
    merged = Dict()
    defaults = get_generation_defaults(context=context, component=component, profile=profile)
    for key, value in defaults.items():
        merged[key] = copy.deepcopy(value)
    for key, value in Dict(gene_ops).items():
        merged[key] = copy.deepcopy(value)
    return copy.deepcopy(merged)


def get_routing_defaults(context, profile="default"):
    profile_obj = _get_profile(context=context, profile=profile)
    return copy.deepcopy(Dict(profile_obj.get("routing", {})))


def apply_routing_defaults(routing_ops, context, profile="default"):
    merged = Dict()
    defaults = get_routing_defaults(context=context, profile=profile)
    for key, value in defaults.items():
        merged[key] = copy.deepcopy(value)
    for key, value in Dict(routing_ops).items():
        merged[key] = copy.deepcopy(value)
    return copy.deepcopy(merged)
