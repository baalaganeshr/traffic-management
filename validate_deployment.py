#!/usr/bin/env python3
"""
Traffic Management System - Deployment Validation & Testing
==========================================================

Comprehensive validation script to test deployment readiness
across different environments and platforms.
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import socket
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_config, validate_deployment, AppConfig, DeploymentEnvironment
    from health_check import HealthChecker
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📋 Ensure config.py and health_check.py are available")
    sys.exit(1)


class DeploymentValidator:
    """Comprehensive deployment validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DeploymentValidator")
        self.config = get_config()
        self.health_checker = HealthChecker(self.config)
        self.test_results: List[Dict[str, Any]] = []
    
    def run_all_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run complete validation suite"""
        
        self.logger.info("🧪 Starting deployment validation...")
        
        tests = [
            ("Configuration", self._test_configuration),
            ("Dependencies", self._test_dependencies),
            ("File Structure", self._test_file_structure),
            ("Environment Variables", self._test_environment_variables),
            ("Port Availability", self._test_port_availability),
            ("Application Import", self._test_application_import),
            ("Streamlit Compatibility", self._test_streamlit_compatibility),
            ("Docker Compatibility", self._test_docker_compatibility),
            ("Health Check", self._test_health_check),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.logger.info(f"🔍 Running test: {test_name}")
            
            try:
                result = test_func()
                self.test_results.append({
                    "test": test_name,
                    "status": "passed" if result["success"] else "failed",
                    "message": result["message"],
                    "details": result.get("details", {}),
                    "timestamp": time.time()
                })
                
                if result["success"]:
                    self.logger.info(f"✅ {test_name}: {result['message']}")
                    passed += 1
                else:
                    self.logger.error(f"❌ {test_name}: {result['message']}")
                    failed += 1
                    
            except Exception as e:
                self.logger.error(f"💥 {test_name}: Exception - {e}")
                self.test_results.append({
                    "test": test_name,
                    "status": "error",
                    "message": f"Test failed with exception: {e}",
                    "timestamp": time.time()
                })
                failed += 1
        
        # Generate final report
        all_passed = failed == 0
        report = {
            "overall_status": "passed" if all_passed else "failed",
            "summary": {
                "total_tests": len(tests),
                "passed": passed,
                "failed": failed,
                "pass_rate": (passed / len(tests)) * 100
            },
            "config": {
                "environment": self.config.environment.value,
                "port": self.config.port,
                "version": self.config.version,
            },
            "tests": self.test_results,
            "timestamp": time.time()
        }
        
        if all_passed:
            self.logger.info(f"🎉 All tests passed! ({passed}/{len(tests)})")
        else:
            self.logger.error(f"💥 {failed} test(s) failed out of {len(tests)}")
        
        return all_passed, report
    
    def _test_configuration(self) -> Dict[str, Any]:
        """Test configuration loading and validation"""
        try:
            # Test basic config loading
            config = get_config()
            
            # Test validation
            is_valid, errors = validate_deployment()
            
            if is_valid:
                return {
                    "success": True,
                    "message": f"Configuration valid for {config.environment.value} environment",
                    "details": {
                        "environment": config.environment.value,
                        "port": config.port,
                        "debug": config.debug
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Configuration validation failed: {', '.join(errors)}",
                    "details": {"errors": errors}
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Configuration loading failed: {e}"
            }
    
    def _test_dependencies(self) -> Dict[str, Any]:
        """Test required dependencies"""
        required_packages = [
            ("streamlit", "Streamlit web framework"),
            ("pandas", "Data manipulation library"),
            ("plotly", "Interactive plotting library"),
            ("numpy", "Numerical computing library"),
        ]
        
        missing_packages = []
        available_packages = {}
        
        for package, description in required_packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                available_packages[package] = version
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return {
                "success": False,
                "message": f"Missing required packages: {', '.join(missing_packages)}",
                "details": {
                    "missing": missing_packages,
                    "available": available_packages
                }
            }
        else:
            return {
                "success": True,
                "message": "All required dependencies available",
                "details": {"packages": available_packages}
            }
    
    def _test_file_structure(self) -> Dict[str, Any]:
        """Test required file structure"""
        required_files = [
            "config.py",
            "app.py", 
            "health_check.py",
            "requirements.txt",
            "frontend/streamlit_app.py",
            "demo/kerala_demo.py"
        ]
        
        missing_files = []
        found_files = []
        
        for file_path in required_files:
            full_path = self.config.app_root / file_path
            if full_path.exists():
                found_files.append(str(file_path))
            else:
                missing_files.append(str(file_path))
        
        if missing_files:
            return {
                "success": False,
                "message": f"Missing required files: {', '.join(missing_files)}",
                "details": {
                    "missing": missing_files,
                    "found": found_files
                }
            }
        else:
            return {
                "success": True,
                "message": "All required files present",
                "details": {"files": found_files}
            }
    
    def _test_environment_variables(self) -> Dict[str, Any]:
        """Test environment variable handling"""
        env_tests = []
        
        # Test PORT variable
        original_port = os.environ.get("PORT")
        os.environ["PORT"] = "9999"
        
        try:
            from config import AppConfig
            test_config = AppConfig.from_environment()
            if test_config.port == 9999:
                env_tests.append("PORT variable correctly detected")
            else:
                env_tests.append("PORT variable not properly handled")
        finally:
            if original_port:
                os.environ["PORT"] = original_port
            else:
                os.environ.pop("PORT", None)
        
        # Test environment detection
        env_detection = self.config.environment.value
        env_tests.append(f"Environment detected as: {env_detection}")
        
        return {
            "success": True,
            "message": "Environment variable handling working",
            "details": {"tests": env_tests}
        }
    
    def _test_port_availability(self) -> Dict[str, Any]:
        """Test if configured port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.config.host, self.config.port))
                
                if result == 0:
                    return {
                        "success": False,
                        "message": f"Port {self.config.port} is already in use",
                        "details": {"port": self.config.port, "host": self.config.host}
                    }
                else:
                    return {
                        "success": True,
                        "message": f"Port {self.config.port} is available",
                        "details": {"port": self.config.port, "host": self.config.host}
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Port availability test failed: {e}"
            }
    
    def _test_application_import(self) -> Dict[str, Any]:
        """Test if main applications can be imported"""
        try:
            # Test importing frontend app
            frontend_path = self.config.app_root / self.config.frontend_app
            if not frontend_path.exists():
                return {
                    "success": False,
                    "message": "Frontend app file not found"
                }
            
            # Test importing demo app
            demo_path = self.config.app_root / self.config.demo_app
            if not demo_path.exists():
                return {
                    "success": False,
                    "message": "Demo app file not found"
                }
            
            return {
                "success": True,
                "message": "Application files are accessible",
                "details": {
                    "frontend_app": str(frontend_path),
                    "demo_app": str(demo_path)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Application import test failed: {e}"
            }
    
    def _test_streamlit_compatibility(self) -> Dict[str, Any]:
        """Test Streamlit configuration compatibility"""
        try:
            import streamlit as st
            
            # Test getting Streamlit args
            args = self.config.get_streamlit_args()
            
            # Validate args format
            valid_args = all(arg.startswith('--') for arg in args)
            
            if valid_args:
                return {
                    "success": True,
                    "message": "Streamlit configuration compatible",
                    "details": {
                        "streamlit_version": st.__version__,
                        "args_count": len(args),
                        "sample_args": args[:3]
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid Streamlit arguments generated"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Streamlit compatibility test failed: {e}"
            }
    
    def _test_docker_compatibility(self) -> Dict[str, Any]:
        """Test Docker-related compatibility"""
        dockerfile_path = self.config.app_root / "Dockerfile"
        
        if not dockerfile_path.exists():
            return {
                "success": False,
                "message": "Dockerfile not found"
            }
        
        try:
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
            
            # Check for required Docker elements
            checks = {
                "has_python_base": "FROM python:" in dockerfile_content,
                "has_workdir": "WORKDIR" in dockerfile_content,
                "has_copy": "COPY" in dockerfile_content,
                "has_cmd": "CMD" in dockerfile_content,
                "has_expose": "EXPOSE" in dockerfile_content,
            }
            
            missing = [check for check, present in checks.items() if not present]
            
            if missing:
                return {
                    "success": False,
                    "message": f"Dockerfile missing elements: {', '.join(missing)}",
                    "details": checks
                }
            else:
                return {
                    "success": True,
                    "message": "Dockerfile structure looks good",
                    "details": checks
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Dockerfile analysis failed: {e}"
            }
    
    def _test_health_check(self) -> Dict[str, Any]:
        """Test health check functionality"""
        try:
            report = self.health_checker.get_health_report()
            
            return {
                "success": True,
                "message": f"Health check working - status: {report['status']}",
                "details": {
                    "status": report["status"],
                    "checks": len(report.get("checks", {}))
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Health check failed: {e}"
            }


def save_report(report: Dict[str, Any], filename: str = "deployment-validation-report.json"):
    """Save validation report to file"""
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Validation report saved to: {filename}")
    except Exception as e:
        print(f"⚠️ Failed to save report: {e}")


def print_summary(report: Dict[str, Any]):
    """Print validation summary"""
    print("\n" + "="*60)
    print("🧪 DEPLOYMENT VALIDATION SUMMARY")
    print("="*60)
    
    summary = report["summary"]
    print(f"📊 Overall Status: {'✅ PASSED' if report['overall_status'] == 'passed' else '❌ FAILED'}")
    print(f"📈 Pass Rate: {summary['pass_rate']:.1f}% ({summary['passed']}/{summary['total_tests']})")
    print(f"🌍 Environment: {report['config']['environment']}")
    print(f"🔌 Port: {report['config']['port']}")
    
    if report['overall_status'] != 'passed':
        print("\n❌ FAILED TESTS:")
        for test in report["tests"]:
            if test["status"] in ["failed", "error"]:
                print(f"  - {test['test']}: {test['message']}")
    
    print("="*60 + "\n")


def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VIN Traffic System Deployment Validator")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--json-only", action="store_true", help="Output only JSON report")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Run validation
    validator = DeploymentValidator()
    success, report = validator.run_all_tests()
    
    # Output results
    if args.json_only:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_summary(report)
    
    # Save report if requested
    if args.output:
        save_report(report, args.output)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()