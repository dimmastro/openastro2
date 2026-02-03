# Configuration

OpenAstro2 provides extensive configuration options to customize calculations, appearance, and behavior.

## Configuration Overview

Configuration in OpenAstro2 is managed through JSON settings structures that can be:
- Loaded from predefined JSON files
- Created programmatically
- Combined and modified for specific needs

## Settings Structure

The main settings object has several key sections:

```python
settings = {
    'astrocfg': {           # Core astrological configuration
        # Calculation settings
    },
    'color_codes': {        # Visual appearance colors
        # Color definitions
    },
    'label': {             # Text labels and translations
        # Label definitions
    },
    'settings_planet': [   # Planet-specific settings
        # Planet configurations
    ],
    'settings_aspect': [   # Aspect definitions
        # Aspect configurations
    ]
}
```

## Core Configuration (astrocfg)

### Basic Settings

```python
astrocfg = {
    'version': '2.0.0',
    'language': 'en',                    # Interface language
    'houses_system': 'P',                # House system
    'houses_system_polar': 'A',          # Polar house system
    'postype': 'geo',                    # Position type
    'chartview': 'european',             # Chart style
    'zodiactype': 'tropical',            # Zodiac type
    'siderealmode': 'FAGAN_BRADLEY',     # Sidereal ayanamsa
    'round_aspects': 1,                  # Round aspect degrees
    'planet_in_one_house': 0,            # Allow multiple planets per house
    'geo_zodiac_start': 0                # Geographic zodiac starting point
}
```

### Location Settings

```python
astrocfg.update({
    'home_location': 'London',
    'home_geolat': '51.5074',
    'home_geolon': '-0.1278',
    'home_countrycode': 'GB',
    'home_timezonestr': 'Europe/London',
    'use_geonames.org': '0'              # Use online geonames service
})
```

### House Systems

OpenAstro2 supports numerous house systems:

```python
# Popular house systems
house_systems = {
    'P': 'Placidus',              # Most common
    'K': 'Koch',                  # German system
    'E': 'Equal',                 # Equal houses from Ascendant
    'W': 'Whole Sign',            # Ancient system
    'R': 'Regiomontanus',         # Medieval system
    'C': 'Campanus',              # Spatial system
    'A': 'Equal (Ascendant)',     # Equal from Asc
    'D': 'Equal (MC)',            # Equal from MC
    'M': 'Morinus',               # French system
    'O': 'Porphyrius',            # Ancient system
    'T': 'Topocentric',           # Page-Polich
    'V': 'Vehlow',                # German equal
    'H': 'Horizontal',            # Azimuthal
    'U': 'Krusinski',             # Polish system
    'N': 'Equal/Aries'            # Aries = 1st house
}

# Set house system
settings = {
    'astrocfg': {
        'houses_system': 'K'  # Koch houses
    }
}
```

### Position Types

Configure the reference frame for calculations:

```python
position_types = {
    'geo': 'Apparent Geocentric',     # Default, Earth-centered
    'truegeo': 'True Geocentric',     # No atmospheric refraction
    'topo': 'Topocentric',            # Observer's actual location
    'helio': 'Heliocentric'           # Sun-centered
}

# Example: Topocentric calculations
settings = {
    'astrocfg': {
        'postype': 'topo'
    }
}
```

### Zodiac Types

Choose between tropical and sidereal zodiac:

```python
# Tropical zodiac (seasonal, Western)
tropical_settings = {
    'astrocfg': {
        'zodiactype': 'tropical'
    }
}

# Sidereal zodiac (star-based, Vedic)
sidereal_settings = {
    'astrocfg': {
        'zodiactype': 'sidereal',
        'siderealmode': 'LAHIRI'      # Popular Vedic ayanamsa
    }
}
```

### Sidereal Ayanamsas

When using sidereal zodiac, choose an ayanamsa:

```python
sidereal_modes = {
    'FAGAN_BRADLEY': 'Fagan-Bradley',
    'LAHIRI': 'Lahiri (Chitrapaksha)',
    'DELUCE': 'DeLuce',
    'RAMAN': 'Raman',
    'USHASHASHI': 'Ushashashi',
    'KRISHNAMURTI': 'Krishnamurti',
    'DJWHAL_KHUL': 'Djwhal Khul',
    'YUKTESHWAR': 'Yukteshwar',
    'JN_BHASIN': 'JN Bhasin',
    'BABYL_KUGLER1': 'Babylonian Kugler 1',
    'BABYL_KUGLER2': 'Babylonian Kugler 2',
    'BABYL_KUGLER3': 'Babylonian Kugler 3',
    'GALCENT_0SAG': 'Galactic Center 0° Sagittarius',
    'TRUE_CITRA': 'True Citra',
    'TRUE_REVATI': 'True Revati'
}
```

