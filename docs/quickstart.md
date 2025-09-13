# Quick Start Guide

This guide will help you create your first astrological chart with OpenAstro2 in just a few minutes.

## Basic Usage

### Creating Your First Chart

```python
from openastro2.openastro2 import openAstro

# Create a birth event
event = openAstro.event(
    name="John Doe",
    year=1990, month=6, day=15,
    hour=14, minute=30, second=0,
    timezone=2,  # UTC+2
    location="Berlin",
    countrycode="DE",
    geolat=52.5200,  # Latitude
    geolon=13.4050   # Longitude
)

# Create a natal chart
chart = openAstro(event, type="Radix")

# Generate SVG chart
svg_content = chart.makeSVG2()

# Save to file
with open("natal_chart.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

### Alternative Date/Time Input

You can also use datetime strings:

```python
from openastro2.openastro2 import openAstro

# Using datetime string
event = openAstro.event_dt_str(
    name="Jane Smith",
    dt_str="1985-12-25 18:45:00",
    timezone=-5,  # UTC-5 (EST)
    location="New York",
    geolat=40.7128,
    geolon=-74.0060
)

chart = openAstro(event, type="Radix")
```

## Chart Types

### Natal Chart (Radix)
```python
natal_chart = openAstro(event, type="Radix")
```

### Transit Chart
```python
# Current transits to natal chart
transit_chart = openAstro(event, type="Transit")

# Specific date transits
transit_event = openAstro.event_dt_str(
    "Transit", "2024-01-01 12:00:00", 
    timezone=0, location="London",
    geolat=51.5074, geolon=-0.1278
)
transit_chart = openAstro(event, transit_event, type="Transit")
```

### Solar Return
```python
solar_return = openAstro(event, type="Solar")
```

### Progression Chart
```python
progression = openAstro(event, type="SProgression")
```

## Accessing Chart Data

### Planet Positions
```python
chart = openAstro(event, type="Radix")

# Planet degrees (0-360)
print("Sun position:", chart.planets_degree_ut[0])  # Sun
print("Moon position:", chart.planets_degree_ut[1])  # Moon

# Planet signs (0-11, Aries=0, Taurus=1, etc.)
print("Sun sign:", chart.planets_sign[0])
print("Moon sign:", chart.planets_sign[1])

# Retrograde status
print("Mercury retrograde:", chart.planets_retrograde[2])
```

### Houses
```python
# House cusps
print("Ascendant:", chart.houses_degree_ut[0])
print("Midheaven:", chart.houses_degree_ut[9])

# House systems
chart_placidus = openAstro(event, type="Radix")  # Default Placidus
```

### Aspects
```python
# Calculate aspects between planets
aspects = chart.aspects_grid

# Major aspects will be calculated automatically
# Check the aspects_list for detailed aspect information
```

## Configuration

### Basic Settings
```python
# Configure language and appearance
settings = {
    'astrocfg': {
        'language': 'en',  # English
        'houses_system': 'P',  # Placidus
        'zodiactype': 'tropical',
        'postype': 'geo'  # Geocentric
    }
}

chart = openAstro(event, type="Radix", settings=settings)
```

### House Systems
```python
settings = {
    'astrocfg': {
        'houses_system': 'K',  # Koch
        # Other options: 'E' (Equal), 'W' (Whole Sign), 
        # 'R' (Regiomontanus), 'C' (Campanus), etc.
    }
}
```

### Coordinate Systems
```python
settings = {
    'astrocfg': {
        'postype': 'topo',  # Topocentric
        # Options: 'geo' (geocentric), 'topo' (topocentric), 
        # 'helio' (heliocentric), 'truegeo' (true geocentric)
    }
}
```

## Working with Multiple Charts

### Synastry (Relationship Charts)
```python
# Person A
person_a = openAstro.event(
    "Person A", 1985, 3, 15, 10, 30, 0,
    timezone=1, location="London",
    geolat=51.5074, geolon=-0.1278
)

# Person B  
person_b = openAstro.event(
    "Person B", 1987, 7, 22, 16, 45, 0,
    timezone=1, location="London", 
    geolat=51.5074, geolon=-0.1278
)

# Create synastry chart
synastry = openAstro(person_a, person_b, type="Transit")
```

### Progressions and Directions
```python
# Secondary progressions
progression = openAstro(event, type="SProgression")

# Primary directions
direction = openAstro(event, type="Direction")
```

## Common Patterns

### Batch Processing
```python
def create_chart_for_person(name, birth_data):
    """Create a chart for a person given birth data."""
    event = openAstro.event(
        name=name,
        year=birth_data['year'],
        month=birth_data['month'], 
        day=birth_data['day'],
        hour=birth_data['hour'],
        minute=birth_data['minute'],
        second=0,
        timezone=birth_data['timezone'],
        location=birth_data['location'],
        geolat=birth_data['lat'],
        geolon=birth_data['lon']
    )
    
    chart = openAstro(event, type="Radix")
    svg = chart.makeSVG2()
    
    # Save chart
    filename = f"{name.replace(' ', '_')}_natal.svg"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)
    
    return chart

