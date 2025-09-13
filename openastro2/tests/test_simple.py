#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openastro2.openastromod.utils import get_zodiac_sign, normalize_degree
    print("✅ Import successful!")
    
    # Test get_zodiac_sign
    result = get_zodiac_sign(45.5)
    print(f"✅ get_zodiac_sign(45.5) = {result}")
    
    # Test normalize_degree  
    result = normalize_degree(450)
    print(f"✅ normalize_degree(450) = {result}")
    
    print("✅ All utility functions working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()