from openastro.my_openastro import openAstroCfg, openAstroSqlite, openAstroInstance

cfg = openAstroCfg()
db = openAstroSqlite()
openAstro = openAstroInstance(db, cfg)
r=240
file = openAstro.makeSVG()
print (file)
openAstro.makePlanets(r)
print (openAstro.planets)