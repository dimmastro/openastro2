from typing import Dict, Any
import json

if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    event1 = openAstro.event("Nikola Tesla", 1856, 7, 10, 0, 0, 0, timezone=1, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    # event2 = openAstro.event("Ill", 1873, 10, 10, 0, 30, 0, timezone=1.36666666, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    # event1 = openAstro.event("Nikola Tesla", 2000, 7, 10, 0, 0, 0, timezone=1, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)

    event2 = openAstro.event("Ill", 2000, 10, 10, 0, 30, 0, timezone=1.36666666, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)

    settings={}
    settings['astrocfg']={}
    settings['astrocfg']['language'] = "ru"
    settings['astrocfg']['round_aspects'] = 0
    settings['settings_svg']={}
    settings['settings_svg']['saveSwgFile'] = 1

    openAstro = openAstro(event1, event2, type="Transit", settings=settings, lang='ru')
    # openAstro = openAstro(event1, event2, type="Radix", settings=settings)
    # openAstro = openAstro(event1, type="Radix", lang='ru')
    # openAstro = openAstro(event1, event2, type="Solar", settings=settings)
    # openAstro = openAstro(event1, event2, type="Lunar", settings=settings)
    # openAstro = openAstro(event1, event2, type="Direction", settings=settings)
    # svg = openAstro.calcAstro()
    svg = openAstro.makeSVG2()

    print(openAstro.planets_degree)
    with open("astro_dict.json", "w", encoding="utf-8") as f:
        json.dump(openAstro.astro_dict, f, ensure_ascii=False, indent=2)
    # print('openAstro.astro_dict=', openAstro.astro_dict)
    # print('openAstro.planets_dict=', openAstro.planets_dict)
    # print('openAstro.planets_aspects_list=', openAstro.planets_aspects_list)
    # print('openAstro.t_planets_aspects_list=', openAstro.t_planets_aspects_list)
    # print('openAstro.planets_dict_t=', openAstro.planets_dict_t)
    # print(openAstro.planets_degree_ut)
    # # print(openAstro.t_planets_degree_ut)
    # print(openAstro.planets_sign)
    # binary_list = [int(value) for value in openAstro.planets_retrograde]
    # print(openAstro.planets_retrograde)
    # print(binary_list)
    # print(openAstro.lunar_phase)
    # print(openAstro.lunar_phase["degrees"])
    # print(openAstro.lunar_phase["moon_phase"])
    # print(openAstro.lunar_phase["sun_phase"])
    # print(openAstro.t_planets_degree_ut)
    # print(openAstro.t_planets_degree_ut)
