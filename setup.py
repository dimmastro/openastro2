from setuptools import setup, find_packages

setup(name='OpenAstro2',
      version='2.0.0',
      description='Open Source Astrology 2',
      author='Pelle van der Scheer + DimmAstro',
      author_email='',
      url='https://github.com/dimmastro/openastro2',
      packages=["openastro2"],
      package_dir={"openastro2": "openastro2"},
      license='GPL',
      scripts=['openastro2'],
      include_package_data=True,
      python_requires=">=3.9",
      install_requires=[
            "pyswisseph",
            "pytz",
            "jsonpickle",
            "requests",
            "requests_cache",
            "pydantic",
            "terminaltables"
      ],
     )
