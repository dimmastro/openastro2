# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    from openastro2.openastro2 import openAstroCfg, openAstroSqlite, openAstroInstance

    cfg = openAstroCfg()
    db = openAstroSqlite()

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

    openAstro = openAstroInstance(event)
    # r = 240
    svg = openAstro.makeSVG()
    print (svg)
    # openAstro.makePlanets(r)
    print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)
