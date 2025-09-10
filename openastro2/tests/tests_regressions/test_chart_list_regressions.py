import pytest
import json
from openastro2.openastro2 import openAstro
from openastro2.openastro2 import openAstroSettings
# from openastro2 import openAstro
# from openastro2 import openAstroSettings


def auto_serialize(obj, max_depth=6, current_depth=0, seen=None):
    """
    Автоматически сериализует объект в структуру, совместимую с JSON.
    Пропускает приватные атрибуты и несериализуемые типы.
    """
    if seen is None:
        seen = set()

    # Защита от циклических ссылок
    obj_id = id(obj)
    if obj_id in seen:
        return "<CYCLIC REFERENCE>"
    if current_depth > max_depth:
        return f"<MAX_DEPTH {current_depth}>"

    seen.add(obj_id)

    try:
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [auto_serialize(item, max_depth, current_depth + 1, seen) for item in obj]
        elif isinstance(obj, dict):
            return {
                key: auto_serialize(value, max_depth, current_depth + 1, seen)
                for key, value in obj.items()
                if isinstance(key, (str, int, float))  # Ключи должны быть сериализуемы
            }
        elif hasattr(obj, "__dict__"):
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith("_"):  # Только публичные атрибуты
                    result[key] = auto_serialize(value, max_depth, current_depth + 1, seen)
            return result
        else:
            # Попытка привести к строке, если не получается — заменяем заглушкой
            return str(obj)
    except Exception as e:
        return f"<NOT_SERIALIZABLE: {type(obj).__name__} ({str(e)})>"
    finally:
        seen.discard(obj_id)

FULL_CHART_TYPES = [
    "Radix",
    "Transit",
    "SProgression",
    "Direction",
    "Solar",
    "DirectionPast",
    "DirectionRealPast",
    "DirectionRealFuture",
    "SolarNext",
    "SolarPrev",
    "SolarNear",
    "NewMoonNext",
    "NewMoonPrev",
    "FullMoonNext",
    "FullMoonPrev",
    "Lunar",
    "AscReturn",
    "EarthReturn",
    "GeoZodiac",
    "FixarPlanetMoment",
    "FixarPlanetRadix",
    "FixarPlanetTransit",
    "FixarEarthMoment",
    "FixarEarthTransit"
]


event1 = openAstro.event_dt_str("Vladimir Visotskiy", dt_str="1938-01-25 09:40:00", timezone=3, location="Moscow",
                                geolat=55.78472277151802, geolon=37.628137530436106)
event2 = openAstro.event_dt_str("Enrolled in the Taganka Theatre", dt_str="1964-09-10 12:00:00", timezone=3, location="Moscow",
                                geolat=55.78472277151802, geolon=37.628137530436106)
# event2 = openAstro.event_dt_str("Death", dt_str="1980-07-25 09:40:00", timezone=3, location="Moscow",
#                                 geolat=55.78472277151802, geolon=37.628137530436106)

oas = openAstroSettings()
# settings = oas.read_settings(settings_path='settings/settings2.json')
# settings = oas.read_settings(settings_path='settings/settings2-square.json')
# settings = oas.read_settings(settings_path='settings/settings_natal.json')
settings = oas.read_settings(settings_path='settings/settings_transit_with_cuspids.json')
print(settings)

@pytest.mark.parametrize("astro_type", FULL_CHART_TYPES)
def test_openastro_types_svg(astro_type, file_regression):

    oa = openAstro(event1, event2, type=astro_type, settings=settings)
    svg_content = oa.makeSVG2()
    # Проверка SVG
    file_regression.check(
        svg_content,
        basename=f"test_openastro_types[{astro_type}]",
        extension=".svg",
        encoding='utf-8'
    )


@pytest.mark.parametrize("astro_type", FULL_CHART_TYPES)
def test_openastro_types_svg_obtained(astro_type, file_regression):

    oa = openAstro(event1, event2, type=astro_type, settings=settings)
    svg_content = oa.makeSVG2()
    # Проверка SVG
    file_regression.check(
        svg_content,
        basename=f"obtained/test_openastro_types[{astro_type}]",
        extension=".svg",
        encoding='utf-8'
    )



@pytest.mark.parametrize("astro_type", FULL_CHART_TYPES)
def test_openastro_types_json(astro_type, file_regression):

    oa = openAstro(event1, event2, type=astro_type, settings=settings)
    svg_content = oa.makeSVG2()
    # Автоматическая сериализация объектов
    serialized_data = {
        # "event1": auto_serialize(event1),
        # "event2": auto_serialize(event2),
        "oa": auto_serialize(oa),
    }
    # Преобразуем в JSON
    json_content = json.dumps(serialized_data, indent=2, ensure_ascii=False, sort_keys=True)

    # Сохраняем
    file_regression.check(
        json_content,
        basename=f"test_openastro_types[{astro_type}].data",
        extension=".json",
        encoding='utf-8'
    )


@pytest.mark.parametrize("astro_type", FULL_CHART_TYPES)
def test_openastro_types_json_obtained(astro_type, file_regression):

    oa = openAstro(event1, event2, type=astro_type, settings=settings)
    svg_content = oa.makeSVG2()
    # Автоматическая сериализация объектов
    serialized_data = {
        # "event1": auto_serialize(event1),
        # "event2": auto_serialize(event2),
        "oa": auto_serialize(oa),
    }
    # Преобразуем в JSON
    json_content = json.dumps(serialized_data, indent=2, ensure_ascii=False, sort_keys=True)

    # Сохраняем
    file_regression.check(
        json_content,
        basename=f"obtained/test_openastro_types[{astro_type}].data",
        extension=".json",
        encoding='utf-8'
    )