## Color Configuration

### Basic Colors

```python
color_codes = {
    # Paper/background colors
    'paper_0': '#000000',        # Background
    'paper_1': '#ffffff',        # Foreground
    
    # Zodiac sign colors (12 signs)
    'zodiac_bg_0': '#ef5350',    # Aries
    'zodiac_bg_1': '#73b230',    # Taurus
    'zodiac_bg_2': '#ffd237',    # Gemini
    'zodiac_bg_3': '#4093f4',    # Cancer
    'zodiac_bg_4': '#ef5350',    # Leo
    'zodiac_bg_5': '#73b230',    # Virgo
    'zodiac_bg_6': '#ffd237',    # Libra
    'zodiac_bg_7': '#4093f4',    # Scorpio
    'zodiac_bg_8': '#ef5350',    # Sagittarius
    'zodiac_bg_9': '#73b230',    # Capricorn
    'zodiac_bg_10': '#ffd237',   # Aquarius
    'zodiac_bg_11': '#4093f4',   # Pisces
    
    # Planet colors
    'planet_0': '#ffd700',       # Sun - Gold
    'planet_1': '#c0c0c0',       # Moon - Silver
    'planet_2': '#ff6600',       # Mercury - Orange
    'planet_3': '#00ff00',       # Venus - Green
    'planet_4': '#ff0000',       # Mars - Red
    'planet_5': '#0066ff',       # Jupiter - Blue
    'planet_6': '#800080',       # Saturn - Purple
    'planet_7': '#00ffff',       # Uranus - Cyan
    'planet_8': '#0080ff',       # Neptune - Blue
    'planet_9': '#800000',       # Pluto - Maroon
    
    # Chart elements
    'houses_radix_line': '#444444',
    'houses_transit_line_1': '#ff0000',
    'houses_transit_line_2': '#0000ff'
}
```

### Elemental Color Schemes

```python
# Fire signs (Aries, Leo, Sagittarius)
fire_colors = {
    'zodiac_bg_0': '#ff4500',    # Aries
    'zodiac_bg_4': '#ff6600',    # Leo  
    'zodiac_bg_8': '#ff8c00'     # Sagittarius
}

# Earth signs (Taurus, Virgo, Capricorn)
earth_colors = {
    'zodiac_bg_1': '#8b4513',    # Taurus
    'zodiac_bg_5': '#a0522d',    # Virgo
    'zodiac_bg_9': '#654321'     # Capricorn
}

# Air signs (Gemini, Libra, Aquarius)
air_colors = {
    'zodiac_bg_2': '#87ceeb',    # Gemini
    'zodiac_bg_6': '#b0e0e6',    # Libra
    'zodiac_bg_10': '#add8e6'    # Aquarius
}

# Water signs (Cancer, Scorpio, Pisces)
water_colors = {
    'zodiac_bg_3': '#4682b4',    # Cancer
    'zodiac_bg_7': '#191970',    # Scorpio
    'zodiac_bg_11': '#6a5acd'    # Pisces
}
```

## Planet Configuration

### Planet Settings Structure

```python
planet_config = {
    'id': 0,                     # Planet index
    'name': 'sun',               # Internal name
    'color': '#ffd700',          # Display color
    'visible': 1,                # Show in chart (1/0)
    'element_points': 40,        # Strength in elements
    'zodiac_relation': '4',      # Ruling sign(s)
    'label': 'Sun',              # Display label
    'label_short': 'sun',        # Short label
    'visible_aspect_line': 1,    # Show aspect lines
    'visible_aspect_grid': 1,    # Show in aspect grid
    'visible_json': 1,           # Include in JSON output
    'planet_orb': {              # Orbs by chart type and aspect
        'Radix': {
            'default': 10,
            '0': 10,    # Conjunction
            '60': 9,    # Sextile
            '90': 10,   # Square
            '120': 10,  # Trine
            '180': 10   # Opposition
        },
        'Transit': {
            'default': 2,
            '0': 2,
            '60': 2,
            '90': 2,
            '120': 2,
            '180': 2
        }
    }
}
```

