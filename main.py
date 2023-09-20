
if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    event1 = openAstro.event("Nikola Tesla", 1856, 7, 10, 0, 0, 0, timezone=1, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    event2 = openAstro.event("Ill", 1873, 10, 10, 0, 30, 0, timezone=1.36666666, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)

    settings={}
    settings['astrocfg']={}
    settings['astrocfg']['language'] = "ru"

    # openAstro = openAstro(event1, event2, type="Transit", settings=settings)
    # openAstro = openAstro(event1, event2, type="Radix", settings=settings)
    # openAstro = openAstro(event1, event2, type="Solar", settings=settings)
    # openAstro = openAstro(event1, event2, type="Lunar", settings=settings)
    openAstro = openAstro(event1, event2, type="Direction", settings=settings)
    svg = openAstro.makeSVG2()

    # print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
    print(openAstro.t_planets_degree_ut)

