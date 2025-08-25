#!/usr/bin/env python3
"""
Test script to check if SEO routes are registered
"""

import sys
import os
sys.path.append('/app/backend')

from server import app

def check_routes():
    """Check if SEO routes are registered"""
    print("Checking registered routes...")
    
    # Get all routes from the FastAPI app
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods) if route.methods else [],
                'name': getattr(route, 'name', 'unknown')
            })
    
    # Filter for admin routes
    admin_routes = [r for r in routes if '/admin/' in r['path']]
    
    print(f"Total routes: {len(routes)}")
    print(f"Admin routes: {len(admin_routes)}")
    
    # Look for SEO routes specifically
    seo_routes = [r for r in routes if '/admin/seo' in r['path']]
    
    print(f"\nSEO routes found: {len(seo_routes)}")
    for route in seo_routes:
        print(f"  {route['methods']} {route['path']} ({route['name']})")
    
    # Show some admin routes for comparison
    print(f"\nSample admin routes:")
    for route in admin_routes[:10]:
        print(f"  {route['methods']} {route['path']} ({route['name']})")
    
    return len(seo_routes) > 0

if __name__ == "__main__":
    has_seo_routes = check_routes()
    if has_seo_routes:
        print("\n✅ SEO routes are registered!")
    else:
        print("\n❌ SEO routes are NOT registered!")
    
    sys.exit(0 if has_seo_routes else 1)