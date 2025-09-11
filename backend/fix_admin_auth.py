#!/usr/bin/env python3
"""
Script to systematically fix admin endpoint authentication in server.py
"""

import re

def fix_admin_endpoints():
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    # Pattern to match admin endpoints without authentication
    pattern = r'(@app\.(get|post|put|delete)\("/api/admin/[^"]*"\))\s*\n(\s*)async def ([^(]+)\(([^:)]*)\):'
    
    def replace_endpoint(match):
        decorator = match.group(1)
        method = match.group(2)
        spaces = match.group(3)
        func_name = match.group(4)
        params = match.group(5)
        
        # Skip if already has authentication
        if 'current_user: dict = Depends(require_admin_role)' in params:
            return match.group(0)
        
        # Add authentication parameter
        if params.strip():
            # Has other parameters, add auth as first param
            new_params = f'current_user: dict = Depends(require_admin_role), {params}'
        else:
            # No parameters, just add auth
            new_params = 'current_user: dict = Depends(require_admin_role)'
        
        return f'{decorator}\n{spaces}async def {func_name}({new_params}):'
    
    # Apply the replacements
    fixed_content = re.sub(pattern, replace_endpoint, content, flags=re.MULTILINE)
    
    # Write back the fixed content
    with open('/app/backend/server.py', 'w') as f:
        f.write(fixed_content)
    
    print("Admin endpoint authentication fixes applied!")

if __name__ == '__main__':
    fix_admin_endpoints()