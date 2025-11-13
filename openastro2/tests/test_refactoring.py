#!/usr/bin/env python3
"""Test the refactored code with utility functions."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_utility_functions():
    """Test the utility functions work correctly."""
    from openastro2.openastromod.utils import get_zodiac_sign, normalize_degree
    
    print("Testing utility functions...")
    
    # Test get_zodiac_sign function
    test_cases = [
        (0, (0, 0)),      # Aries 0°
        (30, (1, 0)),     # Taurus 0°
        (45, (1, 15)),    # Taurus 15°
        (90, (3, 0)),     # Cancer 0°
        (180, (6, 0)),    # Libra 0°
        (270, (9, 0)),    # Capricorn 0°
        (360, (0, 0)),    # Aries 0° (normalized)
        (375, (0, 15)),   # Aries 15° (375° - 360° = 15° Aries)
        (29.99, (0, 29.99)), # Aries 29.99°
        (359.99, (11, 29.99)), # Pisces 29.99°
    ]
    
    for degree, expected in test_cases:
        result = get_zodiac_sign(degree)
        print(f"  get_zodiac_sign({degree}) = {result}, expected {expected}")
        # Check zodiac sign index
        assert result[0] == expected[0], f"Failed zodiac sign for {degree}: got {result[0]}, expected {expected[0]}"
        # Check degree within sign with tolerance for floating point precision
        assert abs(result[1] - expected[1]) < 1e-10, f"Failed degree within sign for {degree}: got {result[1]}, expected {expected[1]}"
    
    # Test normalize_degree function
    normalize_cases = [
        (0, 0),
        (180, 180),
        (360, 0),
        (450, 90),
        (-90, 270),
        (-360, 0),
    ]
    
    for degree, expected in normalize_cases:
        result = normalize_degree(degree)
        print(f"  normalize_degree({degree}) = {result}, expected {expected}")
        assert result == expected, f"Failed for {degree}: got {result}, expected {expected}"
    
    print("✓ All utility function tests passed!")


def test_openastro_integration():
    """Test that OpenAstro classes work with the refactored code."""
    from openastro2.openastro2 import openAstro
    
    print("\nTesting OpenAstro integration...")
    
    # Create a simple chart using the correct API
    event = openAstro.event('Test', 1990, 6, 15, 12, 0, 0, 0, 0, 0, 0, 0)
    astro = openAstro(event, type="Radix")
    astro.calcAstro()
    
    print(f"  Chart created successfully")
    print(f"  Sun position: {astro.planets_name[0]} at {astro.planets_degree[0]:.2f}° {astro.zodiac[astro.planets_sign[0]]}")
    print(f"  Moon position: {astro.planets_name[1]} at {astro.planets_degree[1]:.2f}° {astro.zodiac[astro.planets_sign[1]]}")
    
    # Check that zodiac signs are valid (0-11)
    for i in range(len(astro.planets_sign)):
        if astro.planets_sign[i] is not None:
            assert 0 <= astro.planets_sign[i] <= 11, f"Invalid zodiac sign for planet {i}: {astro.planets_sign[i]}"
    
    print("✓ OpenAstro integration test passed!")


if __name__ == "__main__":
    try:
        test_utility_functions()
        test_openastro_integration()
        print("\n🎉 All tests passed! The refactoring was successful.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)