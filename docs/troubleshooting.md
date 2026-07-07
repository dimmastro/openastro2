# Troubleshooting

This guide helps resolve common issues when installing and using OpenAstro2.

## Installation Issues

### Python Version Problems

**Problem**: "Python version not supported" or import errors
```
ERROR: Python 3.8 is not supported, requires Python 3.9+
```

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.9+ if needed
# Visit https://python.org/downloads/

# Use specific Python version
python3.9 -m pip install openastro2
```

### Swiss Ephemeris Issues

**Problem**: "No module named 'swisseph'" or Swiss Ephemeris errors
```
ImportError: No module named 'swisseph'
RuntimeError: Swiss Ephemeris file not found
```

**Solutions**:
```bash
# Install pyswisseph explicitly
pip install pyswisseph==2.10.3.2

# Clear and reinstall if corrupted
pip uninstall pyswisseph
pip install pyswisseph==2.10.3.2

# Check installation
python -c "import swisseph; print('Swiss Ephemeris OK')"
```

### System Dependencies Missing

**Problem**: "rsvg-convert not found" or "ImageMagick not found"

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install librsvg2-bin imagemagick
```

**CentOS/RHEL/Fedora**:
```bash
sudo yum install librsvg2-tools ImageMagick
# or on newer systems:
sudo dnf install librsvg2-tools ImageMagick
```

**macOS**:
```bash
# Using Homebrew
brew install librsvg imagemagick

# Using MacPorts
sudo port install librsvg2 ImageMagick
```

