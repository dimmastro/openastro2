# Testing

OpenAstro2 includes a comprehensive testing framework to ensure accuracy and reliability of calculations.

## Test Structure

The test suite is organized into several categories:

```
tests/
├── test_chart_list.py              # Chart type tests
├── test_time_conversion.py         # Time handling tests
└── tests_regressions/
    ├── test_chart_list_regressions.py  # Regression tests
    └── readme.md                    # Regression test documentation
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_chart_list.py

# Run with verbose output
pytest tests/ -v

# Run specific test function
pytest tests/test_chart_list.py::test_openastro_types
```

### Test Coverage

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=openastro2 --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Chart Type Tests

### Basic Chart Generation Test

```python
import pytest
from openastro2.openastro2 import openAstro

def test_basic_chart_creation():
    """Test basic chart creation functionality."""
    
    # Create test event
    event = openAstro.event(
        "Test Person", 2000, 1, 1, 12, 0, 0,
        timezone=0, location="London",
        geolat=51.5074, geolon=-0.1278
    )
    
    # Create chart
    chart = openAstro(event, type="Radix")
    
    # Basic assertions
    assert chart is not None
    assert hasattr(chart, 'planets_degree_ut')
    assert hasattr(chart, 'planets_sign')
    assert hasattr(chart, 'houses_degree_ut')
    
    # Check data integrity
    assert len(chart.planets_degree_ut) > 0
    assert len(chart.planets_sign) > 0
    assert len(chart.houses_degree_ut) == 12
    
    # Test SVG generation
    svg = chart.makeSVG2()
    assert isinstance(svg, str)
    assert '<svg' in svg
    assert '</svg>' in svg
```

### Parameterized Chart Type Tests

```python
CHART_TYPES = [
    "Radix", "Transit", "SProgression", "Direction",
    "Solar", "Lunar", "NewMoonNext", "FullMoonNext"
]

@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_chart_types(chart_type):
    """Test all supported chart types."""
    
    event1 = openAstro.event(
        "Person 1", 1990, 6, 15, 14, 30, 0,
        timezone=2, location="Berlin",
        geolat=52.5200, geolon=13.4050
    )
    
    event2 = openAstro.event(
        "Person 2", 2000, 1, 1, 12, 0, 0,
        timezone=2, location="Berlin", 
        geolat=52.5200, geolon=13.4050
    )
    
    # Create chart (some types need two events)
    if chart_type in ["Transit", "SProgression", "Direction"]:
        chart = openAstro(event1, event2, type=chart_type)
    else:
        chart = openAstro(event1, type=chart_type)
    
    # Verify chart creation
    assert chart is not None
    assert hasattr(chart, 'hour')
    
    # Test SVG generation
    svg = chart.makeSVG2()
    assert isinstance(svg, str)
    assert len(svg) > 100  # Should be substantial content
```

## Data Validation Tests

### Planet Position Tests

```python
def test_planet_positions():
    """Test planet position calculations."""
    
    # Known birth data for testing
    event = openAstro.event(
        "Test", 1990, 6, 21, 12, 0, 0,  # Summer solstice
        timezone=0, location="Greenwich",
        geolat=51.4769, geolon=0.0
    )
    
    chart = openAstro(event, type="Radix")
    
    # Sun should be around 0° Cancer (90°) at summer solstice
    sun_position = chart.planets_degree_ut[0]
    sun_sign = chart.planets_sign[0]
    
    # Allow some tolerance for exact time
    assert 85 <= sun_position <= 95, f"Sun position {sun_position}° seems incorrect"
    assert sun_sign == 3, f"Sun should be in Cancer (3), got {sun_sign}"
    
    # All planet positions should be valid (0-360°)
    for i, pos in enumerate(chart.planets_degree_ut[:10]):  # Main planets
        assert 0 <= pos < 360, f"Planet {i} position {pos}° out of range"
    
    # All signs should be valid (0-11)
    for i, sign in enumerate(chart.planets_sign[:10]):
        assert 0 <= sign <= 11, f"Planet {i} sign {sign} out of range"
```

### House Calculation Tests

