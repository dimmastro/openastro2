# Chart Types

OpenAstro2 supports a comprehensive range of astrological chart types for different analysis purposes.

## Primary Chart Types

### Radix (Natal Chart)
The foundational birth chart showing planetary positions at the moment of birth.

```python
natal_chart = openAstro(event, type="Radix")
```

**Features:**
- Planet positions in signs and houses
- House cusps and angles
- Aspects between planets
- Lunar phase information

**Use Cases:**
- Personality analysis
- Life potential assessment
- Foundation for other techniques

### Transit
Current planetary positions overlaid on the natal chart.

```python
transit_chart = openAstro(natal_event, transit_event, type="Transit")

# Or for current transits
current_transits = openAstro(natal_event, type="Transit")
```

**Features:**
- Current planet positions
- Aspects between transiting and natal planets
- House transits
- Timing of events

**Use Cases:**
- Current influences
- Predictive astrology
- Event timing

### Secondary Progressions
Symbolic progression where each day after birth represents one year of life.

```python
progression_chart = openAstro(event, type="SProgression")
```

**Features:**
- Progressed planet positions
- Progressed-to-natal aspects
- Progressed house cusps
- Progressed lunar phases

**Use Cases:**
- Character development
- Long-term trends
- Psychological evolution

### Primary Directions
Ancient technique relating celestial motion to life events.

```python
direction_chart = openAstro(event, type="Direction")
```

**Variations:**
- `"Direction"` - Standard primary directions
- `"DirectionPast"` - Historical directions
- `"DirectionRealPast"` - Real-time past directions
- `"DirectionRealFuture"` - Real-time future directions

## Solar System Returns

### Solar Return
Annual chart cast for the moment the Sun returns to its natal position.

```python
solar_return = openAstro(event, type="Solar")
```

**Variations:**
- `"Solar"` - Current year's solar return
- `"SolarNext"` - Next solar return
- `"SolarPrev"` - Previous solar return
- `"SolarNear"` - Nearest solar return

**Features:**
- Annual themes and focuses
- Relocated for current residence
- Houses emphasize life areas

**Use Cases:**
- Annual forecasting
- Birthday planning
- Relocation considerations

### Lunar Return
Monthly chart for when the Moon returns to its natal position.

```python
lunar_return = openAstro(event, type="Lunar")
```

**Features:**
- Monthly emotional themes
- Shorter-term cycles
- Emotional responses

## Lunation Charts

### New Moon Charts
Charts cast for New Moon closest to the person's location.

```python
new_moon_next = openAstro(event, type="NewMoonNext")
new_moon_prev = openAstro(event, type="NewMoonPrev")
```

**Features:**
- New beginnings and initiatives
- Planting seeds for growth
- Fresh starts

### Full Moon Charts
Charts cast for Full Moon closest to the person's location.

```python
full_moon_next = openAstro(event, type="FullMoonNext")
full_moon_prev = openAstro(event, type="FullMoonPrev")
```

**Features:**
- Culmination and manifestation
- Emotional peaks
- Completion of cycles

## Specialized Returns

### Ascendant Return
Chart for when the Ascendant returns to its natal position.

```python
asc_return = openAstro(event, type="AscReturn")
```

**Features:**
- Personal identity cycles
- Appearance and first impressions
- Self-expression themes

### Earth Return
Chart showing Earth's position in heliocentric terms.

```python
earth_return = openAstro(event, type="EarthReturn")
```

**Features:**
- Heliocentric perspective
- Earth's orbital position
- Solar system integration

## Geographic Astrology

### Geo Zodiac
Local space astrology using geographical coordinates.

```python
geo_zodiac = openAstro(event, type="GeoZodiac")
```

**Features:**
- Local horizon mapping
- Direction-based interpretation
- Location-specific influences

### Local Space Map
Maps planetary energies to geographical directions.

```python
local_space = openAstro(event, type="LocalSpace")
```

