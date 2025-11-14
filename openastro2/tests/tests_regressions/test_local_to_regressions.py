import inspect
import json

import pytest

from openastro2.openastro2 import openAstro, openAstroSettings


def auto_serialize(obj, max_depth=6, current_depth=0, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return "<CYCLIC REFERENCE>"
    if current_depth > max_depth:
        return f"<MAX_DEPTH {current_depth}>"

    seen.add(obj_id)
    try:
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        if isinstance(obj, (list, tuple)):
            return [auto_serialize(item, max_depth, current_depth + 1, seen) for item in obj]
        if isinstance(obj, dict):
            return {
                key: auto_serialize(value, max_depth, current_depth + 1, seen)
                for key, value in obj.items()
                if isinstance(key, (str, int, float, bool))
            }
        if hasattr(obj, "__dict__"):
            return {
                key: auto_serialize(value, max_depth, current_depth + 1, seen)
                for key, value in obj.__dict__.items()
                if not key.startswith("_")
            }
        return str(obj)
    finally:
        seen.discard(obj_id)


def _build_events():
    event1 = openAstro.event_dt_str(
        "Vladimir Visotskiy",
        dt_str="1938-01-25 09:40:00",
        timezone=3,
        location="Moscow",
        geolat=55.78472277151802,
        geolon=37.628137530436106,
    )
    event2 = openAstro.event_dt_str(
        "Enrolled in the Taganka Theatre",
        dt_str="1964-09-10 12:00:00",
        timezone=3,
        location="Moscow",
        geolat=55.78472277151802,
        geolon=37.628137530436106,
    )
    return event1, event2


EVENT1, EVENT2 = _build_events()
SETTINGS = openAstroSettings().read_settings(
    settings_path="settings/settings_transit_with_cuspids.json"
)
LOCAL_TO_METHODS = [
    name
    for name, func in inspect.getmembers(openAstro, predicate=inspect.isfunction)
    if name.startswith("localTo")
]


def _build_kwargs(oa, signature):
    kwargs = {}
    for name in signature.parameters:
        if name == "self":
            continue
        if name == "solaryearsecs":
            kwargs[name] = 31556925.51
        elif name == "dt":
            kwargs[name] = oa.dt2_utc
        else:
            kwargs[name] = getattr(oa, name)
    return kwargs


def test_local_to_functions_regression(file_regression):
    results = {}
    for method_name in sorted(LOCAL_TO_METHODS):
        oa = openAstro(EVENT1, EVENT2, type="Transit", settings=SETTINGS)
        oa.calcAstro()
        func = getattr(oa, method_name)
        signature = inspect.signature(func)
        kwargs = _build_kwargs(oa, signature)
        result = func(**kwargs)
        results[method_name] = auto_serialize(result)

    json_content = json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True)
    file_regression.check(
        json_content,
        basename="local_to_functions",
        extension=".json",
        encoding="utf-8",
    )
