from openastro2.openastro2 import openAstro

# Create test chart
event = openAstro.event('Test', 2000, 1, 1, 12, 0, 0)
chart = openAstro(event, type="Radix")

# Find planet-related attributes
planet_attrs = [attr for attr in dir(chart) if 'planet' in attr.lower()]
print("Planet-related attributes:", planet_attrs)

# Find degree-related attributes
degree_attrs = [attr for attr in dir(chart) if 'degree' in attr.lower()]
print("Degree-related attributes:", degree_attrs)

# Find sign-related attributes
sign_attrs = [attr for attr in dir(chart) if 'sign' in attr.lower()]
print("Sign-related attributes:", sign_attrs)

# Try to access some common attributes
try:
    if hasattr(chart, 'planets_degree_ut'):
        print(f"planets_degree_ut: {chart.planets_degree_ut[:5]}")
    if hasattr(chart, 'planets_sign'):
        print(f"planets_sign: {chart.planets_sign[:5]}")
    if hasattr(chart, 'houses_degree_ut'):
        print(f"houses_degree_ut: {chart.houses_degree_ut[:5]}")
except Exception as e:
    print(f"Error accessing attributes: {e}")