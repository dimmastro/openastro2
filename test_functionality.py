#!/usr/bin/env python3
"""
Quick test script to verify OpenAstro2 functionality
"""

from typing import Any
from openastro2.openastro2 import openAstro

def test_basic_functionality() -> bool:
    """Test basic chart creation and data access"""
    print("Testing OpenAstro2 basic functionality...")
    
    try:
        # Create a test event
        event = openAstro.event(
            name="Test Person",
            year=2000, month=1, day=1,
            hour=12, minute=0, second=0,
            timezone=0,
            location="London",
            geolat=51.5074, geolon=-0.1278
        )
        print("✓ Event created successfully")
        
        # Create a natal chart
        chart = openAstro(event, type="Radix")
        print("✓ Chart created successfully")
        
        # Check chart attributes
        print(f"Chart type: {type(chart)}")
        print(f"Available attributes: {[attr for attr in dir(chart) if not attr.startswith('_')][:10]}...")
        
        # Try to access planet data
        if hasattr(chart, 'planets_degree_ut'):
            print(f"✓ Sun position: {chart.planets_degree_ut[0]:.2f}°")
        elif hasattr(chart, 'planets_degree'):
            print(f"✓ Sun position: {chart.planets_degree[0]:.2f}°")
        else:
            print("? Planet data attribute not found in expected format")
        
        # Try to generate SVG
        svg = chart.makeSVG2()
        print(f"✓ SVG generated successfully ({len(svg)} characters)")
        
        # Test different chart type
        transit_chart = openAstro(event, type="Transit")
        print("✓ Transit chart created successfully")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic_functionality()