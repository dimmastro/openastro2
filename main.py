
if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    event1 = {}
    event1["name"] = "Now"
    event1["charttype"] = "Transit"
    event1["year"] = 2023
    event1["month"] = 10
    event1["day"] = 10
    event1["hour"] = 1
    event1["minute"] = 1
    event1["second"] = 1
    event1["timezone"] = 0
    event1["altitude"] = 25
    event1["geonameid"] = None
    event1["location"] = "London"
    event1["geolat"] = 0
    event1["geolon"] = 0
    event1["countrycode"] = "en"
    event1["timezonestr"] = "Europe/Amsterdam"

    event2 = {}
    event2["name"] = "Now"
    event2["charttype"] = "Radix"
    event2["year"] = 2024
    event2["month"] = 10
    event2["day"] = 10
    event2["hour"] = 1
    event2["minute"] = 1
    event2["second"] = 1
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

    openAstro = openAstro(event1, event2, type="Transit", settings=settings)
    svg = openAstro.makeSVG()
    # print(svg)
    print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
    print(openAstro.settings.settings['astrocfg'])
