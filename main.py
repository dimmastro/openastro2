from typing import Dict, Any

if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    # event1 = openAstro.event("Nikola Tesla", 1856, 7, 10, 0, 0, 0, timezone=1, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    # event2 = openAstro.event("Ill", 1873, 10, 10, 0, 30, 0, timezone=1.36666666, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    # event1 = openAstro.event("Nikola Tesla", 2000, 7, 10, 0, 0, 0, timezone=1, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    event1 = openAstro.event_dt_str("Dimm", dt_str="1900-03-19 06:47:00", dt_str_format='%Y-%m-%d %H:%M:%S', timezone=7, location="Красноярск", countrycode="RU", geolat=56.0166742583253, geolon=92.9715236569857)

    event2 = openAstro.event("Ill", 2000, 10, 10, 0, 30, 0, timezone=1.36666666, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)

    settings={}
    settings['astrocfg']={}
    settings['astrocfg']['language'] = "ru"

    # openAstro = openAstro(event1, event2, type="Transit", settings=settings)
    openAstro = openAstro(event1, event2, type="Radix", settings=settings)
    # openAstro = openAstro(event1, event2, type="Solar", settings=settings)
    # openAstro = openAstro(event1, event2, type="Lunar", settings=settings)
    # openAstro = openAstro(event1, event2, type="Direction", settings=settings)
    svg = openAstro.makeSVG2()

    # print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
    # print(openAstro.t_planets_degree_ut)
    print(openAstro.planets_sign)
    binary_list = [int(value) for value in openAstro.planets_retrograde]
    print(openAstro.planets_retrograde)
    print(binary_list)
    print(openAstro.lunar_phase)
    print(openAstro.lunar_phase["degrees"])
    print(openAstro.lunar_phase["moon_phase"])
    print(openAstro.lunar_phase["sun_phase"])
    # print(openAstro.t_planets_degree_ut)
    # print(openAstro.t_planets_degree_ut)

