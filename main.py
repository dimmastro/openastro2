
if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    # event1 = {}
    # event1["name"] = "Nikola Tesla"
    # event1["charttype"] = "Radix"
    # event1["year"] = 1856
    # event1["month"] = 7
    # event1["day"] = 10
    # event1["hour"] = 0
    # event1["minute"] = 0
    # event1["second"] = 0
    # event1["timezone"] = 1
    # event1["altitude"] = 25
    # event1["geonameid"] = None
    # event1["location"] = "Smiljan"
    # event1["geolat"] = 44.5666644
    # event1["geolon"] = 15.3166654
    # event1["countrycode"] = "hr"
    # event1["timezonestr"] = "Europe/Zagreb"
    event1 = openAstro.event("Nikola Tesla", 1856, 7, 10, 0, 0, 0, timezone=1, location="Smiljan", countrycode="HR", geolat=44.5666644, geolon=15.3166654)
    print (event1)

    # event2 = {}
    # event2["name"] = "End"
    # event2["charttype"] = "Radix"
    # event2["year"] = 1943
    # event2["month"] = 4
    # event2["day"] = 7
    # event2["hour"] = 12
    # event2["minute"] = 0
    # event2["second"] = 0
    # event2["timezone"] = 0
    # event2["altitude"] = 25
    # event2["geonameid"] = None
    # event2["location"] = "London"
    # event2["geolat"] = 0
    # event2["geolon"] = 0
    # event2["countrycode"] = "en"
    # event2["timezonestr"] = "Europe/Amsterdam"
    event2 = openAstro.event("End", 1943, 4, 7, 12, 0, 0, location="нью йорк", countrycode="US")
    # event2 = openAstro.event("Now", location="New York", countrycode="US")
    print (event2)

    settings={}
    settings['astrocfg']={}
    settings['astrocfg']['home_location'] = "Krasnoyarsk, Krasnoyarskiy, Russia"
    settings['astrocfg']['language'] = "ru"

    # openAstro = openAstro(event1, event2, type="Transit", settings=settings)
    # openAstro = openAstro(event1, event2, type="Radix", settings=settings)

    # openAstro = openAstro(event1, event2, type="Solar", settings=settings)
    # openAstro = openAstro(event1, event2, type="Lunar", settings=settings)
    openAstro = openAstro(event1, event2, type="Direction", settings=settings)
    # openAstro.calcAstro()
    # openAstro.localToSolar(1900)
    # openAstro.calcAstro()


    svg = openAstro.makeSVG2()

    # print(svg)
    print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
    print(openAstro.t_planets_degree_ut)
    print(openAstro.settings.settings['astrocfg'])
