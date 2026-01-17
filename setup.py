from setuptools import setup, find_packages

setup(
    name='OpenAstro2',
    version='2.0.0',
    description='Open Source Astrology 2',
    author='Pelle van der Scheer + DimmAstro',
    author_email='',
    url='https://github.com/dimmastro/openastro2',  # ← убраны лишние пробелы
    packages=find_packages(),
    license='GPL',
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "pyswisseph==2.10.3.2",
        "pytz",
        "jsonpickle",
        "requests==2.31.0",
        "requests_cache",
        "pydantic",
        "terminaltables",
        "skyfield==1.46",
        "pydeck==0.8.0",
        "pandas==2.0.2",
        "certifi==2023.11.17",
        "svgwrite==1.4.3",
        "numpy==1.26.4",
        "openpyxl==3.1.5",
        "ephem==4.2",
        "geographiclib==2.0",
        "json5==0.12.1",
        "spiceypy==8.0.1",
    ],
)