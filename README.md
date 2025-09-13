# OpenAstro2

**A comprehensive Python library for astrological calculations and chart generation**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-GPL-green.svg)](LICENSE)
[![Tests](https://github.com/dimmastro/openastro2/workflows/Tests/badge.svg)](https://github.com/dimmastro/openastro2/actions)

OpenAstro2 provides high-precision astrological calculations using the Swiss Ephemeris, supporting multiple chart types, house systems, and coordinate systems. It generates professional-quality SVG charts with extensive customization options.

## ✨ Features

### 🗓️ Chart Types
- **Natal/Radix Charts** - Birth chart analysis
- **Transit Charts** - Current planetary influences  
- **Progression Charts** - Secondary progressions and directions
- **Solar/Lunar Returns** - Annual and monthly return charts
- **Lunation Charts** - New Moon and Full Moon charts
- **Geographic Astrology** - Local Space Maps and AstroMaps
- **Fixed Star Charts** - Fixed star influences

### 🏠 House Systems
- Placidus, Koch, Equal, Whole Sign, Regiomontanus
- Campanus, Morinus, Porphyrius, Topocentric
- And 15+ more systems

### 🌍 Coordinate Systems
- Apparent Geocentric (default)
- True Geocentric
- Topocentric
- Heliocentric

### 🎨 Visualization
- High-quality SVG chart generation
- Customizable colors, symbols, and layouts
- European and other traditional chart styles
- Export to various image formats

## 🚀 Quick Start

### Installation

```bash
pip install openastro2
```

### Basic Usage

```python
from openastro2.openastro2 import openAstro

# Create a birth event
event = openAstro.event(
    name="John Doe",
    year=1990, month=6, day=15,
    hour=14, minute=30, second=0,
    timezone=2,  # UTC+2
    location="Berlin",
    geolat=52.5200, geolon=13.4050
)

# Generate natal chart
chart = openAstro(event, type="Radix")

# Get planet positions
print(f"Sun position: {chart.planets_degree_ut[0]:.2f}°")
print(f"Moon sign: {chart.planets_sign[1]}")  # 0=Aries, 1=Taurus, etc.

# Generate SVG chart
svg_content = chart.makeSVG2()
with open("natal_chart.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

### Current Transits

```python
# Get current transits
transit_chart = openAstro(event, type="Transit")

# Or for specific date
transit_event = openAstro.event_dt_str(
    "Transit", "2024-12-25 12:00:00",
    timezone=2, location="Berlin",
    geolat=52.5200, geolon=13.4050
)
transit_chart = openAstro(event, transit_event, type="Transit")
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Quick Start](docs/quickstart.md)** - Get started in minutes
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Chart Types](docs/chart-types.md)** - All available chart types
- **[Configuration](docs/configuration.md)** - Customization options
- **[Examples](docs/examples.md)** - Practical usage examples
- **[Testing](docs/testing.md)** - Testing framework
- **[Contributing](docs/contributing.md)** - How to contribute
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🌐 Online Examples

Try OpenAstro2 in Google Colab:

- [Basic Chart Generation](https://colab.research.google.com/drive/1kfohBTCbLnVZ3NAg6QSwqzG7nhhzY3XX?usp=sharing)
- [Transit Analysis](https://colab.research.google.com/drive/1Xw_Yb7hLIsIK6HQWgvmM5nVyhgSeDiqe?usp=sharing)
- [Multiple Chart Types](https://colab.research.google.com/drive/1bIYvXDyVwZ0IJl0KY54Cutozu-ZB7xyg?usp=sharing)
- [Advanced Features](https://colab.research.google.com/drive/1-ujLJZQy693fnb15RNXuDcHKmLa6CVN9?usp=sharing)

## 🛠️ System Requirements

### Python Requirements
- **Python 3.9+** (3.11+ recommended)
- **64-bit architecture** recommended

### Core Dependencies
- `pyswisseph>=2.10.3.2` - Swiss Ephemeris calculations
- `skyfield>=1.46` - Astronomical computations
- `svgwrite>=1.4.3` - SVG generation
- `pandas>=2.0.2` - Data manipulation
- `numpy>=1.26.4` - Numerical operations

### System Dependencies (Optional)
- `librsvg2-bin` - SVG to image conversion
- `imagemagick` - Additional image formats

## 🎯 Use Cases

### Professional Astrologers
```python
# Generate client chart with custom settings
settings = {
    'astrocfg': {
        'houses_system': 'P',  # Placidus
        'language': 'en',
        'zodiactype': 'tropical'
    }
}
chart = openAstro(client_event, type="Radix", settings=settings)
```

### Research Applications
```python
# Batch process multiple charts
people_data = [...] # List of birth data
results = []

for person in people_data:
    event = openAstro.event(**person)
    chart = openAstro(event, type="Radix")
    results.append({
        'name': person['name'],
        'sun_sign': chart.planets_sign[0],
        'moon_sign': chart.planets_sign[1]
    })
```

### Web Applications
```python
# API endpoint for chart generation
def generate_chart_api(birth_data):
    try:
        event = openAstro.event(**birth_data)
        chart = openAstro(event, type="Radix")
        return {'svg': chart.makeSVG2(), 'status': 'success'}
    except Exception as e:
        return {'error': str(e), 'status': 'error'}
```

## 🧪 Testing

```bash
# Run test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=openastro2 --cov-report=html

# Run specific test
pytest tests/test_chart_list.py::test_openastro_types -v
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/dimmastro/openastro2.git
cd openastro2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## 📜 License

OpenAstro2 is released under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Swiss Ephemeris** by Astrodienst for accurate astronomical calculations
- **Original OpenAstro** project by Pelle van der Scheer
- **Contributors** who help improve the project

## 📞 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/dimmastro/openastro2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dimmastro/openastro2/discussions)

---

**OpenAstro2** - Making professional astrological calculations accessible to everyone.