# Example usage
people = [
    {
        'name': 'Alice',
        'year': 1990, 'month': 5, 'day': 10,
        'hour': 14, 'minute': 20,
        'timezone': 2, 'location': 'Berlin',
        'lat': 52.5200, 'lon': 13.4050
    },
    # Add more people...
]

for person in people:
    chart = create_chart_for_person(person['name'], person)
```

### Chart Comparison
```python
def compare_charts(chart1, chart2):
    """Compare two charts and extract key differences."""
    comparison = {
        'sun_signs': (chart1.planets_sign[0], chart2.planets_sign[0]),
        'moon_signs': (chart1.planets_sign[1], chart2.planets_sign[1]),
        'ascendants': (chart1.houses_degree_ut[0], chart2.houses_degree_ut[0])
    }
    return comparison
```

### Current Transits
```python
from datetime import datetime
import pytz

def get_current_transits(natal_event, location_tz='UTC'):
    """Get current transits for a natal chart."""
    now = datetime.now(pytz.timezone(location_tz))
    
    transit_event = openAstro.event_dt_str(
        "Current Transits",
        dt_str=now.strftime("%Y-%m-%d %H:%M:%S"),
        timezone=now.utcoffset().total_seconds() / 3600,
        location=natal_event.location,
        geolat=natal_event.geolat,
        geolon=natal_event.geolon
    )
    
    return openAstro(natal_event, transit_event, type="Transit")
```

## Error Handling

### Basic Error Handling
```python
try:
    event = openAstro.event(
        "Test", 2000, 1, 1, 12, 0, 0,
        timezone=0, location="London",
        geolat=51.5074, geolon=-0.1278
    )
    chart = openAstro(event, type="Radix")
    svg = chart.makeSVG2()
    
except Exception as e:
    print(f"Error creating chart: {e}")
    # Handle error appropriately
```

### Common Issues
```python
# Invalid dates
try:
    event = openAstro.event("Test", 2000, 2, 30, 12, 0, 0)  # Invalid date
except ValueError as e:
    print("Invalid date provided")

# Invalid coordinates
try:
    event = openAstro.event(
        "Test", 2000, 1, 1, 12, 0, 0,
        geolat=91.0,  # Invalid latitude
        geolon=0.0
    )
except ValueError as e:
    print("Invalid coordinates provided")
```

## Performance Tips

### Reusing Objects
```python
# Create event once, use multiple times
event = openAstro.event("Person", 1990, 1, 1, 12, 0, 0)

# Create different chart types
natal = openAstro(event, type="Radix")
solar_return = openAstro(event, type="Solar") 
progressions = openAstro(event, type="SProgression")
```

### Caching Results
```python
chart_cache = {}

def get_cached_chart(event_key, chart_type):
    """Get chart from cache or create new one."""
    cache_key = f"{event_key}_{chart_type}"
    
    if cache_key not in chart_cache:
        event = create_event_from_key(event_key)  # Your function
        chart_cache[cache_key] = openAstro(event, type=chart_type)
    
    return chart_cache[cache_key]
```

## Next Steps

Now that you've created your first charts, explore:

1. **[Chart Types](chart-types.md)** - Learn about all available chart types
2. **[Configuration](configuration.md)** - Customize appearance and calculations  
3. **[API Reference](api-reference.md)** - Detailed documentation of all methods
4. **[Examples](examples.md)** - More complex usage examples
5. **[Testing](testing.md)** - How to test your implementations

## Common Use Cases

### Personal Astrology App
```python
class PersonalAstrology:
    def __init__(self, birth_data):
        self.event = openAstro.event(**birth_data)
        self.natal_chart = openAstro(self.event, type="Radix")
    
    def get_daily_transits(self):
        return get_current_transits(self.event)
    
    def get_solar_return(self, year=None):
        if year:
            # Create event for specific solar return year
            pass
        return openAstro(self.event, type="Solar")
```

### Astrological Research
```python
def batch_analyze_charts(birth_data_list):
    """Analyze multiple charts for research."""
    results = []
    
    for data in birth_data_list:
        event = openAstro.event(**data)
        chart = openAstro(event, type="Radix")
        
        # Extract specific data points
        analysis = {
            'sun_sign': chart.planets_sign[0],
            'moon_sign': chart.planets_sign[1], 
            'ascendant': chart.houses_degree_ut[0],
            # Add more analysis points
        }
        results.append(analysis)
    
    return results
```