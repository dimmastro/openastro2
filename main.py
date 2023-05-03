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
    event["month"] = 1
    event["day"] = 1
    event["hour"] = 1
    event["timezone"] = 0
    event["altitude"] = 25
    event["geonameid"] = None

    openAstro = openAstroInstance(db, cfg, event)
    r = 240
    file = openAstro.makeSVG()
    print(file)
    openAstro.makePlanets(r)
    print(openAstro.planets_degree)
    print(openAstro.planets_degree_ut)