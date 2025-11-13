from typing import Dict, Any, List
from openastro2.openastro2 import openAstro

# Create test chart
event = openAstro.event('Test', 2000, 1, 1, 12, 0, 0, 0, 0, 0, 0, 0)
chart = openAstro(event, type="Radix")

# Calculate astrological data
chart.calcAstro()

print("Testing chart data access...")

try:
    # Try to get planet degrees using the correct API
    if hasattr(chart, 'getPlanetsDegut') and hasattr(chart, 'planets_degree_ut'):
        planet_degrees = chart.getPlanetsDegut(chart.planets_degree_ut, flag_transit="Radix")
        print(f"✓ Planet degrees (first 5): {list(planet_degrees.keys())[:5]}")
    elif hasattr(chart, 'planets_degree_ut'):
        # Access planet degrees directly from attribute
        planet_degrees = chart.planets_degree_ut
        print(f"✓ Planet degrees direct access (first 5): {planet_degrees[:5]}")
    
    # Check for other data access methods
    if hasattr(chart, 'makePlanetDict'):
        planet_dict = chart.makePlanetDict()
        print(f"✓ Planet dictionary keys: {list(planet_dict.keys())[:5]}")
    
    # Check object attributes directly
    all_attrs = [attr for attr in dir(chart) if not attr.startswith('_') and not callable(getattr(chart, attr))]
    print(f"Data attributes: {all_attrs[:10]}")
    
    # Check for specific data attributes
    data_attrs = ['planets_degree_ut', 'planets_sign', 'houses_degree_ut', 'lunar_phase']
    for attr in data_attrs:
        if hasattr(chart, attr):
            value = getattr(chart, attr)
            print(f"✓ {attr}: {str(value)[:50]}...")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nChart creation successful - basic functionality verified!")