### Customizing Planet Visibility

```python
# Hide certain planets/points
hidden_planets = {
    'settings_planet': [
        {
            'id': 16,           # Pholus
            'visible': 0        # Hide
        },
        {
            'id': 17,           # Ceres
            'visible': 0        # Hide
        }
    ]
}

# Show only traditional planets
traditional_only = {
    'settings_planet': [
        {'id': i, 'visible': 1 if i <= 9 else 0}  # Sun through Pluto only
        for i in range(43)
    ]
}
```

### Planet Orbs

Configure orbs (allowable deviation) for aspects:

```python
# Tight orbs for precision
tight_orbs = {
    'settings_planet': [
        {
            'id': 0,  # Sun
            'planet_orb': {
                'Radix': {
                    'default': 6,    # Reduced from 10
                    '0': 8,          # Conjunction
                    '90': 6,         # Square
                    '120': 6,        # Trine
                    '180': 6         # Opposition
                }
            }
        }
    ]
}

# Loose orbs for research
loose_orbs = {
    'settings_planet': [
        {
            'id': 0,  # Sun
            'planet_orb': {
                'Radix': {
                    'default': 15,   # Increased
                    '0': 15,
                    '90': 12,
                    '120': 15,
                    '180': 12
                }
            }
        }
    ]
}
```

## Aspect Configuration

### Aspect Structure

```python
aspect_config = {
    'id': '0',                   # Aspect degree as string
    'degree': 0,                 # Exact degree
    'name': 'conjunction',       # Aspect name
    'color': '#4093f4',          # Display color
    'visible': 1,                # Show in chart
    'visible_grid': 1,           # Show in aspect grid
    'is_major': 1,               # Major aspect flag
    'is_minor': 0,               # Minor aspect flag
    'orb': 10                    # Default orb
}
```

### Major Aspects Only

```python
major_aspects_only = {
    'settings_aspect': [
        {'id': '0', 'degree': 0, 'name': 'conjunction', 'visible': 1, 'orb': 10},
        {'id': '60', 'degree': 60, 'name': 'sextile', 'visible': 1, 'orb': 6},
        {'id': '90', 'degree': 90, 'name': 'square', 'visible': 1, 'orb': 8},
        {'id': '120', 'degree': 120, 'name': 'trine', 'visible': 1, 'orb': 8},
        {'id': '180', 'degree': 180, 'name': 'opposition', 'visible': 1, 'orb': 8}
    ]
}
```

### All Aspects (Including Minor)

```python
all_aspects = {
    'settings_aspect': [
        # Major aspects
        {'id': '0', 'degree': 0, 'name': 'conjunction', 'visible': 1, 'orb': 10},
        {'id': '60', 'degree': 60, 'name': 'sextile', 'visible': 1, 'orb': 6},
        {'id': '90', 'degree': 90, 'name': 'square', 'visible': 1, 'orb': 8},
        {'id': '120', 'degree': 120, 'name': 'trine', 'visible': 1, 'orb': 8},
        {'id': '180', 'degree': 180, 'name': 'opposition', 'visible': 1, 'orb': 8},
        
        # Minor aspects
        {'id': '30', 'degree': 30, 'name': 'semi-sextile', 'visible': 1, 'orb': 2},
        {'id': '45', 'degree': 45, 'name': 'semi-square', 'visible': 1, 'orb': 2},
        {'id': '72', 'degree': 72, 'name': 'quintile', 'visible': 1, 'orb': 2},
        {'id': '135', 'degree': 135, 'name': 'sesquiquadrate', 'visible': 1, 'orb': 2},
        {'id': '150', 'degree': 150, 'name': 'quincunx', 'visible': 1, 'orb': 2}
    ]
}
```

## Label Configuration

### Text Labels

```python
labels = {
    'cusp': 'Cusp',
    'longitude': 'Longitude',
    'latitude': 'Latitude',
    'north': 'N',
    'south': 'S',
    'east': 'E',
    'west': 'W',
    'radix': 'Natal',
    'transit': 'Transit',
    'fire': 'Fire',
    'earth': 'Earth',
    'air': 'Air',
    'water': 'Water'
}
```

### Multilingual Labels

