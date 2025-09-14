#!/usr/bin/env python3
"""
Debug script to test date parsing logic
"""

from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_date_parsing(date_string):
    """Test the date parsing logic"""
    print(f"\n🔍 Testing date parsing for: {date_string}")
    
    if date_string:
        # Format date nicely
        if isinstance(date_string, str):
            try:
                # Handle different date formats
                date_str = date_string
                print(f"Original date string: {date_str}")
                
                # Remove microseconds if present (e.g., 2025-09-09T10:20:41.643000 -> 2025-09-09T10:20:41)
                if '.' in date_str:
                    date_str = date_str.split('.')[0]
                    print(f"Removed microseconds: {date_str}")
                
                # Add timezone if missing
                if 'T' in date_str and not ('+' in date_str or 'Z' in date_str):
                    date_str = date_str + '+00:00'
                    print(f"Added UTC timezone: {date_str}")
                elif 'Z' in date_str:
                    date_str = date_str.replace('Z', '+00:00')
                    print(f"Replaced Z with +00:00: {date_str}")
                
                date_obj = datetime.fromisoformat(date_str)
                formatted_date = date_obj.strftime("%b %Y")  # e.g., "Sep 2025"
                print(f"✅ Successfully formatted date: {formatted_date}")
                return formatted_date
            except Exception as e:
                print(f"❌ Error formatting date {date_string}: {str(e)}")
                # Try simple string parsing as fallback
                try:
                    # Extract year and month from YYYY-MM-DD format
                    if len(date_string) >= 10:
                        year = date_string[:4]
                        month_num = date_string[5:7]
                        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        month_name = month_names[int(month_num)]
                        formatted_date = f"{month_name} {year}"
                        print(f"✅ Fallback parsing successful: {formatted_date}")
                        return formatted_date
                    else:
                        print("❌ Date string too short for fallback parsing")
                        return "Unknown"
                except Exception as e2:
                    print(f"❌ Fallback parsing also failed: {str(e2)}")
                    return "Unknown"
        else:
            print("❌ Date is not a string")
            return "Unknown"
    else:
        print("❌ No date provided")
        return "Unknown"

if __name__ == "__main__":
    # Test with the actual date strings we're seeing
    test_cases = [
        "2025-09-09T10:20:41.643000",
        "2025-09-09T09:53:56.308000",
        "2025-09-09T10:20:41",
        "2025-09-09",
        None,
        ""
    ]
    
    for test_case in test_cases:
        result = test_date_parsing(test_case)
        print(f"Result: {result}")
        print("-" * 50)