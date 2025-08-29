#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - CONFIGURATION LOADER
============================================
Centralized configuration loader that reads from /app/directions file
Use this in all Python scripts instead of hardcoded paths and settings
"""

import os
import sys
from typing import Dict, Any

class CataloroConfig:
    """Centralized configuration manager for Cataloro Marketplace"""
    
    def __init__(self, config_file='/app/directions'):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from directions file"""
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line.startswith('#') or not line or '=' not in line:
                        continue
                    
                    # Parse key=value pairs
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Convert boolean strings
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    # Convert integer strings (but not IP addresses)
                    elif value.isdigit():
                        value = int(value)
                    # Convert float strings (but not IP addresses or URLs)
                    elif '.' in value and value.replace('.', '').isdigit() and value.count('.') == 1:
                        value = float(value)
                    
                    self.config[key] = value
                    
        except FileNotFoundError:
            print(f"❌ Configuration file {self.config_file} not found!")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            sys.exit(1)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config.get(key, default)
    
    def get_database_url(self) -> str:
        """Get complete database connection URL"""
        return self.get('MONGO_URL', 'mongodb://127.0.0.1:27017/cataloro')
    
    def get_backend_url(self, mode='production') -> str:
        """Get backend URL based on deployment mode"""
        if mode == 'production':
            return self.get('BACKEND_URL_PRODUCTION', 'http://217.154.0.82')
        else:
            return self.get('BACKEND_URL_LOCAL', 'http://localhost:8001')
    
    def get_admin_credentials(self) -> tuple:
        """Get admin email and password"""
        return (
            self.get('ADMIN_EMAIL', 'admin@marketplace.com'),
            self.get('ADMIN_PASSWORD', 'admin123')
        )
    
    def get_paths(self) -> Dict[str, str]:
        """Get all important paths"""
        return {
            'app_root': self.get('APP_ROOT', '/app'),
            'backend_dir': self.get('BACKEND_DIR', '/app/backend'),
            'frontend_dir': self.get('FRONTEND_DIR', '/app/frontend'),
            'uploads_dir': self.get('UPLOADS_DIR', '/app/backend/uploads'),
        }
    
    def get_cors_origins(self) -> list:
        """Get CORS origins as a list"""
        origins = self.get('CORS_ORIGINS', '')
        return [origin.strip() for origin in origins.split(',') if origin.strip()]
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.get('DEPLOYMENT_MODE', 'production') == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.get('DEPLOYMENT_MODE', 'production') == 'production'
    
    def print_config(self):
        """Print all configuration for debugging"""
        print("=== CATALORO CONFIGURATION ===")
        for key, value in sorted(self.config.items()):
            if 'PASSWORD' in key or 'SECRET' in key:
                print(f"{key}=***HIDDEN***")
            else:
                print(f"{key}={value}")
        print("==============================")

# Global configuration instance
config = CataloroConfig()

# Convenience functions for common operations
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key, default)

def get_backend_url(mode='production') -> str:
    """Get backend URL"""
    return config.get_backend_url(mode)

def get_database_url() -> str:
    """Get database URL"""
    return config.get_database_url()

def get_admin_credentials() -> tuple:
    """Get admin credentials"""
    return config.get_admin_credentials()

def get_paths() -> Dict[str, str]:
    """Get system paths"""
    return config.get_paths()

def is_development() -> bool:
    """Check if development mode"""
    return config.is_development()

def is_production() -> bool:
    """Check if production mode"""
    return config.is_production()

# CLI interface for debugging
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'print':
            config.print_config()
        elif sys.argv[1] == 'get':
            if len(sys.argv) > 2:
                key = sys.argv[2]
                value = config.get(key)
                print(f"{key}={value}")
            else:
                print("Usage: python3 config_loader.py get <KEY>")
        elif sys.argv[1] == 'test':
            print("Testing configuration loader...")
            paths = get_paths()
            print(f"App Root: {paths['app_root']}")
            print(f"Backend URL: {get_backend_url()}")
            print(f"Database URL: {get_database_url()}")
            admin_email, admin_pass = get_admin_credentials()
            print(f"Admin Email: {admin_email}")
            print(f"Is Production: {is_production()}")
        else:
            print("Available commands: print, get <key>, test")
    else:
        print("Cataloro Configuration Loader")
        print("Usage: python3 config_loader.py [print|get|test]")