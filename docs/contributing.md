# Contributing to OpenAstro2

We welcome contributions to OpenAstro2! This guide will help you get started with contributing to the project.

## Getting Started

### Development Environment Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
```bash
git clone https://github.com/yourusername/openastro2.git
cd openastro2
```

3. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

4. **Install development dependencies**:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-regressions
pip install black flake8 mypy  # Code formatting and linting
```

5. **Install in development mode**:
```bash
pip install -e .
```

6. **Verify installation**:
```bash
python -c "from openastro2.openastro2 import openAstro; print('Installation successful')"
```

### Development Workflow

1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
3. **Run tests**:
```bash
pytest tests/ -v
```

4. **Format code**:
```bash
black openastro2/
flake8 openastro2/
```

5. **Commit your changes**:
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

6. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

7. **Create a Pull Request** on GitHub

## Types of Contributions

### Bug Fixes

- **Report bugs** using GitHub Issues
- **Provide minimal reproduction** cases
- **Include system information** (OS, Python version, package versions)
- **Fix bugs** with tests to prevent regression

### Feature Additions

- **Discuss large features** in GitHub Issues first
- **Add comprehensive tests** for new features
- **Update documentation** for new functionality
- **Maintain backward compatibility** when possible

### Documentation Improvements

- **Fix typos and errors** in documentation
- **Add examples** for unclear functionality
- **Improve API documentation** with better descriptions
- **Translate documentation** to other languages

### Code Quality Improvements

- **Refactor code** for better readability
- **Optimize performance** with benchmarks
- **Add type hints** for better IDE support
- **Improve error messages** and exception handling

## Code Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Use Black formatter for consistent style
black openastro2/

# Maximum line length: 88 characters (Black default)
# Use double quotes for strings
# Use trailing commas in multi-line structures
```

### Code Organization

```python
# Module structure
"""
Module docstring describing purpose.
"""

# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import numpy as np

# Local imports
from openastromod import swiss
from openastromod.utils import utc_to_local
```

### Documentation Style

```python
def calculate_aspects(planet1_pos, planet2_pos, orb=8):
    """Calculate aspects between two planets.
    
    Args:
        planet1_pos (float): Position of first planet in degrees
        planet2_pos (float): Position of second planet in degrees
        orb (float): Orb tolerance in degrees (default: 8)
    
    Returns:
        dict: Aspect information including type and exactness
        
    Example:
        >>> calculate_aspects(30.0, 120.0, orb=5)
        {'aspect': 'trine', 'orb': 0.0, 'exact': True}
    """
    # Implementation here
    pass
```

### Testing Standards

```python
import pytest
from openastro2.openastro2 import openAstro

def test_feature_name():
    """Test specific functionality with descriptive name."""
    # Arrange
    event = openAstro.event("Test", 2000, 1, 1, 12, 0, 0)
    
    # Act
    chart = openAstro(event, type="Radix")
    
    # Assert
    assert chart is not None
    assert hasattr(chart, 'planets_degree_ut')

def test_edge_case():
    """Test edge cases and error conditions."""
    with pytest.raises(ValueError):
        openAstro.event("Test", 2000, 13, 1, 12, 0, 0)  # Invalid month
```

## Contribution Guidelines

### Before Submitting

- [ ] **Run all tests** and ensure they pass
- [ ] **Add tests** for new functionality
- [ ] **Update documentation** if needed
- [ ] **Check code style** with Black and Flake8
- [ ] **Verify no regressions** in existing functionality

### Pull Request Process

1. **Fill out PR template** completely
2. **Reference related issues** with "Fixes #123"
3. **Provide clear description** of changes
4. **Include screenshots** for UI changes
5. **Request review** from maintainers

### Commit Message Format

```
Type: Short description (50 chars max)

Longer description explaining what and why vs how.
Can include multiple paragraphs.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"
- Reference issues: "Fixes #123"
```

#### Commit Types:
- **Add**: New features or functionality
- **Fix**: Bug fixes
- **Update**: Changes to existing features
- **Remove**: Removing features or code
- **Docs**: Documentation only changes
- **Style**: Code style changes (formatting, etc.)
- **Refactor**: Code changes that neither fix bugs nor add features
- **Test**: Adding or updating tests
- **Chore**: Maintenance tasks

## Specific Contribution Areas

### Adding New Chart Types