**Windows**:
1. Download librsvg from [librsvg.org](https://librsvg.org/)
2. Download ImageMagick from [imagemagick.org](https://imagemagick.org/)
3. Add both to your system PATH

### Permission Errors

**Problem**: "Permission denied" during installation
```bash
# Use user installation instead of system-wide
pip install --user openastro2

# Or use virtual environment
python -m venv openastro2_env
source openastro2_env/bin/activate  # Linux/macOS
openastro2_env\Scripts\activate     # Windows
pip install openastro2
```

## Runtime Errors

### Import Errors

**Problem**: "No module named 'openastro2'" after installation

**Check installation**:
```python
import sys
print(sys.path)

# Verify package location
pip show openastro2
```

**Solutions**:
```bash
# Reinstall in current environment
pip uninstall openastro2
pip install openastro2

# Check for multiple Python installations
which python
which pip

# Use specific Python/pip
python3 -m pip install openastro2
```

### Chart Creation Errors

**Problem**: Charts fail to generate or return empty/invalid data

**Debugging steps**:
```python
from openastro2.openastro2 import openAstro

# Test with simple, known-good data
try:
    event = openAstro.event(
        "Test", 2000, 1, 1, 12, 0, 0,
        timezone=0, location="London",
        geolat=51.5074, geolon=-0.1278
    )
    print("Event created successfully")
    
    chart = openAstro(event, type="Radix")
    print("Chart created successfully")
    
    svg = chart.makeSVG2()
    print(f"SVG generated, length: {len(svg)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

### Date/Time Issues

**Problem**: Invalid dates or time zone errors

**Common mistakes**:
```python
# WRONG - Invalid date
event = openAstro.event("Test", 2000, 2, 30, 12, 0, 0)  # Feb 30 doesn't exist

# WRONG - Invalid time
event = openAstro.event("Test", 2000, 1, 1, 25, 0, 0)   # Hour 25 doesn't exist

# WRONG - Extreme timezone
event = openAstro.event("Test", 2000, 1, 1, 12, 0, 0, timezone=15)  # UTC+15 invalid

# CORRECT
event = openAstro.event("Test", 2000, 2, 29, 12, 0, 0)  # Leap year date
event = openAstro.event("Test", 2000, 1, 1, 23, 59, 59) # Valid time
event = openAstro.event("Test", 2000, 1, 1, 12, 0, 0, timezone=-8)  # Valid timezone
```

**Validate inputs**:
```python
def validate_date(year, month, day, hour, minute, second, timezone):
    """Validate date/time inputs before creating event."""
    
    # Check basic ranges
    if not (1 <= month <= 12):
        raise ValueError(f"Invalid month: {month}")
    
    if not (1 <= day <= 31):
        raise ValueError(f"Invalid day: {day}")
    
    if not (0 <= hour <= 23):
        raise ValueError(f"Invalid hour: {hour}")
    
    if not (0 <= minute <= 59):
        raise ValueError(f"Invalid minute: {minute}")
    
    if not (0 <= second <= 59):
        raise ValueError(f"Invalid second: {second}")
    
    if not (-12 <= timezone <= 14):
        raise ValueError(f"Invalid timezone: {timezone}")
    
    # Check date validity
    from datetime import datetime
    try:
        datetime(year, month, day, hour, minute, second)
    except ValueError as e:
        raise ValueError(f"Invalid date/time: {e}")

# Usage
validate_date(2000, 2, 29, 12, 30, 0, 2)  # Will pass
event = openAstro.event("Test", 2000, 2, 29, 12, 30, 0, timezone=2)
```

### Coordinate Issues

**Problem**: Invalid geographic coordinates

**Validation**:
```python
def validate_coordinates(latitude, longitude):
    """Validate geographic coordinates."""
    
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Invalid latitude: {latitude} (must be -90 to 90)")
    
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Invalid longitude: {longitude} (must be -180 to 180)")

# Usage
validate_coordinates(51.5074, -0.1278)  # London - OK
validate_coordinates(91.0, 0.0)         # Error - invalid latitude
```

### SVG Generation Problems

**Problem**: SVG output is empty, corrupted, or missing elements

**Debugging**:
```python
chart = openAstro(event, type="Radix")
svg = chart.makeSVG2()

# Check SVG structure
print(f"SVG length: {len(svg)}")
print(f"Starts with <svg: {'<svg' in svg}")
print(f"Ends with </svg>: {'</svg>' in svg}")

# Save for inspection
with open("debug_chart.svg", "w", encoding="utf-8") as f:
    f.write(svg)

# Check for errors in content
if len(svg) < 1000:  # Suspiciously short
    print("Warning: SVG seems too short")

if "error" in svg.lower() or "exception" in svg.lower():
    print("Warning: SVG may contain error messages")
```

## Configuration Issues

### Settings Problems

**Problem**: Custom settings not being applied

**Debug settings loading**:
```python
import json
from pathlib import Path

# Check settings file exists and is valid
settings_file = Path("my_settings.json")
if settings_file.exists():
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        print("Settings loaded successfully")
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
else:
    print("Settings file not found")

# Verify settings structure
required_keys = ['astrocfg', 'color_codes', 'settings_planet', 'settings_aspect']
for key in required_keys:
    if key not in settings:
        print(f"Warning: Missing settings key: {key}")
```

### House System Issues

**Problem**: Unexpected house calculations

**Test different house systems**:
```python
house_systems = {
    'P': 'Placidus',
    'K': 'Koch', 
    'E': 'Equal',
    'W': 'Whole Sign'
}

event = openAstro.event("Test", 1990, 6, 15, 12, 0, 0)

for code, name in house_systems.items():
    settings = {'astrocfg': {'houses_system': code}}
    chart = openAstro(event, type="Radix", settings=settings)
    
    print(f"\n{name} ({code}):")
    print(f"ASC: {chart.houses_degree_ut[0]:.2f}°")
    print(f"MC:  {chart.houses_degree_ut[9]:.2f}°")
```

## Performance Issues

### Slow Chart Generation

**Problem**: Charts take too long to generate

**Profiling**:
```python
import time
import cProfile

def profile_chart_creation():
    """Profile chart creation performance."""
    
    event = openAstro.event("Test", 1990, 1, 1, 12, 0, 0)
    
    start_time = time.time()
    chart = openAstro(event, type="Radix")
    creation_time = time.time() - start_time
    
    start_time = time.time()
    svg = chart.makeSVG2()
    svg_time = time.time() - start_time
    
    print(f"Chart creation: {creation_time:.3f}s")
    print(f"SVG generation: {svg_time:.3f}s")
    print(f"Total time: {creation_time + svg_time:.3f}s")

# Run profiling
cProfile.run('profile_chart_creation()')
```

**Optimization tips**:
```python
# Reuse settings objects
settings = {'astrocfg': {'language': 'en'}}
for event in events:
    chart = openAstro(event, type="Radix", settings=settings)

# Cache complex calculations
chart_cache = {}
def get_cached_chart(event_key):
    if event_key not in chart_cache:
        chart_cache[event_key] = openAstro(event, type="Radix")
    return chart_cache[event_key]
```

### Memory Issues

**Problem**: High memory usage with multiple charts

**Memory monitoring**:
```python
import psutil
import gc

def monitor_memory():
    """Monitor memory usage during chart generation."""
    
    process = psutil.Process()
    
    for i in range(10):
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        event = openAstro.event(f"Test {i}", 1990 + i, 1, 1, 12, 0, 0)
        chart = openAstro(event, type="Radix")
        svg = chart.makeSVG2()
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Chart {i}: {memory_after - memory_before:.1f} MB increase")
        
        # Force garbage collection
        del chart, svg
        gc.collect()

monitor_memory()
```

## Platform-Specific Issues

### Windows Issues

**Problem**: Path separators or encoding issues

**Solutions**:
```python
import os
from pathlib import Path

# Use Path objects for cross-platform compatibility
output_path = Path("charts") / "natal_chart.svg"
output_path.parent.mkdir(exist_ok=True)

# Specify encoding explicitly
with open(output_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

# Handle Windows path limitations
if os.name == 'nt':  # Windows
    # Avoid long paths, special characters
    safe_filename = "chart.svg"
else:
    safe_filename = "natal_chart_with_unicode_✨.svg"
```

### macOS Issues

**Problem**: Permission errors or missing system libraries

**Solutions**:
```bash
# Install command line tools
xcode-select --install

# Use Homebrew for dependencies
brew install python librsvg imagemagick

# Check system integrity
brew doctor
```

### Linux Issues

**Problem**: Missing system packages or permission errors

**Solutions**:
```bash
# Update package manager
sudo apt-get update  # Debian/Ubuntu
sudo yum update      # CentOS/RHEL

# Install build essentials if compiling from source
sudo apt-get install build-essential python3-dev

# Check library paths
ldconfig -p | grep rsvg
```

## Debug Mode

### Enable Debugging

```python
from openastro2.openastro2 import DEBUG, dprint

# Enable debug output
DEBUG = True

# Use debug print
dprint("Debug message will be shown")

# Verbose error reporting
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Collecting Debug Information

```python
def collect_debug_info():
    """Collect system information for debugging."""
    
    import sys
    import platform
    import pkg_resources
    
    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'openastro2_version': pkg_resources.get_distribution('openastro2').version,
        'swisseph_version': None,
        'numpy_version': None
    }
    
    try:
        import swisseph
        info['swisseph_version'] = swisseph.version
    except ImportError:
        info['swisseph_version'] = 'Not installed'
    
    try:
        import numpy
        info['numpy_version'] = numpy.__version__
    except ImportError:
        info['numpy_version'] = 'Not installed'
    
    return info

# Print debug info
debug_info = collect_debug_info()
for key, value in debug_info.items():
    print(f"{key}: {value}")
```

## Getting Help

### Creating Bug Reports

Include this information in bug reports:

1. **System information** (from `collect_debug_info()` above)
2. **Complete error message** with traceback
3. **Minimal reproduction case**:
```python
from openastro2.openastro2 import openAstro

# Minimal example that demonstrates the problem
event = openAstro.event("Bug Report", 2000, 1, 1, 12, 0, 0)
chart = openAstro(event, type="Radix")
# Error occurs here
```

4. **Expected vs actual behavior**
5. **Steps to reproduce**

### Common Solutions Checklist

Before reporting issues, try:

- [ ] **Update to latest version**: `pip install --upgrade openastro2`
- [ ] **Reinstall dependencies**: `pip install --force-reinstall -r requirements.txt`
- [ ] **Clear Python cache**: `find . -name "*.pyc" -delete; find . -name "__pycache__" -delete`
- [ ] **Try in clean environment**: Create new virtual environment
- [ ] **Check system dependencies**: Ensure librsvg2-bin and imagemagick are installed
- [ ] **Verify file permissions**: Ensure write access to output directories
- [ ] **Test with minimal example**: Use simple, known-good data

### Community Resources

- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check all documentation sections
- **Examples**: Review the examples in the docs
- **Stack Overflow**: Search for "openastro2" or "pyswisseph" tags

Remember to search existing issues before creating new ones, as your problem may already have a solution!