```python
def test_house_calculations():
    """Test house cusp calculations."""
    
    event = openAstro.event(
        "Test", 2000, 1, 1, 0, 0, 0,
        timezone=0, location="London",
        geolat=51.5074, geolon=-0.1278
    )
    
    chart = openAstro(event, type="Radix")
    
    # Should have 12 house cusps
    assert len(chart.houses_degree_ut) >= 12
    
    # All house cusps should be valid degrees
    for i, cusp in enumerate(chart.houses_degree_ut[:12]):
        assert 0 <= cusp < 360, f"House {i+1} cusp {cusp}° out of range"
    
    # Houses should be in ascending order (with wraparound)
    ascendant = chart.houses_degree_ut[0]
    assert 0 <= ascendant < 360
```

### Time Conversion Tests

```python
def test_time_conversions():
    """Test time zone and date conversions."""
    
    from openastromod.utils import utc_to_local, local_to_utc
    from datetime import datetime
    
    # Test UTC to local conversion
    utc_time = datetime(2000, 1, 1, 12, 0, 0)
    timezone_offset = 2  # UTC+2
    
    local_time = utc_to_local(utc_time, timezone_offset)
    expected_local = datetime(2000, 1, 1, 14, 0, 0)
    
    assert local_time.hour == expected_local.hour
    
    # Test reverse conversion
    back_to_utc = local_to_utc(local_time, timezone_offset)
    assert back_to_utc.hour == utc_time.hour
```

## Regression Tests

### Chart Comparison Tests

```python
import pytest
from pytest_regressions.data_regression import DataRegressionFixture

def test_chart_regression(data_regression: DataRegressionFixture):
    """Regression test to ensure chart calculations remain consistent."""
    
    # Fixed test data
    event = openAstro.event(
        "Regression Test", 1985, 5, 10, 15, 30, 0,
        timezone=1, location="Paris",
        geolat=48.8566, geolon=2.3522
    )
    
    chart = openAstro(event, type="Radix")
    
    # Extract key data for comparison
    test_data = {
        'planets_degrees': [round(deg, 4) for deg in chart.planets_degree_ut[:10]],
        'planets_signs': chart.planets_sign[:10],
        'house_cusps': [round(deg, 4) for deg in chart.houses_degree_ut[:12]],
        'lunar_phase_degrees': round(chart.lunar_phase.get('degrees', 0), 4)
    }
    
    # Compare with stored regression data
    data_regression.check(test_data)
```

### Historical Data Validation

```python
def test_historical_accuracy():
    """Test accuracy against known historical events."""
    
    # Eclipse test - Total solar eclipse August 21, 2017
    eclipse_event = openAstro.event(
        "Eclipse Test", 2017, 8, 21, 18, 26, 0,
        timezone=0, location="Carbondale, IL",
        geolat=37.7272, geolon=-89.2175
    )
    
    chart = openAstro(eclipse_event, type="Radix")
    
    # Sun and Moon should be very close (New Moon)
    sun_pos = chart.planets_degree_ut[0]
    moon_pos = chart.planets_degree_ut[1]
    
    diff = abs(sun_pos - moon_pos)
    if diff > 180:
        diff = 360 - diff
    
    # Should be within 1 degree for eclipse
    assert diff < 1.0, f"Sun-Moon separation {diff}° too large for eclipse"
    
    # Both should be in Leo (sign 4) around 28-29 degrees
    sun_sign = chart.planets_sign[0]
    moon_sign = chart.planets_sign[1]
    
    assert sun_sign == 4, f"Sun should be in Leo (4), got {sun_sign}"
    assert moon_sign == 4, f"Moon should be in Leo (4), got {moon_sign}"
```

## Performance Tests

### Speed Benchmarks

```python
import time
import pytest

def test_chart_generation_speed():
    """Test chart generation performance."""
    
    event = openAstro.event(
        "Speed Test", 1990, 1, 1, 12, 0, 0,
        timezone=0, location="London",
        geolat=51.5074, geolon=-0.1278
    )
    
    # Time chart creation
    start_time = time.time()
    chart = openAstro(event, type="Radix")
    creation_time = time.time() - start_time
    
    # Should create chart in reasonable time (< 2 seconds)
    assert creation_time < 2.0, f"Chart creation took {creation_time:.2f}s"
    
    # Time SVG generation
    start_time = time.time()
    svg = chart.makeSVG2()
    svg_time = time.time() - start_time
    
    # SVG generation should be fast (< 1 second)
    assert svg_time < 1.0, f"SVG generation took {svg_time:.2f}s"

def test_batch_processing_performance():
    """Test performance with multiple charts."""
    
    events = []
    for i in range(10):
        event = openAstro.event(
            f"Test {i}", 1990 + i, 1, 1, 12, 0, 0,
            timezone=0, location="London",
            geolat=51.5074, geolon=-0.1278
        )
        events.append(event)
    
    start_time = time.time()
    
    for event in events:
        chart = openAstro(event, type="Radix")
        svg = chart.makeSVG2()
    
    total_time = time.time() - start_time
    avg_time = total_time / len(events)
    
    # Average should be reasonable
    assert avg_time < 1.0, f"Average chart time {avg_time:.2f}s too slow"
```