1. **Extend chart type enumeration** in main module
2. **Implement calculation logic** in appropriate module
3. **Add configuration support** in settings
4. **Create comprehensive tests**
5. **Document the new chart type**

Example:
```python
# In openastro2.py
def create_custom_chart(self, event1, event2=None):
    """Create custom chart type."""
    # Implementation
    pass

# In tests/
def test_custom_chart_type():
    """Test custom chart type functionality."""
    # Test implementation
    pass
```

### Adding New House Systems

1. **Research house system** calculation method
2. **Implement in Swiss Ephemeris interface**
3. **Add to configuration options**
4. **Test against known results**
5. **Document usage**

### Improving Calculations

1. **Identify calculation accuracy issues**
2. **Research proper astronomical methods**
3. **Implement with regression tests**
4. **Benchmark performance impact**
5. **Document changes**

### Translation and Internationalization

1. **Add new language support** in settings
2. **Translate planet and sign names**
3. **Translate UI labels**
4. **Test with Unicode characters**
5. **Document translation process**

## Testing Your Contributions

### Running Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_chart_list.py -v
pytest tests/tests_regressions/ -v

# Run with coverage
pytest tests/ --cov=openastro2 --cov-report=html

# Run performance tests
pytest tests/ -k "performance" -v
```

### Adding New Tests

```python
# For new features
def test_new_feature():
    """Test the new feature works correctly."""
    # Test implementation

# For bug fixes
def test_bug_fix_issue_123():
    """Test that issue #123 is fixed."""
    # Regression test

# For edge cases
def test_edge_case_extreme_dates():
    """Test handling of extreme historical dates."""
    # Edge case test
```

### Regression Testing

```python
from pytest_regressions.data_regression import DataRegressionFixture

def test_calculation_regression(data_regression: DataRegressionFixture):
    """Ensure calculations remain consistent."""
    # Fixed test data
    event = openAstro.event("Regression", 1990, 6, 15, 12, 0, 0)
    chart = openAstro(event, type="Radix")
    
    # Extract key data
    test_data = {
        'planets': [round(p, 6) for p in chart.planets_degree_ut[:10]],
        'houses': [round(h, 6) for h in chart.houses_degree_ut[:12]]
    }
    
    # Compare with stored baseline
    data_regression.check(test_data)
```

## Documentation Contributions

### API Documentation

- Use **clear, concise descriptions**
- Include **practical examples**
- Document **all parameters and return values**
- Add **usage warnings** where appropriate

### User Guides

- **Step-by-step instructions** for common tasks
- **Complete working examples**
- **Troubleshooting sections**
- **Cross-references** to related documentation

### Code Comments

```python
def complex_calculation(params):
    """Brief description of what this does.
    
    Longer explanation of the algorithm or approach.
    """
    # Explain WHY not just WHAT
    # Reference sources for calculations
    # Clarify non-obvious logic
    pass
```

## Performance Considerations

### Optimization Guidelines

- **Profile before optimizing** - use `cProfile` or `line_profiler`
- **Optimize hot paths** - focus on frequently called code
- **Maintain accuracy** - don't sacrifice precision for speed
- **Add benchmarks** - ensure optimizations actually help

### Memory Usage

- **Avoid unnecessary data copies**
- **Use generators** for large datasets
- **Cache expensive calculations** appropriately
- **Clean up resources** properly

## Release Process

### Version Numbering

We use Semantic Versioning (semver):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Checklist

1. **Update version number** in `setup.py`
2. **Update CHANGELOG** with new features and fixes
3. **Run full test suite** on all platforms
4. **Update documentation** as needed
5. **Create release notes**
6. **Tag release** in Git
7. **Build and upload** to PyPI

## Community Guidelines

### Code of Conduct

- **Be respectful** to all contributors
- **Provide constructive feedback** in reviews
- **Help newcomers** get started
- **Focus on technical merit** in discussions

### Communication

- **Use GitHub Issues** for bug reports and feature requests
- **Use GitHub Discussions** for questions and ideas
- **Be clear and specific** in communications
- **Provide context** for problems and suggestions

### Getting Help

- **Check existing documentation** first
- **Search GitHub Issues** for similar problems
- **Provide minimal reproduction** cases
- **Include relevant system information**

## Recognition

Contributors are recognized in:
- **Git commit history**
- **GitHub contributors list**
- **Release notes** for significant contributions
- **Documentation acknowledgments**

Thank you for contributing to OpenAstro2! Your contributions help make astrological calculations more accessible and accurate for everyone.
