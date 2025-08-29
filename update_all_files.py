#!/usr/bin/env python3
"""
CATALORO - MASS FILE UPDATER
============================
Updates all files to use centralized configuration from /app/directions
"""

import os
import sys
import re
import glob

# Add current directory to path
sys.path.append('/app')
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths

def update_python_files():
    """Update all Python files to use centralized config"""
    
    print("🔄 Updating Python files...")
    
    # Get all Python files
    python_files = glob.glob('/app/**/*.py', recursive=True)
    python_files = [f for f in python_files if '__pycache__' not in f and 'node_modules' not in f]
    
    # Patterns to replace
    replacements = {
        # URLs
        r'http://217\.154\.0\.82': 'get_backend_url()',
        r'https://cataloro-hub\.preview\.emergentagent\.com': 'get_backend_url()',
        r'http://localhost:8001': 'get_backend_url("local")',
        r'http://localhost:3000': 'get_config("FRONTEND_URL_LOCAL")',
        
        # Database
        r'mongodb://127\.0\.0\.1:27017/cataloro': 'get_database_url()',
        r'cataloro_production': 'get_config("DB_NAME")',
        
        # Admin credentials
        r'admin@marketplace\.com': 'get_admin_credentials()[0]',
        r'admin123': 'get_admin_credentials()[1]',
        
        # Paths
        r'/app/backend': 'get_paths()["backend_dir"]',
        r'/app/frontend': 'get_paths()["frontend_dir"]',
        r'/app': 'get_paths()["app_root"]',
    }
    
    updated_files = []
    
    for file_path in python_files:
        # Skip our own config files
        if 'config_loader' in file_path or 'update_all_files' in file_path:
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            # Apply replacements
            for pattern, replacement in replacements.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True
            
            # Add import statement if we made replacements
            if modified and 'from config_loader import' not in content:
                # Add import at the top after other imports
                lines = content.split('\n')
                import_added = False
                
                for i, line in enumerate(lines):
                    if (line.startswith('import ') or line.startswith('from ')) and not import_added:
                        # Find the last import
                        continue
                    elif not line.strip().startswith(('#', 'import', 'from')) and not import_added:
                        # Insert import before first non-import line
                        lines.insert(i, 'from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url')
                        import_added = True
                        break
                
                if not import_added:
                    lines.insert(0, 'from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url')
                
                content = '\n'.join(lines)
            
            # Write back if modified
            if modified:
                with open(file_path, 'w') as f:
                    f.write(content)
                updated_files.append(file_path)
                
        except Exception as e:
            print(f"⚠️ Warning: Could not update {file_path}: {e}")
    
    print(f"✅ Updated {len(updated_files)} Python files")
    for file_path in updated_files[:10]:  # Show first 10
        print(f"   - {file_path}")
    
    if len(updated_files) > 10:
        print(f"   ... and {len(updated_files) - 10} more files")

def update_js_files():
    """Update JavaScript files to use environment variables"""
    
    print("🔄 Updating JavaScript files...")
    
    js_files = glob.glob('/app/frontend/**/*.js', recursive=True)
    js_files += glob.glob('/app/frontend/**/*.jsx', recursive=True)
    js_files = [f for f in js_files if 'node_modules' not in f]
    
    replacements = {
        r'http://217\.154\.0\.82': 'process.env.REACT_APP_BACKEND_URL',
        r'https://cataloro-hub\.preview\.emergentagent\.com': 'process.env.REACT_APP_BACKEND_URL',
        r'http://localhost:8001': 'process.env.REACT_APP_BACKEND_URL || "http://localhost:8001"',
    }
    
    updated_files = []
    
    for file_path in js_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                updated_files.append(file_path)
                
        except Exception as e:
            print(f"⚠️ Warning: Could not update {file_path}: {e}")
    
    print(f"✅ Updated {len(updated_files)} JavaScript files")

def update_config_files():
    """Update configuration files"""
    
    print("🔄 Updating configuration files...")
    
    # Update ecosystem.config.js if it exists
    ecosystem_file = '/app/ecosystem.config.js'
    if os.path.exists(ecosystem_file):
        try:
            with open(ecosystem_file, 'r') as f:
                content = f.read()
            
            # Replace any hardcoded URLs
            content = re.sub(r'http://217\.154\.0\.82', 'https://cataloro-hub.preview.emergentagent.com', content)
            
            with open(ecosystem_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Updated ecosystem.config.js")
        except Exception as e:
            print(f"   ⚠️ Could not update ecosystem.config.js: {e}")

def create_env_sync_script():
    """Create a script to sync .env files with directions"""
    
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open('/app/sync_env.py', 'w') as f:
        f.write(script_content)
    
    os.chmod('/app/sync_env.py', 0o755)
    print("✅ Created sync_env.py script")

if __name__ == "__main__":
    print("🚀 CATALORO - MASS FILE UPDATER")
    print("=" * 40)
    
    # Run updates
    update_python_files()
    print()
    update_js_files() 
    print()
    update_config_files()
    print()
    create_env_sync_script()
    
    print()
    print("🎉 MASS UPDATE COMPLETED!")
    print("=" * 40)
    print("All files have been updated to use centralized configuration.")
    print("Run 'python3 /app/sync_env.py' to sync .env files anytime.")