## Error Handling Tests

### Invalid Input Tests

```python
def test_invalid_dates():
    """Test handling of invalid dates."""
    
    with pytest.raises(ValueError):
        # Invalid date
        openAstro.event("Test", 2000, 2, 30, 12, 0, 0)
    
    with pytest.raises(ValueError):
        # Invalid month
        openAstro.event("Test", 2000, 13, 1, 12, 0, 0)
    
    with pytest.raises(ValueError):
        # Invalid time
        openAstro.event("Test", 2000, 1, 1, 25, 0, 0)

def test_invalid_coordinates():
    """Test handling of invalid coordinates."""
    
    with pytest.raises(ValueError):
        # Invalid latitude
        openAstro.event("Test", 2000, 1, 1, 12, 0, 0, geolat=91.0)
    
    with pytest.raises(ValueError):
        # Invalid longitude  
        openAstro.event("Test", 2000, 1, 1, 12, 0, 0, geolon=181.0)

def test_invalid_chart_types():
    """Test handling of invalid chart types."""
    
    event = openAstro.event("Test", 2000, 1, 1, 12, 0, 0)
    
    with pytest.raises(KeyError):
        openAstro(event, type="InvalidType")
```

## Custom Test Utilities

### Test Data Generators

```python
def generate_test_events(count=10):
    """Generate test events for batch testing."""
    
    import random
    events = []
    
    for i in range(count):
        event = openAstro.event(
            f"Test Person {i}",
            year=random.randint(1900, 2100),
            month=random.randint(1, 12),
            day=random.randint(1, 28),  # Safe day range
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=0,
            timezone=random.randint(-12, 12),
            location=f"Test Location {i}",
            geolat=random.uniform(-90, 90),
            geolon=random.uniform(-180, 180)
        )
        events.append(event)
    
    return events

def assert_chart_validity(chart):
    """Common assertions for chart validity."""
    
    assert chart is not None
    assert hasattr(chart, 'planets_degree_ut')
    assert hasattr(chart, 'planets_sign')
    assert hasattr(chart, 'houses_degree_ut')
    
    # Check planet position ranges
    for pos in chart.planets_degree_ut[:10]:
        assert 0 <= pos < 360
    
    # Check sign ranges
    for sign in chart.planets_sign[:10]:
        assert 0 <= sign <= 11
    
    # Check house cusp ranges
    for cusp in chart.houses_degree_ut[:12]:
        assert 0 <= cusp < 360

def compare_charts(chart1, chart2, tolerance=0.01):
    """Compare two charts for similarity within tolerance."""
    
    # Compare planet positions
    for i in range(min(len(chart1.planets_degree_ut), len(chart2.planets_degree_ut))):
        diff = abs(chart1.planets_degree_ut[i] - chart2.planets_degree_ut[i])
        if diff > 180:
            diff = 360 - diff
        assert diff <= tolerance, f"Planet {i} differs by {diff}°"
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install system dependencies (Ubuntu)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y librsvg2-bin imagemagick
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-regressions
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=openastro2 --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Best Practices

1. **Use fixed test data** - Avoid random inputs for reproducible tests
2. **Test edge cases** - Invalid dates, extreme coordinates, historical ranges
3. **Regression testing** - Ensure calculations remain consistent across versions
4. **Performance monitoring** - Track speed of critical operations
5. **Cross-platform testing** - Test on different operating systems
6. **Documentation testing** - Ensure examples in docs actually work

## Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-regressions

# Run basic tests
pytest tests/test_chart_list.py -v

# Run regression tests
pytest tests/tests_regressions/ -v

# Run with coverage
pytest tests/ --cov=openastro2 --cov-report=html

# Run specific test pattern
pytest -k "test_planet" -v

# Run tests with markers
pytest -m "slow" -v  # If you use test markers
```

This comprehensive testing framework ensures OpenAstro2 maintains accuracy and reliability across different platforms and use cases.