**Features:**
- Directional planetary influences
- Compass-based mapping
- Local environment analysis

### AstroMap (Astrocartography)
World map showing planetary lines and influences.

```python
astro_map = openAstro(event, type="AstroMap")
```

**Features:**
- Global planetary lines
- Relocation guidance
- Travel planning
- Best locations for different purposes

## Fixed Star Charts

### Fixed Star Planet Moment
Current positions of fixed stars relative to planets.

```python
fixar_planet_moment = openAstro(event, type="FixarPlanetMoment")
```

### Fixed Star Planet Radix
Fixed stars in relation to natal planetary positions.

```python
fixar_planet_radix = openAstro(event, type="FixarPlanetRadix")
```

### Fixed Star Planet Transit
Transiting fixed star influences.

```python
fixar_planet_transit = openAstro(event, type="FixarPlanetTransit")
```

### Fixed Star Earth Charts
Earth-centered fixed star calculations.

```python
fixar_earth_moment = openAstro(event, type="FixarEarthMoment")
fixar_earth_transit = openAstro(event, type="FixarEarthTransit")
```

## Chart Type Usage Examples

### Complete Natal Analysis
```python
def complete_natal_analysis(birth_event):
    """Create comprehensive natal analysis."""
    charts = {}
    
    # Core chart
    charts['natal'] = openAstro(birth_event, type="Radix")
    
    # Current influences
    charts['transits'] = openAstro(birth_event, type="Transit")
    charts['progressions'] = openAstro(birth_event, type="SProgression")
    
    # Annual cycle
    charts['solar_return'] = openAstro(birth_event, type="Solar")
    
    # Monthly cycle
    charts['lunar_return'] = openAstro(birth_event, type="Lunar")
    
    return charts
```

### Predictive Package
```python
def predictive_analysis(birth_event, target_date):
    """Create predictive chart package for specific date."""
    
    # Create target event
    target_event = openAstro.event_dt_str(
        "Target", target_date.strftime("%Y-%m-%d %H:%M:%S"),
        timezone=birth_event["timezone"],
        location=birth_event["location"],
        geolat=birth_event["geolat"],
        geolon=birth_event["geolon"]
    )
    
    analysis = {}
    
    # Transits for target date
    analysis['transits'] = openAstro(birth_event, target_event, type="Transit")
    
    # Progressions for target date
    analysis['progressions'] = openAstro(birth_event, target_event, type="SProgression")
    
    # Directions
    analysis['directions'] = openAstro(birth_event, target_event, type="Direction")
    
    return analysis
```

### Relationship Analysis
```python
def relationship_analysis(person1_event, person2_event):
    """Analyze relationship between two people."""
    
    analysis = {}
    
    # Individual charts
    analysis['person1_natal'] = openAstro(person1_event, type="Radix")
    analysis['person2_natal'] = openAstro(person2_event, type="Radix")
    
    # Synastry (person1's planets in person2's chart)
    analysis['synastry_1_to_2'] = openAstro(person1_event, person2_event, type="Transit")
    analysis['synastry_2_to_1'] = openAstro(person2_event, person1_event, type="Transit")
    
    # Composite chart (midpoint method would need custom calculation)
    
    return analysis
```

### Relocation Analysis
```python
def relocation_analysis(birth_event, new_location):
    """Analyze chart for new location."""
    
    # Create relocated event
    relocated_event = openAstro.event(
        name=f"{birth_event['name']} - Relocated",
        year=birth_event["year"],
        month=birth_event["month"],
        day=birth_event["day"],
        hour=birth_event["hour"],
        minute=birth_event["minute"],
        second=birth_event["second"],
        timezone=new_location['timezone'],
        location=new_location['name'],
        countrycode=new_location['country'],
        geolat=new_location['lat'],
        geolon=new_location['lon']
    )
    
    analysis = {}
    
    # Relocated natal chart
    analysis['relocated_natal'] = openAstro(relocated_event, type="Radix")
    
    # Solar return for new location
    analysis['relocated_solar'] = openAstro(relocated_event, type="Solar")
    
    # Geographic charts
    analysis['geo_zodiac'] = openAstro(relocated_event, type="GeoZodiac")
    analysis['local_space'] = openAstro(relocated_event, type="LocalSpace")
    
    return analysis
```

