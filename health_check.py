"""
Traffic Management System - Health Check Service
==============================================

Standalone health check service that can run alongside Streamlit
to provide comprehensive application monitoring and diagnostics.
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_config, HealthChecker
except ImportError:
    print("⚠️ Health check service running in standalone mode")
    
    class MockConfig:
        def __init__(self):
            self.port = 8501
            self.host = "0.0.0.0"
            self.version = "2.0.0"
            self.environment = type('Env', (), {'value': 'unknown'})()
            self.app_root = Path.cwd()
            self.health_check_enabled = True
    
    def get_config():
        return MockConfig()
    
    class HealthChecker:
        def __init__(self, config):
            self.config = config
        
        def get_health_report(self):
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "message": "Standalone health check"
            }


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints"""
    
    def __init__(self, health_checker: HealthChecker, *args, **kwargs):
        self.health_checker = health_checker
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == "/_health" or self.path == "/health":
                self._handle_health_check()
            elif self.path == "/_health/detailed" or self.path == "/health/detailed":
                self._handle_detailed_health_check()
            elif self.path == "/_health/metrics" or self.path == "/metrics":
                self._handle_metrics()
            elif self.path == "/_health/status" or self.path == "/status":
                self._handle_status()
            else:
                self._send_response(404, {"error": "Not found"})
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def _handle_health_check(self):
        """Basic health check - just return 200 OK"""
        self._send_response(200, {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "VIN Traffic Management System"
        })
    
    def _handle_detailed_health_check(self):
        """Detailed health check with full report"""
        try:
            report = self.health_checker.get_health_report()
            status_code = 200 if report["status"] == "healthy" else 503
            self._send_response(status_code, report)
        except Exception as e:
            self._send_response(500, {"status": "error", "message": str(e)})
    
    def _handle_metrics(self):
        """Prometheus-style metrics endpoint"""
        metrics = self._generate_metrics()
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; version=0.0.4; charset=utf-8')
        self.end_headers()
        self.wfile.write(metrics.encode('utf-8'))
    
    def _handle_status(self):
        """Service status endpoint"""
        config = get_config()
        status = {
            "service": "VIN Traffic Management System",
            "version": config.version,
            "environment": config.environment.value,
            "uptime": self._get_uptime(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self._send_response(200, status)
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response"""
        response_data = json.dumps(data, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', str(len(response_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_data.encode('utf-8'))
    
    def _generate_metrics(self) -> str:
        """Generate Prometheus-style metrics"""
        config = get_config()
        uptime = self._get_uptime()
        
        metrics = [
            "# HELP traffic_system_info Information about the traffic system",
            f'traffic_system_info{{version="{config.version}",environment="{config.environment.value}"}} 1',
            "",
            "# HELP traffic_system_uptime_seconds Uptime of the service in seconds",
            f"traffic_system_uptime_seconds {uptime}",
            "",
            "# HELP traffic_system_health Health status (1 = healthy, 0 = unhealthy)",
        ]
        
        try:
            report = self.health_checker.get_health_report()
            health_value = 1 if report["status"] == "healthy" else 0
            metrics.append(f"traffic_system_health {health_value}")
        except Exception:
            metrics.append("traffic_system_health 0")
        
        return "\n".join(metrics)
    
    def _get_uptime(self) -> float:
        """Get service uptime in seconds"""
        if not hasattr(self, '_start_time'):
            self._start_time = time.time()
        return time.time() - self._start_time
    
    def log_message(self, format, *args):
        """Override to use proper logging"""
        logger = logging.getLogger(f"{__name__}.HealthCheck")
        logger.info(f"{self.address_string()} - {format % args}")


class HealthCheckServer:
    """Health check server that runs alongside main application"""
    
    def __init__(self, port: int = 8502, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(f"{__name__}.HealthCheckServer")
        
        # Initialize health checker
        config = get_config()
        self.health_checker = HealthChecker(config)
        
    def start(self):
        """Start health check server in background thread"""
        try:
            # Create handler class with health checker
            def handler_factory(*args, **kwargs):
                return HealthCheckHandler(self.health_checker, *args, **kwargs)
            
            # Create server
            self.server = HTTPServer((self.host, self.port), handler_factory)
            
            # Start server in background thread
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            self.logger.info(f"🏥 Health check server started on http://{self.host}:{self.port}")
            self.logger.info(f"📊 Endpoints available:")
            self.logger.info(f"   - http://{self.host}:{self.port}/_health (basic)")
            self.logger.info(f"   - http://{self.host}:{self.port}/_health/detailed (full report)")
            self.logger.info(f"   - http://{self.host}:{self.port}/_health/metrics (Prometheus)")
            self.logger.info(f"   - http://{self.host}:{self.port}/_health/status (service info)")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start health check server: {e}")
            raise
    
    def stop(self):
        """Stop health check server"""
        if self.server:
            self.logger.info("🛑 Stopping health check server...")
            self.server.shutdown()
            self.server.server_close()
            
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        self.logger.info("✅ Health check server stopped")


def main():
    """Run standalone health check server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VIN Traffic System Health Check Server")
    parser.add_argument("--port", type=int, default=8502, help="Port to run on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Start server
    server = HealthCheckServer(port=args.port, host=args.host)
    
    try:
        server.start()
        print(f"✅ Health check server running on http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.stop()
    except Exception as e:
        print(f"❌ Server error: {e}")
        server.stop()


if __name__ == "__main__":
    main()