# API Reference

Complete reference for OpenAstro2 classes, methods, and functions.

## Core Classes

### openAstro

The main class for creating astrological charts.

```python
class openAstro(event1, event2=None, type="Radix", settings=None)
```

#### Parameters

- **event1** (`event`): Primary event (usually birth data)
- **event2** (`event`, optional): Secondary event (for transits, synastry)
- **type** (`str`): Chart type (see [Chart Types](chart-types.md))
- **settings** (`dict`, optional): Configuration settings

#### Example
```python
from openastro2.openastro2 import openAstro

event = openAstro.event("John", 1990, 6, 15, 14, 30, 0)
chart = openAstro(event, type="Radix")
```

### Event Creation

#### event()

Create an event using individual date/time components.

```python
@staticmethod
event(name, year, month, day, hour, minute, second, 
      timezone=0, location="", countrycode="", 
      geolat=0.0, geolon=0.0)
```

**Parameters:**
- **name** (`str`): Event name
- **year** (`int`): Year (e.g., 1990)
- **month** (`int`): Month (1-12)
- **day** (`int`): Day (1-31)
- **hour** (`int`): Hour (0-23)
- **minute** (`int`): Minute (0-59)
- **second** (`int`): Second (0-59)
- **timezone** (`float`): UTC offset in hours (e.g., 2.0 for UTC+2)
- **location** (`str`): Location name
- **countrycode** (`str`): ISO country code
- **geolat** (`float`): Latitude in decimal degrees
- **geolon** (`float`): Longitude in decimal degrees

#### event_dt_str()

Create an event using a datetime string.

```python
@staticmethod
event_dt_str(name, dt_str, timezone=0, location="", 
             countrycode="", geolat=0.0, geolon=0.0)
```

**Parameters:**
- **dt_str** (`str`): Datetime string in format "YYYY-MM-DD HH:MM:SS"
- Other parameters same as `event()`

**Example:**
```python
event = openAstro.event_dt_str(
    "Birth", "1990-06-15 14:30:00",
    timezone=2, location="Berlin",
    geolat=52.5200, geolon=13.4050
)
```

## Chart Generation

### makeSVG2()

Generate SVG chart representation.

```python
def makeSVG2() -> str
```

**Returns:** SVG content as string

