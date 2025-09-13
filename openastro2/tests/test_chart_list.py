from typing import Any
import pytest

from openastro2.openastro2 import openAstro


# from your_module import openAstro2  # Замените на ваш реальный модуль

FULL_CHART_TYPES = [
    "Radix",
    "Transit",
    "SProgression",
    "Direction",
    "Solar",
    # "DirectionWithEnd",
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
    # "SProgressionPast",
    "FixarPlanetMoment",
    "FixarPlanetRadix",
    "FixarPlanetTransit",
    "FixarEarthMoment",
    "FixarEarthTransit"
]
@pytest.mark.parametrize("astro_type", FULL_CHART_TYPES)
def test_openastro_types(astro_type: str) -> None:
    # Инициализация событий с фиксированными параметрами
    event1 = openAstro.event_dt_str("Владимир Высоцкий", dt_str="1938-01-25 09:40:00", timezone=3, location="Москва",
                                    geolat=55.78472277151802, geolon=37.628137530436106)
    event2 = openAstro.event_dt_str("Смерть", dt_str="1980-07-25 09:40:00", timezone=3, location="Москва",
                                    geolat=55.78472277151802, geolon=37.628137530436106)

    # Создание объекта без передачи args
    oa = openAstro(event1, event2, type=astro_type)

    # Базовые проверки
    assert oa is not None
    assert hasattr(oa, 'hour')
    # assert hasattr(oa, 'planets_degree_ut')

    # Проверка типов данных
    assert isinstance(oa.hour, (int, float, str))
    # assert isinstance(oa.planets_degree_ut, dict)

    # Проверка генерации SVG
    svg_content = oa.makeSVG2()
    assert isinstance(svg_content, str)
    # assert svg_content.startswith('<svg')
    # assert '"http://www.w3.org/2000/svg"' in svg_content
    assert '<svg' in svg_content
    assert '</svg>' in svg_content
