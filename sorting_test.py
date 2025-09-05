#!/usr/bin/env python3
"""
Backend Test Suite for Cataloro Marketplace - Newest First Sorting Verification
Testing the "newest first" sorting functionality fixes
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://market-refactor.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}🧪 {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def test_browse_endpoint_sorting():
    """Test 1: Verify browse endpoint returns listings with created_at field and proper sorting"""
    print_test_header("Browse Endpoint Sorting Verification")
    
    try:
        # Get all listings from browse endpoint
        response = requests.get(f"{API_BASE}/marketplace/browse")
        
        if response.status_code != 200:
            print_error(f"Browse endpoint failed with status {response.status_code}")
            return False
        
        listings = response.json()
        
        if not listings:
            print_warning("No listings found in browse endpoint")
            return True
        
        print_info(f"Found {len(listings)} listings")
        
        # Test 1.1: Verify all listings have created_at field
        missing_created_at = []
        for i, listing in enumerate(listings):
            if 'created_at' not in listing:
                missing_created_at.append(f"Listing {i+1} (ID: {listing.get('id', 'unknown')})")
        
        if missing_created_at:
            print_error(f"Listings missing created_at field: {', '.join(missing_created_at)}")
            return False
        else:
            print_success("All listings have created_at field")
        
        # Test 1.2: Verify created_at field format and validity
        invalid_dates = []
        valid_dates = []
        for i, listing in enumerate(listings):
            try:
                created_at = listing['created_at']
                # Try to parse the date
                parsed_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                valid_dates.append((i, listing.get('id'), parsed_date, created_at))
            except (ValueError, TypeError) as e:
                invalid_dates.append(f"Listing {i+1}: {created_at} - {str(e)}")
        
        if invalid_dates:
            print_error(f"Invalid created_at dates found: {', '.join(invalid_dates)}")
            return False
        else:
            print_success(f"All {len(valid_dates)} listings have valid created_at dates")
        
        # Test 1.3: Check if listings are in newest-first order (descending chronological)
        if len(valid_dates) > 1:
            is_sorted_newest_first = True
            sorting_issues = []
            
            for i in range(len(valid_dates) - 1):
                current_date = valid_dates[i][2]
                next_date = valid_dates[i + 1][2]
                
                if current_date < next_date:
                    is_sorted_newest_first = False
                    sorting_issues.append(f"Position {i+1} ({current_date}) is older than position {i+2} ({next_date})")
            
            if is_sorted_newest_first:
                print_success("Listings are correctly sorted newest first (descending chronological order)")
                # Show first few listings as example
                print_info("First 3 listings chronological order:")
                for i, (idx, listing_id, date, date_str) in enumerate(valid_dates[:3]):
                    print(f"  {i+1}. {date.strftime('%Y-%m-%d %H:%M:%S')} (ID: {listing_id})")
            else:
                print_error("Listings are NOT sorted newest first")
                for issue in sorting_issues:
                    print_error(f"  {issue}")
                return False
        else:
            print_info("Only one listing found, cannot verify sorting order")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Network error accessing browse endpoint: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error in browse endpoint test: {str(e)}")
        return False

def test_field_name_consistency():
    """Test 2: Verify field name consistency across all listings"""
    print_test_header("Field Name Consistency Verification")
    
    try:
        response = requests.get(f"{API_BASE}/marketplace/browse")
        
        if response.status_code != 200:
            print_error(f"Browse endpoint failed with status {response.status_code}")
            return False
        
        listings = response.json()
        
        if not listings:
            print_warning("No listings found for field consistency test")
            return True
        
        # Check for both created_at and createdAt fields
        created_at_count = 0
        createdAt_count = 0
        both_fields_count = 0
        neither_field_count = 0
        
        for listing in listings:
            has_created_at = 'created_at' in listing
            has_createdAt = 'createdAt' in listing
            
            if has_created_at and has_createdAt:
                both_fields_count += 1
            elif has_created_at:
                created_at_count += 1
            elif has_createdAt:
                createdAt_count += 1
            else:
                neither_field_count += 1
        
        print_info(f"Field analysis results:")
        print_info(f"  Listings with 'created_at': {created_at_count}")
        print_info(f"  Listings with 'createdAt': {createdAt_count}")
        print_info(f"  Listings with both fields: {both_fields_count}")
        print_info(f"  Listings with neither field: {neither_field_count}")
        
        # Verify all listings use created_at (the correct field name)
        if created_at_count + both_fields_count == len(listings):
            print_success("All listings have the correct 'created_at' field name")
        else:
            print_error(f"Some listings missing 'created_at' field: {neither_field_count + createdAt_count} listings")
            return False
        
        # Warn if old createdAt field still exists
        if createdAt_count > 0 or both_fields_count > 0:
            print_warning(f"Found {createdAt_count + both_fields_count} listings with old 'createdAt' field")
            print_info("This is acceptable as the frontend has fallback logic")
        
        return True
        
    except Exception as e:
        print_error(f"Error in field consistency test: {str(e)}")
        return False

def test_sorting_order_verification():
    """Test 3: Detailed sorting order verification with timestamps"""
    print_test_header("Detailed Sorting Order Verification")
    
    try:
        response = requests.get(f"{API_BASE}/marketplace/browse")
        
        if response.status_code != 200:
            print_error(f"Browse endpoint failed with status {response.status_code}")
            return False
        
        listings = response.json()
        
        if len(listings) < 2:
            print_warning("Need at least 2 listings to verify sorting order")
            return True
        
        # Extract and sort dates
        listing_dates = []
        for i, listing in enumerate(listings):
            if 'created_at' in listing:
                try:
                    date = datetime.fromisoformat(listing['created_at'].replace('Z', '+00:00'))
                    listing_dates.append({
                        'index': i,
                        'id': listing.get('id', 'unknown'),
                        'title': listing.get('title', 'Unknown'),
                        'date': date,
                        'date_str': listing['created_at']
                    })
                except Exception as e:
                    print_error(f"Failed to parse date for listing {i}: {e}")
                    return False
        
        if len(listing_dates) < 2:
            print_warning("Not enough valid dates to verify sorting")
            return True
        
        # Check if sorted newest first (descending)
        is_correctly_sorted = True
        for i in range(len(listing_dates) - 1):
            current = listing_dates[i]
            next_item = listing_dates[i + 1]
            
            if current['date'] < next_item['date']:
                is_correctly_sorted = False
                print_error(f"Sorting error at position {i+1}-{i+2}:")
                print_error(f"  Position {i+1}: {current['date']} (ID: {current['id']})")
                print_error(f"  Position {i+2}: {next_item['date']} (ID: {next_item['id']})")
                print_error(f"  Newer item appears after older item!")
        
        if is_correctly_sorted:
            print_success("All listings are correctly sorted in descending chronological order (newest first)")
            
            # Show detailed chronological order
            print_info("Chronological order verification:")
            for i, item in enumerate(listing_dates[:5]):  # Show first 5
                print(f"  {i+1}. {item['date'].strftime('%Y-%m-%d %H:%M:%S')} - {item['title'][:30]}...")
            
            if len(listing_dates) > 5:
                print_info(f"  ... and {len(listing_dates) - 5} more listings")
            
            # Calculate time differences to show sorting is working
            if len(listing_dates) >= 2:
                newest = listing_dates[0]['date']
                oldest = listing_dates[-1]['date']
                time_span = newest - oldest
                print_info(f"Time span: {time_span.days} days, {time_span.seconds // 3600} hours")
        
        return is_correctly_sorted
        
    except Exception as e:
        print_error(f"Error in sorting verification test: {str(e)}")
        return False

def test_api_response_structure():
    """Test 4: Verify API response structure supports frontend sorting"""
    print_test_header("API Response Structure Verification")
    
    try:
        response = requests.get(f"{API_BASE}/marketplace/browse")
        
        if response.status_code != 200:
            print_error(f"Browse endpoint failed with status {response.status_code}")
            return False
        
        listings = response.json()
        
        if not listings:
            print_warning("No listings found for structure verification")
            return True
        
        # Check first listing structure
        first_listing = listings[0]
        required_fields = ['id', 'title', 'price', 'created_at']
        optional_fields = ['seller', 'bid_info', 'time_info']
        
        missing_required = []
        for field in required_fields:
            if field not in first_listing:
                missing_required.append(field)
        
        if missing_required:
            print_error(f"Missing required fields: {', '.join(missing_required)}")
            return False
        else:
            print_success("All required fields present in API response")
        
        # Check optional fields
        present_optional = []
        for field in optional_fields:
            if field in first_listing:
                present_optional.append(field)
        
        if present_optional:
            print_success(f"Optional fields present: {', '.join(present_optional)}")
        
        # Verify created_at format is ISO compatible
        try:
            created_at = first_listing['created_at']
            parsed = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            print_success(f"created_at field format is valid ISO: {created_at}")
        except Exception as e:
            print_error(f"created_at field format invalid: {e}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error in API structure test: {str(e)}")
        return False

def run_all_tests():
    """Run all sorting-related tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 CATALORO MARKETPLACE - NEWEST FIRST SORTING VERIFICATION{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Testing backend API sorting functionality after frontend fixes{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Backend URL: {BACKEND_URL}{Colors.END}")
    
    tests = [
        ("Browse Endpoint Sorting", test_browse_endpoint_sorting),
        ("Field Name Consistency", test_field_name_consistency),
        ("Sorting Order Verification", test_sorting_order_verification),
        ("API Response Structure", test_api_response_structure),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}📊 TEST SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.END}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed += 1
        else:
            print_error(f"{test_name}: FAILED")
            failed += 1
    
    print(f"\n{Colors.BOLD}Total Tests: {len(results)}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}Failed: {failed}{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Newest first sorting is working correctly.{Colors.END}")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED! Sorting issues detected.{Colors.END}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)