**Example:**
```python
chart = openAstro(event, type="Radix")
svg_content = chart.makeSVG2()

with open("chart.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

## Data Access Properties

### Planet Data

#### planets_degree_ut
Planet positions in degrees (0-360).

```python
chart.planets_degree_ut[0]  # Sun position
chart.planets_degree_ut[1]  # Moon position
# ... up to index 42 for various celestial bodies
```

#### planets_sign
Planet zodiac signs (0-11, where 0=Aries, 1=Taurus, etc.).

```python
chart.planets_sign[0]  # Sun sign
chart.planets_sign[1]  # Moon sign
```

#### planets_retrograde
Retrograde status (0=direct, 1=retrograde).

```python
chart.planets_retrograde[2]  # Mercury retrograde status
```

#### Planet Index Reference

| Index | Planet/Point |
|-------|-------------|
| 0     | Sun |
| 1     | Moon |
| 2     | Mercury |
| 3     | Venus |
| 4     | Mars |
| 5     | Jupiter |
| 6     | Saturn |
| 7     | Uranus |
| 8     | Neptune |
| 9     | Pluto |
| 10    | Mean Node |
| 11    | True Node |
| 12    | Mean Apogee (Lilith) |
| 13    | Oscillating Apogee |
| 14    | Earth |
| 15    | Chiron |
| 16-22 | Various asteroids |
| 23    | Ascendant |
| 24-35 | House cusps II-XII |
| 36-42 | Additional points |

### House Data

#### houses_degree_ut
House cusp positions in degrees.

```python
chart.houses_degree_ut[0]   # Ascendant (1st house cusp)
chart.houses_degree_ut[9]   # Midheaven (10th house cusp)
chart.houses_degree_ut[6]   # Descendant (7th house cusp)
chart.houses_degree_ut[3]   # IC (4th house cusp)
```

### Lunar Information

#### lunar_phase
Lunar phase information.

```python
lunar_info = chart.lunar_phase
print(lunar_info["degrees"])      # Phase angle in degrees
print(lunar_info["moon_phase"])   # Moon phase name
print(lunar_info["sun_phase"])    # Sun phase name
```

### Aspect Data

#### aspects_grid
Aspect grid between planets.

```python
aspects = chart.aspects_grid
# Access specific aspect between planets
aspect_sun_moon = aspects[0][1]  # Sun-Moon aspect
```

## Configuration

### Settings Structure

```python
settings = {
    'astrocfg': {
        'language': 'en',           # Language code
        'houses_system': 'P',       # House system
        'zodiactype': 'tropical',   # Zodiac type
        'postype': 'geo',          # Position type
        'chartview': 'european',    # Chart style
        'siderealmode': 'FAGAN_BRADLEY'  # Sidereal mode
    },
    'color_codes': {
        'paper_0': '#000000',       # Background color
        'paper_1': '#ffffff',       # Foreground color
        # ... more color settings
    }
}
```

### House Systems

| Code | System |
|------|--------|
| 'P' | Placidus |
| 'K' | Koch |
| 'E' | Equal |
| 'W' | Whole Sign |
| 'R' | Regiomontanus |
| 'C' | Campanus |
| 'A' | Equal (Ascendant) |
| 'D' | Equal (MC) |
| 'M' | Morinus |
| 'O' | Porphyrius |
| 'T' | Topocentric |
| 'V' | Vehlow |
| 'H' | Horizontal |
| 'U' | Krusinski |
| 'N' | Equal/Aries |

### Position Types

| Type | Description |
|------|-------------|
| 'geo' | Apparent geocentric |
| 'truegeo' | True geocentric |
| 'topo' | Topocentric |
| 'helio' | Heliocentric |

### Zodiac Types

| Type | Description |
|------|-------------|
| 'tropical' | Tropical zodiac |
| 'sidereal' | Sidereal zodiac |

### Sidereal Modes

When using sidereal zodiac:

| Mode | Description |
|------|-------------|
| 'FAGAN_BRADLEY' | Fagan-Bradley |
| 'LAHIRI' | Lahiri |
| 'DELUCE' | DeLuce |
| 'RAMAN' | Raman |
| 'USHASHASHI' | Ushashashi |
| 'KRISHNAMURTI' | Krishnamurti |
| 'DJWHAL_KHUL' | Djwhal Khul |
| 'YUKTESHWAR' | Yukteshwar |
| 'JN_BHASIN' | JN Bhasin |
| 'BABYL_KUGLER1' | Babylonian (Kugler 1) |
| 'BABYL_KUGLER2' | Babylonian (Kugler 2) |
| 'BABYL_KUGLER3' | Babylonian (Kugler 3) |
| 'BABYL_HUBER' | Babylonian (Huber) |
| 'BABYL_ETPSC' | Babylonian (ETPSC) |
| 'ALDEBARAN_15TAU' | Aldebaran at 15° Taurus |
| 'HIPPARCHOS' | Hipparchos |
| 'SASSANIAN' | Sassanian |
| 'GALCENT_0SAG' | Galactic Center at 0° Sagittarius |
| 'J2000' | J2000 |
| 'J1900' | J1900 |
| 'B1950' | B1950 |
| 'SURYASIDDHANTA' | Surya Siddhanta |
| 'SURYASIDDHANTA_MSUN' | Surya Siddhanta (Mean Sun) |
| 'ARYABHATA' | Aryabhata |
| 'ARYABHATA_MSUN' | Aryabhata (Mean Sun) |
| 'SS_REVATI' | Siddhanta with Revati |
| 'SS_CITRA' | Siddhanta with Citra |
| 'TRUE_CITRA' | True Citra |
| 'TRUE_REVATI' | True Revati |
| 'TRUE_PUSHYA' | True Pushya |
| 'GALCENT_RGILBRAND' | Galactic Center (Gil Brand) |
| 'GALEQU_IAU1958' | Galactic Equator (IAU 1958) |
| 'GALEQU_TRUE' | True Galactic Equator |
| 'GALEQU_MULA' | Galactic Equator (Mula) |
| 'GALALIGN_MARDYKS' | Galactic Alignment (Mardyks) |
| 'TRUE_MULA' | True Mula |
| 'GALCENT_MULA_WILHELM' | Galactic Center Mula (Wilhelm) |
| 'ARYABHATA_522' | Aryabhata 522 |
| 'BABYL_BRITTON' | Babylonian (Britton) |
| 'TRUE_SHEORAN' | True Sheoran |
| 'GALCENT_COCHRANE' | Galactic Center (Cochrane) |

## Advanced Features

### Fixed Stars

Access fixed star positions:

```python
# Fixed stars are included in extended planet list
# Check if fixed stars module is available
if hasattr(chart, 'fixar_data'):
    fixed_stars = chart.fixar_data
