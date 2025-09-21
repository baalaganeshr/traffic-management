"""
Traffic Management System - Production Configuration
==================================================

Centralized configuration system that handles all deployment environments
(local, Docker, Render, Railway, Vercel, etc.) with proper validation.
"""

import os
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class DeploymentEnvironment(Enum):
    """Supported deployment environments"""
    LOCAL = "local"
    DOCKER = "docker" 
    RENDER = "render"
    RAILWAY = "railway"
    VERCEL = "vercel"
    HEROKU = "heroku"
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"


@dataclass
class AppConfig:
    """Application configuration with validation"""
    
    # Core Settings
    app_name: str = "VIN Traffic Management System"
    version: str = "2.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8501
    
    # Streamlit Settings
    headless: bool = True
    enable_cors: bool = False
    enable_xsrf: bool = False
    gather_stats: bool = False
    base_url_path: str = ""
    
    # Deployment Settings  
    environment: DeploymentEnvironment = DeploymentEnvironment.LOCAL
    is_production: bool = False
    
    # Health Check Settings
    health_check_enabled: bool = True
    health_check_endpoint: str = "/_health"
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Paths
    app_root: Path = Path(__file__).parent
    frontend_app: Path = Path("frontend/app_unified_improved.py")
    demo_app: Path = Path("demo/app_simple_kerala.py")
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
        self._setup_logging()
    
    def _validate_config(self):
        """Validate all configuration values"""
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Invalid port number: {self.port}")
            
        if not self.app_root.exists():
            raise ValueError(f"App root directory not found: {self.app_root}")
            
        # Validate app files exist
        main_app = self.app_root / self.frontend_app
        if not main_app.exists():
            raise ValueError(f"Main app file not found: {main_app}")
    
    def _setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=self.log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.app_root / "app.log") if self.debug else logging.NullHandler()
            ]
        )
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        
        # Detect deployment environment
        environment = cls._detect_environment()
        
        # Port detection with environment-specific logic
        port = cls._detect_port(environment)
        
        # Production flag
        is_production = environment != DeploymentEnvironment.LOCAL
        
        return cls(
            # Core settings
            debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
            
            # Server settings
            host=os.getenv("HOST", "0.0.0.0"),
            port=port,
            
            # Streamlit settings
            headless=os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() in ("true", "1"),
            enable_cors=os.getenv("STREAMLIT_SERVER_ENABLE_CORS", "false").lower() in ("true", "1"),
            enable_xsrf=os.getenv("STREAMLIT_SERVER_ENABLE_XSRF", "false").lower() in ("true", "1"),
            gather_stats=os.getenv("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false").lower() in ("true", "1"),
            base_url_path=os.getenv("STREAMLIT_SERVER_BASE_URL_PATH", ""),
            
            # Deployment settings
            environment=environment,
            is_production=is_production,
            
            # Health check settings
            health_check_enabled=os.getenv("HEALTH_CHECK_ENABLED", "true").lower() in ("true", "1"),
            
            # Logging settings
            log_level=os.getenv("LOG_LEVEL", "INFO" if is_production else "DEBUG"),
        )
    
    @staticmethod
    def _detect_environment() -> DeploymentEnvironment:
        """Auto-detect deployment environment"""
        
        # Check for specific environment indicators
        if os.getenv("RENDER"):
            return DeploymentEnvironment.RENDER
        elif os.getenv("RAILWAY_ENVIRONMENT"):
            return DeploymentEnvironment.RAILWAY
        elif os.getenv("VERCEL"):
            return DeploymentEnvironment.VERCEL
        elif os.getenv("DYNO"):  # Heroku
            return DeploymentEnvironment.HEROKU
        elif os.getenv("WEBSITE_SITE_NAME"):  # Azure App Service
            return DeploymentEnvironment.AZURE
        elif os.getenv("AWS_LAMBDA_FUNCTION_NAME"):  # AWS Lambda
            return DeploymentEnvironment.AWS
        elif os.getenv("GOOGLE_CLOUD_PROJECT"):  # Google Cloud
            return DeploymentEnvironment.GCP
        elif os.getenv("DOCKER_CONTAINER"):
            return DeploymentEnvironment.DOCKER
        else:
            return DeploymentEnvironment.LOCAL
    
    @staticmethod
    def _detect_port(environment: DeploymentEnvironment) -> int:
        """Detect port based on environment with proper fallbacks"""
        
        # Try PORT environment variable first (most cloud platforms use this)
        port_env = os.getenv("PORT")
        if port_env:
            try:
                port = int(port_env)
                if 1 <= port <= 65535:
                    return port
            except (ValueError, TypeError):
                pass
        
        # Environment-specific port detection
        if environment == DeploymentEnvironment.RENDER:
            return int(os.getenv("PORT", "10000"))
        elif environment == DeploymentEnvironment.RAILWAY:
            return int(os.getenv("PORT", "8000"))  
        elif environment == DeploymentEnvironment.HEROKU:
            return int(os.getenv("PORT", "5000"))
        elif environment == DeploymentEnvironment.VERCEL:
            return int(os.getenv("PORT", "3000"))
        else:
            return 8501  # Default Streamlit port for local/Docker
    
    def get_streamlit_args(self) -> list[str]:
        """Get Streamlit command line arguments"""
        args = [
            f"--server.port={self.port}",
            f"--server.address={self.host}",
            f"--server.headless={str(self.headless).lower()}",
            f"--server.enableCORS={str(self.enable_cors).lower()}",
            f"--server.enableXsrfProtection={str(self.enable_xsrf).lower()}",
            f"--browser.gatherUsageStats={str(self.gather_stats).lower()}",
        ]
        
        if self.base_url_path:
            args.append(f"--server.baseUrlPath={self.base_url_path}")
            
        if self.is_production:
            args.extend([
                "--global.developmentMode=false",
                "--logger.level=warning",
            ])
        
        return args
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for subprocess"""
        return {
            "STREAMLIT_SERVER_ADDRESS": self.host,
            "STREAMLIT_SERVER_HEADLESS": str(self.headless).lower(),
            "STREAMLIT_SERVER_ENABLE_CORS": str(self.enable_cors).lower(),
            "STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION": str(self.enable_xsrf).lower(),
            "STREAMLIT_BROWSER_GATHER_USAGE_STATS": str(self.gather_stats).lower(),
        }
    
    def log_configuration(self):
        """Log current configuration (safely, without secrets)"""
        logger = logging.getLogger(__name__)
        logger.info(f"🚦 {self.app_name} v{self.version}")
        logger.info(f"🌍 Environment: {self.environment.value}")
        logger.info(f"🔌 Server: {self.host}:{self.port}")
        logger.info(f"📁 App Root: {self.app_root}")
        logger.info(f"🏥 Health Check: {'enabled' if self.health_check_enabled else 'disabled'}")
        logger.info(f"🔧 Debug Mode: {'enabled' if self.debug else 'disabled'}")
        logger.info(f"🏭 Production: {'yes' if self.is_production else 'no'}")


# Global configuration instance
config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get global configuration instance"""
    global config
    if config is None:
        config = AppConfig.from_environment()
    return config


def validate_deployment() -> tuple[bool, list[str]]:
    """Validate deployment readiness"""
    errors = []
    
    try:
        cfg = get_config()
        
        # Check required files
        main_app = cfg.app_root / cfg.frontend_app
        if not main_app.exists():
            errors.append(f"Main app not found: {main_app}")
            
        demo_app = cfg.app_root / cfg.demo_app  
        if not demo_app.exists():
            errors.append(f"Demo app not found: {demo_app}")
        
        # Check port availability (basic check)
        if not (1 <= cfg.port <= 65535):
            errors.append(f"Invalid port: {cfg.port}")
            
        # Check Streamlit installation
        try:
            import streamlit
            logger = logging.getLogger(__name__)
            logger.info(f"✅ Streamlit {streamlit.__version__} available")
        except ImportError:
            errors.append("Streamlit not installed")
            
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Configuration error: {str(e)}")
        return False, errors


if __name__ == "__main__":
    # Test configuration
    try:
        cfg = get_config()
        cfg.log_configuration()
        
        valid, errors = validate_deployment()
        if valid:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"❌ Configuration failed: {e}")