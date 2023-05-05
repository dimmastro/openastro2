
if __name__ == '__main__':
    from openastro2.openastro2 import openAstro

    event = {}
    event["name"] = "Now"
    event["charttype"] = "Radix"
    event["year"] = 2023
    event["month"] = 10
    event["day"] = 10
    event["hour"] = 1
    event["minute"] = 1
    event["second"] = 1
    event["timezone"] = 0
    event["altitude"] = 25
    event["geonameid"] = None

    event["location"] = "London"
    event["geolat"] = 0
    event["geolon"] = 0
    event["countrycode"] = "en"
    event["timezonestr"] = "Europe/Amsterdam"

    settings={}
    settings['astrocfg']={}
    settings['astrocfg']['home_location'] = "Krasnoyarsk, Krasnoyarskiy, Russia"
    settings['astrocfg']['language'] = "ru"

    openAstro = openAstro([event], type="Radix", settings=settings)
    svg = openAstro.makeSVG()
    # print(svg)
    print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
    print(openAstro.settings.settings['astrocfg'])
