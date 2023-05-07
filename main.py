
if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    event1 = {}
    event1["name"] = "Nikola Tesla"
    event1["charttype"] = "Radix"
    event1["year"] = 1856
    event1["month"] = 7
    event1["day"] = 10
    event1["hour"] = 0
    event1["minute"] = 0
    event1["second"] = 0
    event1["timezone"] = 1
    event1["altitude"] = 25
    event1["geonameid"] = None
    event1["location"] = "Smiljan"
    event1["geolat"] = 44.5666644
    event1["geolon"] = 15.3166654
    event1["countrycode"] = "hr"
    event1["timezonestr"] = "Europe/Zagreb"

    event2 = {}
    event2["name"] = "Now"
    event2["charttype"] = "Radix"
    event2["year"] = 1943
    event2["month"] = 1
    event2["day"] = 7
    event2["hour"] = 12
    event2["minute"] = 0
    event2["second"] = 0
    event2["timezone"] = 0
    event2["altitude"] = 25
    event2["geonameid"] = None
    event2["location"] = "London"
    event2["geolat"] = 0
    event2["geolon"] = 0
    event2["countrycode"] = "en"
    event2["timezonestr"] = "Europe/Amsterdam"


    settings={}
    settings['astrocfg']={}
    settings['astrocfg']['home_location'] = "Krasnoyarsk, Krasnoyarskiy, Russia"
    settings['astrocfg']['language'] = "ru"

    # openAstro = openAstro(event1, event2, type="Transit", settings=settings)
    openAstro = openAstro(event1, event2, type="Radix", settings=settings)
    svg = openAstro.makeSVG2()

    # print(svg)
    print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
    print(openAstro.settings.settings['astrocfg'])
