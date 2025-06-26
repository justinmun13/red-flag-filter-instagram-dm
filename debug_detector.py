#!/usr/bin/env python3
"""
Debug Red Flag Detector to find the issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_detector_basic():
    """Test basic detector functionality"""
    
    try:
        from red_flag_detector import RedFlagDetector
        print("✅ Successfully imported RedFlagDetector")
        
        detector = RedFlagDetector()
        print("✅ Successfully created detector instance")
        
        # Test with simple messages
        test_messages = [
            "Hello how are you?",
            "I need money urgently",
            "You're perfect, we're soulmates!",
            ""  # Empty message
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🔍 Test {i}: \"{message}\"")
            
            try:
                result = detector.analyze_message(message)
                
                if result is None:
                    print("❌ Result is None")
                elif not isinstance(result, dict):
                    print(f"❌ Result is not dict: {type(result)}")
                elif 'risk_level' not in result:
                    print(f"❌ Result missing risk_level: {result.keys()}")
                else:
                    risk = result['risk_level']
                    risk_str = risk.value if hasattr(risk, 'value') else str(risk)
                    print(f"✅ Risk Level: {risk_str}")
                    print(f"   Red flags: {len(result.get('red_flags', []))}")
                    
            except Exception as e:
                print(f"❌ Error analyzing message: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎉 Basic detector test complete")
        return True
        
    except Exception as e:
        print(f"❌ Error importing or creating detector: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 DEBUGGING RED FLAG DETECTOR")
    print("=" * 40)
    
    success = test_detector_basic()
    
    if success:
        print("\n✅ Detector appears to be working")
        print("The issue might be in the Instagram message processing")
    else:
        print("\n❌ Detector has fundamental issues")
        print("Need to fix the detector before Instagram integration")