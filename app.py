#!/usr/bin/env python3
"""
Traffic Management System - Production Application Launcher
==========================================================

Enterprise-grade application startup system with comprehensive error handling,
health checks, and deployment validation.
"""

import os
import sys
import subprocess
import signal
import time
import logging
import json
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_config, validate_deployment, AppConfig
except ImportError as e:
    print(f"❌ Failed to import configuration: {e}")
    print("📋 Ensure config.py is in the same directory as this script")
    sys.exit(1)


class HealthChecker:
    """Application health monitoring"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.HealthChecker")
        
    def check_streamlit_health(self) -> tuple[bool, str]:
        """Check if Streamlit is responding"""
        try:
            import requests
            url = f"http://{self.config.host}:{self.config.port}/_stcore/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200, "Streamlit healthy"
        except ImportError:
            return True, "Health check skipped (requests not available)"
        except Exception as e:
            return False, f"Streamlit health check failed: {e}"
    
    def check_app_files(self) -> tuple[bool, str]:
        """Check if required app files exist"""
        main_app = self.config.app_root / self.config.frontend_app
        if not main_app.exists():
            return False, f"Main app missing: {main_app}"
        return True, "App files present"
    
    def check_dependencies(self) -> tuple[bool, str]:
        """Check if required dependencies are available"""
        try:
            import streamlit
            import pandas
            import plotly
            return True, f"Dependencies OK (Streamlit {streamlit.__version__})"
        except ImportError as e:
            return False, f"Missing dependency: {e}"
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        checks = [
            ("App Files", self.check_app_files()),
            ("Dependencies", self.check_dependencies()),
            ("Streamlit Health", self.check_streamlit_health()),
        ]
        
        report = {
            "timestamp": time.time(),
            "status": "healthy",
            "checks": {},
            "config": {
                "environment": self.config.environment.value,
                "port": self.config.port,
                "host": self.config.host,
                "version": self.config.version,
            }
        }
        
        for check_name, (is_healthy, message) in checks:
            report["checks"][check_name] = {
                "healthy": is_healthy,
                "message": message
            }
            if not is_healthy:
                report["status"] = "unhealthy"
        
        return report


class ProcessManager:
    """Manage Streamlit process lifecycle"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ProcessManager")
        self.process: Optional[subprocess.Popen] = None
        self.health_checker = HealthChecker(config)
        
    def start_streamlit(self, app_file: str) -> subprocess.Popen:
        """Start Streamlit with proper error handling"""
        
        # Validate app file exists
        app_path = self.config.app_root / app_file
        if not app_path.exists():
            raise FileNotFoundError(f"App file not found: {app_path}")
        
        # Build command
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            *self.config.get_streamlit_args()
        ]
        
        # Prepare environment
        env = os.environ.copy()
        env.update(self.config.get_environment_vars())
        
        self.logger.info(f"🚀 Starting Streamlit: {' '.join(cmd)}")
        
        try:
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
                cwd=str(self.config.app_root)
            )
            
            # Wait a moment to see if process starts successfully
            time.sleep(2)
            
            if process.poll() is not None:
                # Process exited immediately - capture output
                output, _ = process.communicate()
                raise RuntimeError(f"Streamlit failed to start:\n{output}")
            
            self.process = process
            self.logger.info(f"✅ Streamlit started successfully (PID: {process.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Streamlit: {e}")
            raise
    
    def monitor_process(self):
        """Monitor Streamlit process and handle output"""
        if not self.process:
            return
            
        self.logger.info("📊 Monitoring Streamlit process...")
        
        try:
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    # Log Streamlit output with appropriate level
                    line = output.strip()
                    if "error" in line.lower() or "exception" in line.lower():
                        self.logger.error(f"Streamlit: {line}")
                    elif "warning" in line.lower():
                        self.logger.warning(f"Streamlit: {line}")
                    else:
                        self.logger.info(f"Streamlit: {line}")
                        
        except KeyboardInterrupt:
            self.logger.info("🛑 Received interrupt signal")
            self.stop_process()
        except Exception as e:
            self.logger.error(f"❌ Process monitoring error: {e}")
    
    def stop_process(self):
        """Gracefully stop Streamlit process"""
        if not self.process:
            return
            
        self.logger.info("🛑 Stopping Streamlit process...")
        
        try:
            # Send SIGTERM first
            self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=10)
                self.logger.info("✅ Streamlit stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if not stopped
                self.logger.warning("⚠️ Force killing Streamlit process")
                self.process.kill()
                self.process.wait()
                
        except Exception as e:
            self.logger.error(f"❌ Error stopping process: {e}")
        finally:
            self.process = None


@contextmanager
def signal_handler(process_manager: ProcessManager):
    """Handle system signals gracefully"""
    def handle_signal(signum, frame):
        logging.getLogger(__name__).info(f"🛑 Received signal {signum}")
        process_manager.stop_process()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        yield
    finally:
        # Cleanup
        process_manager.stop_process()


def setup_error_handling():
    """Setup global exception handling"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger = logging.getLogger(__name__)
        logger.critical("❌ Uncaught exception:", 
                       exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception


def determine_app_to_run() -> str:
    """Determine which app to run based on environment and arguments"""
    config = get_config()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        app_arg = sys.argv[1].lower()
        if app_arg in ['demo', 'kerala']:
            return str(config.demo_app)
        elif app_arg in ['dashboard', 'main', 'frontend']:
            return str(config.frontend_app)
    
    # Default based on deployment type
    if config.environment.value in ['render', 'railway']:
        # Cloud deployments typically want the simple demo
        return str(config.demo_app) 
    else:
        # Local/Docker runs the full dashboard
        return str(config.frontend_app)


def print_startup_banner(config: AppConfig, app_file: str):
    """Print application startup banner"""
    print("\n" + "="*60)
    print(f"🚦 {config.app_name} v{config.version}")
    print("="*60)
    print(f"🌍 Environment: {config.environment.value}")
    print(f"📱 Application: {app_file}")
    print(f"🔌 Server: http://{config.host}:{config.port}")
    print(f"🏥 Health: {'enabled' if config.health_check_enabled else 'disabled'}")
    print(f"🔧 Debug: {'enabled' if config.debug else 'disabled'}")
    print("="*60 + "\n")


def main():
    """Main application entry point"""
    
    try:
        # Setup error handling
        setup_error_handling()
        
        # Load configuration
        config = get_config()
        config.log_configuration()
        
        # Validate deployment
        is_valid, errors = validate_deployment()
        if not is_valid:
            logger = logging.getLogger(__name__)
            logger.error("❌ Deployment validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        # Determine app to run
        app_file = determine_app_to_run()
        
        # Print startup banner
        print_startup_banner(config, app_file)
        
        # Create process manager
        process_manager = ProcessManager(config)
        
        # Start application with signal handling
        with signal_handler(process_manager):
            process = process_manager.start_streamlit(app_file)
            
            # Log successful startup
            logger = logging.getLogger(__name__)
            logger.info(f"✅ {config.app_name} started successfully")
            logger.info(f"🌐 Access at: http://{config.host}:{config.port}")
            
            # Monitor process
            process_manager.monitor_process()
            
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.critical(f"❌ Application startup failed: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()