#!/usr/bin/env python3
"""
SYNC .env FILES WITH CENTRALIZED CONFIGURATION
=============================================
Run this script to sync all .env files with /app/directions
"""

import sys
sys.path.append('/app')
from config_loader import get_config, get_backend_url, get_paths

def sync_env_files():
    """Sync .env files with centralized configuration"""
    
    # Sync frontend .env
    paths = get_paths()
    frontend_env = f'{paths["frontend_dir"]}/.env'
    frontend_content = f"""# CATALORO FRONTEND ENVIRONMENT - READS FROM /app/directions  
# DO NOT MODIFY - Configuration managed centrally in /app/directions
REACT_APP_BACKEND_URL={get_backend_url()}
REACT_APP_SITE_NAME={get_config('APP_NAME')}
REACT_APP_VERSION={get_config('APP_VERSION')}"""
    
    with open(frontend_env, 'w') as f:
        f.write(frontend_content)
    
    # Sync backend .env  
    backend_env = f'{paths["backend_dir"]}/.env'
    backend_content = f"""# CATALORO BACKEND ENVIRONMENT - READS FROM /app/directions
# DO NOT MODIFY - Configuration managed centrally in /app/directions
MONGO_URL={get_config('MONGO_URL')}
DB_NAME={get_config('DB_NAME')}
JWT_SECRET={get_config('JWT_SECRET')}
CORS_ORIGINS={get_config('ACTIVE_CORS_ORIGINS')}
ENVIRONMENT={get_config('ENVIRONMENT')}
BACKEND_BASE_URL={get_backend_url()}"""
    
    with open(backend_env, 'w') as f:
        f.write(backend_content)
    
    print("✅ Synced .env files with centralized configuration")

if __name__ == "__main__":
    sync_env_files()