```

### Geographic Astrology

For local space and astrocartography:

```python
# Local Space Map
local_space = openAstro(event, type="LocalSpace")

# AstroMap  
astro_map = openAstro(event, type="AstroMap")
```

### Dignities

Access planetary dignities:

```python
# Essential dignities
if hasattr(chart, 'dignities'):
    dignities = chart.dignities
    # Access dignity information for each planet
```

## Utility Functions

### Time Conversion

```python
from openastromod.utils import utc_to_local, local_to_utc

# Convert UTC to local time
local_time = utc_to_local(utc_datetime, timezone_offset)

# Convert local to UTC time  
utc_time = local_to_utc(local_datetime, timezone_offset)
```

### Geographic Functions

```python
from openastromod import geoname

# Get location data
location_data = geoname.search_location("London")
```

## Error Handling

### Common Exceptions

```python
try:
    event = openAstro.event("Test", 2000, 2, 30, 12, 0, 0)  # Invalid date
except ValueError as e:
    print(f"Invalid date: {e}")

try:
    event = openAstro.event("Test", 2000, 1, 1, 12, 0, 0, geolat=91.0)  # Invalid lat
except ValueError as e:
    print(f"Invalid coordinates: {e}")

try:
    chart = openAstro(event, type="InvalidType")
except KeyError as e:
    print(f"Invalid chart type: {e}")
```

### Swiss Ephemeris Errors

```python
try:
    chart = openAstro(event, type="Radix")
    svg = chart.makeSVG2()
except RuntimeError as e:
    if "Swiss Ephemeris" in str(e):
        print("Swiss Ephemeris data files missing or corrupted")
    else:
        print(f"Runtime error: {e}")
```

## Performance Considerations

### Batch Processing

```python
# Reuse settings for multiple charts
settings = {'astrocfg': {'language': 'en'}}

events = [...]  # List of events
charts = []

for event in events:
    chart = openAstro(event, type="Radix", settings=settings)
    charts.append(chart)
```

### Memory Management

```python
# For large batches, consider processing in chunks
def process_charts_in_batches(events, batch_size=100):
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        for event in batch:
            chart = openAstro(event, type="Radix")
            # Process chart immediately
            yield chart
            # Chart will be garbage collected
```

## Version Information

```python
from openastro2.openastro2 import VERSION
print(f"OpenAstro2 version: {VERSION}")
```

## Debugging

### Debug Mode

```python
from openastro2.openastro2 import DEBUG, dprint

# Enable debug output
DEBUG = True

# Use debug print function
dprint("Debug message")
```

### Verbose Output

```python
# Enable verbose calculations
settings = {
    'astrocfg': {
        'debug_mode': True,
        'verbose_calculations': True
    }
}

chart = openAstro(event, type="Radix", settings=settings)
```