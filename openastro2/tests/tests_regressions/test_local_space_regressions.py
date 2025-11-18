import inspect
import json
from datetime import datetime

import json5
import numpy as np
import pandas as pd
import pydeck as pdk
import pytest

from openastro2.openastro2 import openAstro, openAstroSettings


def _build_events():
	from openastro2.openastro2 import openAstro as OA

	event1 = OA.event_dt_str(
		"Vladimir Visotskiy",
		dt_str="1938-01-25 09:40:00",
		timezone=3,
		location="Moscow",
		geolat=55.78472277151802,
		geolon=37.628137530436106,
	)
	event2 = OA.event_dt_str(
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
LOCAL_SPACE_METHODS = [
	name
	for name in dir(openAstro)
	if name.startswith("makeLocalSpace")
]


def _serialize_local_space_output(value):
	if isinstance(value, pdk.Layer):
		layer_payload = json5.loads(value.to_json())
		layer_payload.pop("id", None)
		return layer_payload
	if isinstance(value, pd.DataFrame):
		return value.to_dict(orient="records")
	if isinstance(value, pd.Series):
		return value.to_dict()
	if isinstance(value, np.ndarray):
		return value.tolist()
	if isinstance(value, np.generic):
		return value.item()
	if isinstance(value, datetime):
		return value.isoformat()
	if isinstance(value, dict):
		return {key: _serialize_local_space_output(val) for key, val in value.items()}
	if isinstance(value, (list, tuple)):
		return [_serialize_local_space_output(item) for item in value]
	return value


def _build_kwargs(func, dt, lat, lon):
	kwargs = {}
	sig = inspect.signature(func)
	for name, param in sig.parameters.items():
		if name == "self":
			continue
		if name == "dt":
			kwargs["dt"] = dt
		elif name == "lat":
			kwargs["lat"] = lat
		elif name == "lon":
			kwargs["lon"] = lon
		elif name == "type_tr":
			kwargs["type_tr"] = "Radix"
		elif name == "type":
			kwargs["type"] = "Sky"
		elif param.default is inspect._empty:
			raise RuntimeError(f"Parameter '{name}' in {func.__name__} requires a value")
	return kwargs


def test_local_space_functions_regression(file_regression):
	oa = openAstro(EVENT1, EVENT2, type="Transit", settings=SETTINGS)
	oa.calcAstro()
	dt = oa.dt2_utc
	lat = oa.geolat
	lon = oa.geolon

	results = {}
	for name in sorted(LOCAL_SPACE_METHODS):
		func = getattr(oa, name)
		kwargs = _build_kwargs(func, dt, lat, lon)
		result = func(**kwargs)
		results[name] = _serialize_local_space_output(result)

	json_content = json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True)
	file_regression.check(
		json_content,
		basename="local_space_functions",
		extension=".json",
		encoding="utf-8",
	)