## Chart Type Parameters

### Common Settings
All chart types support these common settings:

```python
settings = {
    'astrocfg': {
        'houses_system': 'P',      # House system
        'zodiactype': 'tropical',   # Zodiac type
        'postype': 'geo',          # Position type
        'language': 'en'           # Display language
    }
}

chart = openAstro(event, type="Radix", settings=settings)
```

### Chart-Specific Settings

Some chart types have specific requirements:

```python
# Sidereal charts
sidereal_settings = {
    'astrocfg': {
        'zodiactype': 'sidereal',
        'siderealmode': 'LAHIRI'
    }
}

# Heliocentric charts
helio_settings = {
    'astrocfg': {
        'postype': 'helio'
    }
}

# Topocentric charts
topo_settings = {
    'astrocfg': {
        'postype': 'topo'
    }
}
```

## Data Access by Chart Type

Different chart types provide different data:

### Standard Charts (Radix, Transit, etc.)
```python
chart = openAstro(event, type="Radix")

# Planet positions
positions = chart.planets_degree_ut
signs = chart.planets_sign
retrograde = chart.planets_retrograde

# House data
houses = chart.houses_degree_ut

# Aspects
aspects = chart.planets_aspects_list

# Lunar phase
lunar = chart.lunar_phase
```

### Return Charts
```python
solar_return = openAstro(event, type="Solar")

# Same data structure as natal chart
# but calculated for return moment
positions = solar_return.planets_degree_ut
houses = solar_return.houses_degree_ut
```

### Geographic Charts
```python
geo_chart = openAstro(event, type="GeoZodiac")

# May include additional geographic data
if hasattr(geo_chart, 'geographic_data'):
    geo_data = geo_chart.geographic_data
```

## Chart Type Selection Guide

| Purpose | Recommended Chart Types |
|---------|------------------------|
| **Personality Analysis** | Radix, SProgression |
| **Current Timing** | Transit, Solar, Lunar |
| **Annual Planning** | Solar, SolarNext |
| **Monthly Themes** | Lunar, NewMoon, FullMoon |
| **Long-term Development** | SProgression, Direction |
| **Relationship Analysis** | Radix (both), Transit (synastry) |
| **Relocation** | GeoZodiac, LocalSpace, AstroMap |
| **Event Timing** | Transit, Direction, NewMoon/FullMoon |
| **Character Development** | SProgression, DirectionPast |
| **Future Planning** | Transit, DirectionRealFuture |

## Advanced Chart Combinations

### Progressive Analysis
```python
def progressive_timeline(birth_event, years_ahead=5):
    """Create progressive timeline of influences."""
    
    timeline = {}
    current_year = datetime.now().year
    
    for year in range(current_year, current_year + years_ahead + 1):
        year_data = {}
        
        # Solar return for each year
        solar_event = create_solar_return_event(birth_event, year)
        year_data['solar_return'] = openAstro(solar_event, type="Solar")
        
        # Major transits for each year
        year_start = datetime(year, 1, 1, 12, 0, 0)
        year_event = openAstro.event_dt_str(
            f"Year {year}", year_start.strftime("%Y-%m-%d %H:%M:%S"),
            timezone=birth_event["timezone"], location=birth_event["location"],
            geolat=birth_event["geolat"], geolon=birth_event["geolon"]
        )
        year_data['year_transits'] = openAstro(birth_event, year_event, type="Transit")
        
        timeline[year] = year_data
    
    return timeline
```

This comprehensive chart type system allows for detailed astrological analysis across multiple dimensions of time, space, and symbolic meaning.
