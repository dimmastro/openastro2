# Overview

OpenAstro2 is a comprehensive Python library for astrological calculations and chart generation. It provides high-precision astronomical computations using the Swiss Ephemeris and supports multiple chart types, visualization formats, and configuration options.

## What is OpenAstro2?

OpenAstro2 is designed to solve core problems in astrological software development:

- **Precise Calculations**: Uses Swiss Ephemeris for accurate planetary positions
- **Multiple Chart Types**: Supports natal, transit, progression, and specialized charts
- **Flexible Visualization**: Generates SVG-based charts with customizable appearance
- **Comprehensive Features**: Includes aspects, houses, dignities, fixed stars, and geographical astrology
- **Extensible Design**: Modular architecture allows for custom extensions

## Key Features

### Chart Types
- **Radix/Natal Charts**: Basic birth chart calculations
- **Transit Charts**: Current planetary positions overlaid on natal chart
- **Progression Charts**: Secondary progressions and directions
- **Solar/Lunar Returns**: Annual and monthly return charts
- **New Moon/Full Moon**: Lunation charts
- **Local Space Maps**: Geographical astrology projections
- **AstroMaps**: Astrocartography functionality

### Calculation Features
- **High Precision**: Swiss Ephemeris integration for accurate positions
- **Multiple Coordinate Systems**: Apparent geocentric, true geocentric, topocentric, heliocentric
- **House Systems**: Support for 20+ house systems (Placidus, Koch, Equal, etc.)
- **Zodiac Types**: Tropical and sidereal zodiac with multiple ayanamsas
- **Aspects**: Major and minor aspects with customizable orbs
- **Fixed Stars**: Integration with star catalog
- **Dignities**: Essential and accidental dignity calculations

### Visualization
- **SVG Output**: Scalable vector graphics for high-quality charts
- **Customizable Appearance**: Colors, fonts, symbols, and layout options
- **Multiple Styles**: European and other traditional chart layouts
- **Export Options**: Various image formats through external tools

### Technical Capabilities
- **Time Zone Handling**: Automatic time zone conversion and DST
- **Location Database**: Built-in geographical database
- **Regression Testing**: Comprehensive test suite for accuracy
- **Multilingual Support**: Multiple language interfaces
- **Configuration System**: JSON-based settings management

## Architecture

OpenAstro2 follows a modular architecture with clear separation of concerns:

### Core Modules
- **`openastro2.py`**: Main API and chart generation logic
- **`swiss.py`**: Swiss Ephemeris interface and calculations
- **`dignities.py`**: Planetary dignity and reception calculations
- **`utils.py`**: Utility functions for time, coordinates, and data processing

### Supporting Systems
- **Settings Management**: JSON configuration files for chart types and appearance
- **Template System**: SVG templates for chart rendering
- **Data Modules**: Geographical data, time zones, and fixed star catalogs
- **Testing Framework**: Regression tests and unit tests

## Use Cases

OpenAstro2 is suitable for:

### Professional Astrologers
- Accurate chart calculations for client work
- Custom chart styles and branding
- Batch processing for research

### Software Developers
- Integration into astrology applications
- Web service backends
- Educational tools and calculators

### Researchers
- Statistical analysis of astrological data
- Historical chart recreation
- Astronomical research applications

### Students and Enthusiasts
- Learning astrological calculations
- Personal chart analysis
- Educational projects

## Technology Stack

- **Python 3.9+**: Core language requirement
- **Swiss Ephemeris**: High-precision astronomical calculations
- **Skyfield**: Additional astronomical computations
- **SVG Generation**: Vector graphics output
- **NumPy/SciPy**: Mathematical operations
- **Pandas**: Data manipulation
- **PyTZ**: Time zone handling

## Accuracy and Reliability

OpenAstro2 prioritizes accuracy through:

- **Swiss Ephemeris**: Industry-standard astronomical library
- **Regression Testing**: Comprehensive test suite comparing results
- **Validation**: Cross-checking with established astrological software
- **Precision**: Calculations accurate to arc-seconds
- **Standards Compliance**: Following astronomical and astrological conventions

## Extensibility

The library is designed for extension:

- **Plugin Architecture**: Custom modules can be added
- **Configuration System**: Flexible settings management
- **Template System**: Custom chart layouts and styles
- **API Design**: Clean interfaces for integration

## Community and Support

OpenAstro2 is open source software released under the GPL license, encouraging:

- Community contributions and improvements
- Transparent development process
- Free usage for educational and personal purposes
- Commercial licensing options available