```python
# English labels
english_labels = {
    'label': {
        'radix': 'Natal Chart',
        'transit': 'Transit Chart',
        'longitude': 'Longitude',
        'latitude': 'Latitude'
    }
}

# Russian labels
russian_labels = {
    'label': {
        'radix': 'Natal chart',
        'transit': 'Transit chart',
        'longitude': 'Longitude',
        'latitude': 'Latitude'
    }
}

# German labels
german_labels = {
    'label': {
        'radix': 'Geburtshoroskop',
        'transit': 'Transithoroskop',
        'longitude': 'Längengrad',
        'latitude': 'Breitengrad'
    }
}
```

## Predefined Configuration Sets

### Professional Settings

```python
professional_settings = {
    'astrocfg': {
        'houses_system': 'P',        # Placidus
        'zodiactype': 'tropical',
        'postype': 'geo',
        'language': 'en',
        'round_aspects': 1
    },
    'color_codes': {
        'paper_0': '#ffffff',        # White background
        'paper_1': '#000000',        # Black text
        # Professional color scheme
    }
}
```

### Research Settings

```python
research_settings = {
    'astrocfg': {
        'houses_system': 'E',        # Equal houses
        'zodiactype': 'tropical',
        'postype': 'truegeo',        # True geocentric
        'round_aspects': 0           # Exact aspects
    },
    # Include all planets and aspects
    # Minimal visual styling
}
```

### Vedic Settings

```python
vedic_settings = {
    'astrocfg': {
        'houses_system': 'W',        # Whole sign houses
        'zodiactype': 'sidereal',
        'siderealmode': 'LAHIRI',
        'postype': 'geo',
        'language': 'en'
    },
    # Vedic-specific planet priorities
    # Traditional Vedic colors
}
```

## Loading and Saving Configuration

### Loading from File

```python
import json5
from pathlib import Path

def load_settings(filename):
    """Load settings from JSON file."""
    settings_path = Path(__file__).parent / 'settings' / filename
    with open(settings_path, 'r', encoding='utf-8') as f:
        return json5.load(f)

# Load predefined settings
settings = load_settings('settings2.json')
chart = openAstro(event, type="Radix", settings=settings)
```

### Saving Configuration

```python
def save_settings(settings, filename):
    """Save settings to JSON file."""
    settings_path = Path('custom_settings') / filename
    settings_path.parent.mkdir(exist_ok=True)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

# Save custom settings
custom_settings = create_custom_settings()
save_settings(custom_settings, 'my_settings.json')
```

### Merging Configurations

```python
def merge_settings(base_settings, override_settings):
    """Merge two settings dictionaries."""
    merged = base_settings.copy()
    
    for key, value in override_settings.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_settings(merged[key], value)
        else:
            merged[key] = value
    
    return merged

# Combine base settings with customizations
base = load_settings('settings2.json')
custom = {
    'astrocfg': {
        'houses_system': 'K',  # Change to Koch
        'language': 'de'       # Change to German
    }
}
final_settings = merge_settings(base, custom)
```

## Configuration Examples

### Minimal Chart

```python
minimal_settings = {
    'astrocfg': {
        'houses_system': 'E',
        'language': 'en'
    },
    'settings_planet': [
        # Only show traditional planets
        {'id': i, 'visible': 1 if i <= 9 else 0}
        for i in range(23)  # Sun through Pluto only
    ],
    'settings_aspect': [
        # Only major aspects
        {'id': '0', 'visible': 1},    # Conjunction
        {'id': '90', 'visible': 1},   # Square
        {'id': '120', 'visible': 1},  # Trine
        {'id': '180', 'visible': 1}   # Opposition
    ]
}
```

### Detailed Research Chart

```python
research_settings = {
    'astrocfg': {
        'houses_system': 'P',
        'postype': 'truegeo',
        'round_aspects': 0,
        'language': 'en'
    },
    'settings_planet': [
        # Show all available planets/points
        {'id': i, 'visible': 1, 'planet_orb': {'Radix': {'default': 1}}}
        for i in range(43)
    ],
    'settings_aspect': [
        # Include minor aspects with tight orbs
        {'id': str(degree), 'visible': 1, 'orb': 1}
        for degree in [0, 30, 36, 45, 60, 72, 90, 120, 135, 144, 150, 180]
    ]
}
```

This configuration system provides maximum flexibility for customizing OpenAstro2 to specific needs, traditions, or research requirements.
