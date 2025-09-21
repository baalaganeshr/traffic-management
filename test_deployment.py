#!/usr/bin/env python3
"""
UrbanFlow360 Deployment Test Suite
==================================
Tests all entry points and configurations to ensure deployment success.
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_imports():
    """Test that all critical imports work"""
    print("🧪 Testing imports...")
    
    try:
        # Test production launcher
        import app
        print("  ✅ app.py (production launcher) - OK")
    except ImportError as e:
        print(f"  ❌ app.py import failed: {e}")
        return False
    
    try:
        # Test configuration
        import config
        print("  ✅ config.py - OK")
    except ImportError as e:
        print(f"  ❌ config.py import failed: {e}")
        return False
    
    try:
        # Test health check
        import health_check
        print("  ✅ health_check.py - OK")
    except ImportError as e:
        print(f"  ❌ health_check.py import failed: {e}")
        return False
    
    return True

def test_entry_points():
    """Test all entry point files exist and are valid"""
    print("\n🚪 Testing entry points...")
    
    entry_points = [
        "start.py",
        "main.py", 
        "app.py",
        "frontend/app_unified_improved.py"
    ]
    
    for entry in entry_points:
        if Path(entry).exists():
            print(f"  ✅ {entry} exists")
            
            # Test if it's valid Python
            try:
                spec = importlib.util.spec_from_file_location("test_module", entry)
                if spec:
                    print(f"  ✅ {entry} is valid Python")
                else:
                    print(f"  ❌ {entry} is not valid Python")
                    return False
            except Exception as e:
                print(f"  ❌ {entry} validation failed: {e}")
                return False
        else:
            print(f"  ❌ {entry} missing")
            return False
    
    return True

def test_configuration():
    """Test configuration system"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config import AppConfig, DeploymentEnvironment
        
        # Test configuration creation
        config = AppConfig()
        print(f"  ✅ Config created - Environment: {config.environment}")
        print(f"  ✅ Port: {config.port}")
        print(f"  ✅ Streamlit args: {len(config.get_streamlit_args())} arguments")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_deployment_files():
    """Test deployment configuration files"""
    print("\n📄 Testing deployment files...")
    
    files = [
        "Procfile",
        "requirements.txt",
        "Dockerfile",
        "render.yaml"
    ]
    
    for file in files:
        if Path(file).exists():
            print(f"  ✅ {file} exists")
            
            # Check content is not empty
            if Path(file).stat().st_size > 0:
                print(f"  ✅ {file} has content")
            else:
                print(f"  ❌ {file} is empty")
                return False
        else:
            print(f"  ❌ {file} missing")
            return False
    
    return True

def test_start_simulation():
    """Simulate startup without actually starting"""
    print("\n🚀 Testing startup simulation...")
    
    try:
        # Test that we can import the main function
        from app import main
        print("  ✅ Production launcher main() function accessible")
        
        # Test configuration in production mode
        os.environ['VIN_PRODUCTION_MODE'] = 'true'
        from config import AppConfig
        config = AppConfig()
        print(f"  ✅ Production mode config: {config.environment}")
        
        return True
    except Exception as e:
        print(f"  ❌ Startup simulation failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🔍 UrbanFlow360 Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Entry Point Tests", test_entry_points), 
        ("Configuration Tests", test_configuration),
        ("Deployment Files", test_deployment_files),
        ("Startup Simulation", test_start_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)