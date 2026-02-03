# Installation Guide

This guide covers the installation process for OpenAstro2 and its dependencies.

## System Requirements

### Supported Platforms
- **Windows**: Windows 10/11, Windows Server 2019+
- **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 8+, other modern distributions
- **macOS**: macOS 10.15+ (Catalina or later)

### Python Requirements
- **Python Version**: 3.9 or higher
- **Architecture**: 64-bit (recommended)

## Installation Methods

### Method 1: Using pip (Recommended)

```bash
# Install from PyPI (when available)
pip install openastro2

# Or install from source
pip install git+https://github.com/dimmastro/openastro2.git
```

### Method 2: Local Installation

1. **Clone the repository**:
```bash
git clone https://github.com/dimmastro/openastro2.git
cd openastro2
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install the package**:
```bash
python setup.py install
```

### Method 3: Development Installation

For development work:

```bash
git clone https://github.com/dimmastro/openastro2.git
cd openastro2
pip install -e .
```

## Translations

If you add or edit translations under `openastro2/locale/<lang>/LC_MESSAGES/openastro.po`,
rebuild the `.mo` files with:

```bash
openastro2/scripts/update_translations.sh
```

## Dependencies

### Python Packages

OpenAstro2 requires the following Python packages (automatically installed with pip):

```
pyswisseph==2.10.3.2    # Swiss Ephemeris calculations
skyfield==1.46          # Astronomical computations
svgwrite==1.4.3         # SVG generation
pandas==2.0.2           # Data manipulation
numpy==1.26.4           # Numerical operations
pytz                    # Time zone handling
requests==2.31.0        # HTTP client
pydeck==0.8.0          # Geospatial visualization
openpyxl==3.1.5        # Excel file support
ephem==4.2             # Additional ephemeris
geographiclib==2.0     # Geographic calculations
certifi==2023.11.17    # SSL certificates
```

### System Dependencies

Some features require additional system-level packages:

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    librsvg2-bin \
    imagemagick \
    python3-dev \
    build-essential
```

#### CentOS/RHEL/Fedora
```bash
sudo yum install -y \
    librsvg2-tools \
    ImageMagick \
    python3-devel \
    gcc \
    gcc-c++
```

#### macOS
```bash
# Using Homebrew
brew install librsvg imagemagick

# Using MacPorts
sudo port install librsvg2 ImageMagick
```

#### Windows
- **librsvg**: Download from [librsvg website](https://librsvg.org/)
- **ImageMagick**: Download from [ImageMagick website](https://imagemagick.org/)
- Ensure binaries are in your system PATH

## Platform-Specific Instructions

### Windows

1. **Install Python 3.9+** from [python.org](https://python.org)
2. **Install Visual C++ Build Tools** (if compiling from source)
3. **Run installation**:
```cmd
py -m pip install -r requirements.txt
py setup.py install
```

### Linux

Most modern Linux distributions should work without issues:

```bash
# Ensure Python 3.9+ is installed
python3 --version

# Install system dependencies
sudo apt-get install librsvg2-bin imagemagick

# Install OpenAstro2
pip3 install -r requirements.txt
python3 setup.py install
```

### macOS

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install python librsvg imagemagick

# Install OpenAstro2
pip3 install -r requirements.txt
python3 setup.py install
```

## Verification

### Basic Installation Test

Create a test file `test_installation.py`:

```python
#!/usr/bin/env python3

try:
    from openastro2.openastro2 import openAstro
    print("✓ OpenAstro2 imported successfully")
    
    # Test basic functionality
    event = openAstro.event("Test", 2000, 1, 1, 12, 0, 0, 
                           timezone=0, location="London", 
                           geolat=51.5074, geolon=-0.1278)
    chart = openAstro(event, type="Radix")
    print("✓ Basic chart creation successful")
    
    # Test SVG generation
    svg = chart.makeSVG2()
    if '<svg' in svg and '</svg>' in svg:
        print("✓ SVG generation successful")
    else:
        print("✗ SVG generation failed")
        
except ImportError as e:
    print(f"✗ Import failed: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run the test:
```bash
python test_installation.py
```

### Run Unit Tests

```bash
# Navigate to the project directory
cd openastro2

# Run tests
python -m pytest tests/
```

## Configuration

### Environment Variables

Optional environment variables:

```bash
# Swiss Ephemeris data directory (optional)
export SWISSEPH_DIR=/path/to/swiss/ephemeris/data

# Timezone database location (optional)
export TZDATA_DIR=/path/to/timezone/data
```

### First Run Setup

On first run, OpenAstro2 will:

1. Create configuration directory: `~/.openastro.org/`
2. Download Swiss Ephemeris data files (if needed)
3. Initialize default settings

## Troubleshooting

### Common Issues

#### "No module named 'swisseph'"
```bash
pip install pyswisseph==2.10.3.2
```

#### "rsvg-convert not found"
Install librsvg2-bin (Linux) or librsvg (macOS/Windows)

#### "Permission denied" errors
```bash
# Use user installation
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Swiss Ephemeris data issues
```bash
# Clear cache and re-download
rm -rf ~/.openastro.org/swiss_ephemeris/
# Restart Python and create a chart
```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting section](troubleshooting.md)
2. Search existing issues on GitHub
3. Create a new issue with:
   - Your operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

## Virtual Environment (Recommended)

Using a virtual environment prevents conflicts:

```bash
# Create virtual environment
python -m venv openastro2-env

# Activate it
source openastro2-env/bin/activate  # Linux/macOS
# or
openastro2-env\Scripts\activate     # Windows

# Install OpenAstro2
pip install -r requirements.txt
python setup.py install

# When done, deactivate
deactivate
```

## Next Steps

After successful installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Explore [Examples](examples.md)
3. Review the [API Reference](api-reference.md)
4. Check out [Configuration Options](configuration.md)
