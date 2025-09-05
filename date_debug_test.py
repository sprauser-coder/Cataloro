#!/usr/bin/env python3
"""
Date Display Issue Debug Testing
Examining the actual listing data structure to identify date fields
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"

class DateDebugTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
        
    def test_browse_endpoint_basic(self):
        """Test 1: Browse Endpoint Basic Functionality"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Browse Endpoint Basic Functionality",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return None
                
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                self.log_test(
                    "Browse Endpoint Basic Functionality",
                    True,
                    f"Successfully retrieved {len(data)} listings"
                )
                return data
            else:
                self.log_test(
                    "Browse Endpoint Basic Functionality",
                    False,
                    f"No listings found or invalid response format",
                    "List of listings",
                    f"Type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Browse Endpoint Basic Functionality",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def analyze_listing_date_fields(self, listings):
        """Test 2: Analyze Listing Date Fields"""
        try:
            if not listings or len(listings) == 0:
                self.log_test(
                    "Analyze Listing Date Fields",
                    False,
                    "No listings available for analysis"
                )
                return False
            
            print("=" * 60)
            print("DETAILED LISTING DATE FIELD ANALYSIS")
            print("=" * 60)
            
            # Analyze first 5 listings for date fields
            sample_size = min(5, len(listings))
            date_field_summary = {}
            
            for i, listing in enumerate(listings[:sample_size]):
                print(f"\n--- LISTING {i+1} ---")
                print(f"ID: {listing.get('id', 'N/A')}")
                print(f"Title: {listing.get('title', 'N/A')}")
                
                # Look for all possible date-related fields
                potential_date_fields = [
                    'created_at', 'createdAt', 'date', 'timestamp', 'created', 
                    'updated_at', 'updatedAt', 'modified_at', 'modifiedAt',
                    'published_at', 'publishedAt', 'listed_at', 'listedAt'
                ]
                
                found_date_fields = {}
                
                # Check all fields in the listing
                for field_name, field_value in listing.items():
                    # Check if field name suggests it's a date
                    if any(date_term in field_name.lower() for date_term in ['date', 'time', 'created', 'updated', 'modified', 'published', 'listed']):
                        found_date_fields[field_name] = field_value
                        
                        # Track field occurrence across listings
                        if field_name not in date_field_summary:
                            date_field_summary[field_name] = 0
                        date_field_summary[field_name] += 1
                
                if found_date_fields:
                    print("Date-related fields found:")
                    for field_name, field_value in found_date_fields.items():
                        print(f"  {field_name}: {field_value} (Type: {type(field_value).__name__})")
                else:
                    print("No date-related fields found")
                
                # Also check all fields to see complete structure
                print("All available fields:")
                for field_name in sorted(listing.keys()):
                    field_value = listing[field_name]
                    field_type = type(field_value).__name__
                    
                    # Truncate long values for display
                    if isinstance(field_value, str) and len(field_value) > 50:
                        display_value = field_value[:47] + "..."
                    elif isinstance(field_value, (dict, list)):
                        display_value = f"{field_type} with {len(field_value)} items"
                    else:
                        display_value = str(field_value)
                    
                    print(f"  {field_name}: {display_value} ({field_type})")
            
            print("\n" + "=" * 60)
            print("DATE FIELD SUMMARY ACROSS ALL ANALYZED LISTINGS")
            print("=" * 60)
            
            if date_field_summary:
                for field_name, count in sorted(date_field_summary.items()):
                    print(f"{field_name}: Found in {count}/{sample_size} listings")
                
                # Identify the most common date field
                most_common_field = max(date_field_summary.items(), key=lambda x: x[1])
                
                self.log_test(
                    "Analyze Listing Date Fields",
                    True,
                    f"Found {len(date_field_summary)} date-related fields. Most common: '{most_common_field[0]}' (in {most_common_field[1]}/{sample_size} listings)"
                )
                
                return {
                    "date_fields": date_field_summary,
                    "most_common": most_common_field[0],
                    "sample_size": sample_size
                }
            else:
                self.log_test(
                    "Analyze Listing Date Fields",
                    False,
                    f"No date-related fields found in any of the {sample_size} analyzed listings"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Analyze Listing Date Fields",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def verify_date_formats(self, listings, date_analysis):
        """Test 3: Verify Date Formats"""
        try:
            if not date_analysis or not listings:
                self.log_test(
                    "Verify Date Formats",
                    False,
                    "No date analysis data available"
                )
                return False
            
            print("=" * 60)
            print("DATE FORMAT VERIFICATION")
            print("=" * 60)
            
            most_common_field = date_analysis["most_common"]
            sample_size = min(5, len(listings))
            
            print(f"Analyzing '{most_common_field}' field format across {sample_size} listings:")
            
            format_analysis = {
                "iso_format": 0,
                "timestamp": 0,
                "other_string": 0,
                "null_values": 0,
                "invalid": 0
            }
            
            sample_values = []
            
            for i, listing in enumerate(listings[:sample_size]):
                field_value = listing.get(most_common_field)
                sample_values.append(field_value)
                
                print(f"Listing {i+1}: {field_value}")
                
                if field_value is None:
                    format_analysis["null_values"] += 1
                elif isinstance(field_value, str):
                    # Check if it's ISO format
                    try:
                        datetime.fromisoformat(field_value.replace('Z', '+00:00'))
                        format_analysis["iso_format"] += 1
                        print(f"  → ISO format detected")
                    except:
                        # Check if it's a timestamp string
                        try:
                            float(field_value)
                            format_analysis["timestamp"] += 1
                            print(f"  → Timestamp format detected")
                        except:
                            format_analysis["other_string"] += 1
                            print(f"  → Other string format")
                elif isinstance(field_value, (int, float)):
                    format_analysis["timestamp"] += 1
                    print(f"  → Numeric timestamp")
                else:
                    format_analysis["invalid"] += 1
                    print(f"  → Invalid format (type: {type(field_value).__name__})")
            
            print(f"\nFormat Analysis Summary:")
            for format_type, count in format_analysis.items():
                if count > 0:
                    print(f"  {format_type}: {count}/{sample_size} listings")
            
            # Determine the primary format
            primary_format = max(format_analysis.items(), key=lambda x: x[1])
            
            if primary_format[1] > 0:
                self.log_test(
                    "Verify Date Formats",
                    True,
                    f"Primary date format: {primary_format[0]} (found in {primary_format[1]}/{sample_size} listings)"
                )
                
                return {
                    "field_name": most_common_field,
                    "primary_format": primary_format[0],
                    "sample_values": sample_values,
                    "format_analysis": format_analysis
                }
            else:
                self.log_test(
                    "Verify Date Formats",
                    False,
                    "No valid date formats detected"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify Date Formats",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_specific_listing_details(self, listings):
        """Test 4: Get Specific Listing Details"""
        try:
            if not listings or len(listings) == 0:
                self.log_test(
                    "Specific Listing Details",
                    False,
                    "No listings available for detailed analysis"
                )
                return False
            
            print("=" * 60)
            print("SPECIFIC LISTING DETAILED ANALYSIS")
            print("=" * 60)
            
            # Get details for first 3 listings
            sample_size = min(3, len(listings))
            
            for i, listing in enumerate(listings[:sample_size]):
                listing_id = listing.get('id')
                if not listing_id:
                    print(f"Listing {i+1}: No ID found, skipping detailed fetch")
                    continue
                
                print(f"\n--- DETAILED ANALYSIS FOR LISTING {i+1} ---")
                print(f"ID: {listing_id}")
                
                try:
                    # Fetch individual listing details
                    response = self.session.get(f"{self.backend_url}/listings/{listing_id}")
                    
                    if response.status_code == 200:
                        detailed_listing = response.json()
                        
                        print("Date-related fields in detailed view:")
                        for field_name, field_value in detailed_listing.items():
                            if any(date_term in field_name.lower() for date_term in ['date', 'time', 'created', 'updated']):
                                print(f"  {field_name}: {field_value}")
                        
                        # Compare with browse data
                        print("Comparison with browse data:")
                        for field_name in ['created_at', 'updated_at', 'date', 'timestamp']:
                            browse_value = listing.get(field_name)
                            detail_value = detailed_listing.get(field_name)
                            
                            if browse_value is not None or detail_value is not None:
                                print(f"  {field_name}:")
                                print(f"    Browse: {browse_value}")
                                print(f"    Detail: {detail_value}")
                                print(f"    Match: {browse_value == detail_value}")
                    
                    else:
                        print(f"Failed to fetch detailed listing: HTTP {response.status_code}")
                
                except Exception as detail_error:
                    print(f"Error fetching listing details: {detail_error}")
            
            self.log_test(
                "Specific Listing Details",
                True,
                f"Analyzed detailed information for {sample_size} listings"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Specific Listing Details",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_date_debug_tests(self):
        """Run all date debugging tests"""
        print("=" * 80)
        print("DATE DISPLAY ISSUE DEBUG TESTING")
        print("Examining actual listing data structure for date fields")
        print("=" * 80)
        print()
        
        # Test 1: Browse Endpoint Basic Functionality
        listings = self.test_browse_endpoint_basic()
        
        if not listings:
            print("❌ Cannot proceed with date analysis - no listings available")
            return False
        
        # Test 2: Analyze Listing Date Fields
        date_analysis = self.analyze_listing_date_fields(listings)
        
        # Test 3: Verify Date Formats
        format_analysis = None
        if date_analysis:
            format_analysis = self.verify_date_formats(listings, date_analysis)
        
        # Test 4: Specific Listing Details
        self.test_specific_listing_details(listings)
        
        # Summary and Recommendations
        print("=" * 80)
        print("DATE DEBUG SUMMARY AND RECOMMENDATIONS")
        print("=" * 80)
        
        if date_analysis and format_analysis:
            print("✅ DATE FIELD ANALYSIS COMPLETED")
            print()
            print("KEY FINDINGS:")
            print(f"• Most common date field: '{format_analysis['field_name']}'")
            print(f"• Primary date format: {format_analysis['primary_format']}")
            print(f"• Sample values:")
            for i, value in enumerate(format_analysis['sample_values'][:3]):
                print(f"  {i+1}. {value}")
            
            print()
            print("RECOMMENDATIONS FOR FRONTEND:")
            
            field_name = format_analysis['field_name']
            primary_format = format_analysis['primary_format']
            
            if primary_format == "iso_format":
                print(f"• Use listing.{field_name} for date display")
                print("• Format with: new Date(listing.created_at).toLocaleDateString()")
                print("• Example: new Date('2025-01-30T15:30:00').toLocaleDateString()")
            elif primary_format == "timestamp":
                print(f"• Use listing.{field_name} for date display")
                print("• Format with: new Date(listing.created_at * 1000).toLocaleDateString()")
                print("• Note: Multiply by 1000 if timestamp is in seconds")
            else:
                print(f"• Date field '{field_name}' needs format investigation")
                print("• Consider backend date format standardization")
            
            print()
            print("FRONTEND CODE SUGGESTION:")
            print("```javascript")
            print("// In your listing tile component:")
            print(f"const formatDate = (listing) => {{")
            if primary_format == "iso_format":
                print(f"  if (listing.{field_name}) {{")
                print(f"    return new Date(listing.{field_name}).toLocaleDateString();")
                print("  }")
            elif primary_format == "timestamp":
                print(f"  if (listing.{field_name}) {{")
                print(f"    return new Date(listing.{field_name} * 1000).toLocaleDateString();")
                print("  }")
            print("  return 'Date not available';")
            print("};")
            print("```")
            
        else:
            print("❌ DATE FIELD ANALYSIS FAILED")
            print()
            print("ISSUES FOUND:")
            if not date_analysis:
                print("• No date-related fields found in listing data")
                print("• Backend may not be providing date information")
            
            print()
            print("RECOMMENDATIONS:")
            print("• Check backend listing creation to ensure date fields are saved")
            print("• Verify browse endpoint includes all necessary fields")
            print("• Consider adding created_at field to listing model if missing")
        
        print()
        return bool(date_analysis and format_analysis)

if __name__ == "__main__":
    tester = DateDebugTester()
    success = tester.run_date_debug_tests()
    
    if success:
        print("🎉 DATE DEBUG ANALYSIS COMPLETED - Check recommendations above!")
        sys.exit(0)
    else:
        print("⚠️  DATE DEBUG ANALYSIS INCOMPLETE - Check issues above")
        sys.exit(1)