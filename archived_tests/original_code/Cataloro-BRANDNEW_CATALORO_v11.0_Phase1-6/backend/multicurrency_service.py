"""
Multi-Currency Service for Cataloro Marketplace - Phase 5B
Handles multiple currencies, live conversion rates, and international payments
"""

import asyncio
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_HALF_UP
import aiofiles

logger = logging.getLogger(__name__)

class MultiCurrencyService:
    def __init__(self, db):
        self.db = db
        
        # Supported currencies with metadata
        self.supported_currencies = {
            "EUR": {"name": "Euro", "symbol": "€", "code": "EUR", "decimal_places": 2, "is_base": True},
            "USD": {"name": "US Dollar", "symbol": "$", "code": "USD", "decimal_places": 2},
            "GBP": {"name": "British Pound", "symbol": "£", "code": "GBP", "decimal_places": 2},
            "CHF": {"name": "Swiss Franc", "symbol": "CHF", "code": "CHF", "decimal_places": 2},
            "JPY": {"name": "Japanese Yen", "symbol": "¥", "code": "JPY", "decimal_places": 0},
            "CAD": {"name": "Canadian Dollar", "symbol": "C$", "code": "CAD", "decimal_places": 2},
            "AUD": {"name": "Australian Dollar", "symbol": "A$", "code": "AUD", "decimal_places": 2},
            "SEK": {"name": "Swedish Krona", "symbol": "kr", "code": "SEK", "decimal_places": 2},
            "NOK": {"name": "Norwegian Krone", "symbol": "kr", "code": "NOK", "decimal_places": 2},
            "DKK": {"name": "Danish Krone", "symbol": "kr", "code": "DKK", "decimal_places": 2}
        }
        
        # Base currency (EUR as platform default)
        self.base_currency = "EUR"
        
        # Exchange rates cache
        self.exchange_rates = {}
        self.rates_last_updated = None
        self.rates_cache_duration = 3600  # 1 hour
        
        # Fallback rates for when API is unavailable
        self.fallback_rates = {
            "USD": 1.08,
            "GBP": 0.85,
            "CHF": 0.95,
            "JPY": 160.0,
            "CAD": 1.45,
            "AUD": 1.65,
            "SEK": 11.2,
            "NOK": 11.8,
            "DKK": 7.45
        }
        
        logger.info("✅ Multi-currency service initialized")
    
    async def get_exchange_rates(self, force_refresh: bool = False) -> Dict[str, float]:
        """Get current exchange rates"""
        try:
            # Check if cache is still valid
            if (not force_refresh and 
                self.rates_last_updated and 
                self.exchange_rates and
                datetime.utcnow() - self.rates_last_updated < timedelta(seconds=self.rates_cache_duration)):
                return self.exchange_rates
            
            # Try to fetch from external API (using free service)
            rates = await self._fetch_rates_from_api()
            
            if rates:
                self.exchange_rates = rates
                self.rates_last_updated = datetime.utcnow()
                
                # Store in database for persistence
                await self._store_exchange_rates(rates)
            else:
                # Use fallback rates or cached rates
                if self.exchange_rates:
                    logger.warning("Using cached exchange rates due to API failure")
                else:
                    logger.warning("Using fallback exchange rates")
                    self.exchange_rates = self.fallback_rates.copy()
                    self.exchange_rates[self.base_currency] = 1.0
            
            return self.exchange_rates
            
        except Exception as e:
            logger.error(f"Failed to get exchange rates: {e}")
            # Return fallback or cached rates
            if not self.exchange_rates:
                self.exchange_rates = self.fallback_rates.copy()
                self.exchange_rates[self.base_currency] = 1.0
            return self.exchange_rates
    
    async def _fetch_rates_from_api(self) -> Optional[Dict[str, float]]:
        """Fetch exchange rates from external API"""
        try:
            # Using a free exchange rate API (replace with preferred service)
            # Note: In production, use a reliable paid service like Open Exchange Rates
            
            # Try exchangerate-api.com (free tier available)
            url = f"https://api.exchangerate-api.com/v4/latest/{self.base_currency}"
            
            # Make async request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(url, timeout=10)
            )
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                
                # Filter to only supported currencies
                filtered_rates = {}
                for currency in self.supported_currencies:
                    if currency in rates:
                        filtered_rates[currency] = float(rates[currency])
                    elif currency == self.base_currency:
                        filtered_rates[currency] = 1.0
                
                logger.info(f"📊 Updated exchange rates: {len(filtered_rates)} currencies")
                return filtered_rates
            
        except Exception as e:
            logger.error(f"API rate fetch failed: {e}")
        
        return None
    
    async def _store_exchange_rates(self, rates: Dict[str, float]):
        """Store exchange rates in database"""
        try:
            rate_document = {
                "base_currency": self.base_currency,
                "rates": rates,
                "updated_at": datetime.utcnow().isoformat(),
                "source": "api"
            }
            
            # Store with upsert
            await self.db.exchange_rates.replace_one(
                {"base_currency": self.base_currency},
                rate_document,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to store exchange rates: {e}")
    
    async def convert_currency(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str
    ) -> Dict[str, Any]:
        """Convert amount from one currency to another"""
        try:
            if from_currency == to_currency:
                return {
                    "original_amount": amount,
                    "converted_amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "exchange_rate": 1.0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get current exchange rates
            rates = await self.get_exchange_rates()
            
            # Convert via base currency if needed
            if from_currency == self.base_currency:
                # Base to target
                rate = rates.get(to_currency, 1.0)
                converted = amount * rate
            elif to_currency == self.base_currency:
                # Source to base
                rate = 1.0 / rates.get(from_currency, 1.0)
                converted = amount * rate
            else:
                # Source to base, then base to target
                to_base_rate = 1.0 / rates.get(from_currency, 1.0)
                to_target_rate = rates.get(to_currency, 1.0)
                rate = to_base_rate * to_target_rate
                converted = amount * rate
            
            # Round to appropriate decimal places
            decimal_places = self.supported_currencies.get(to_currency, {}).get("decimal_places", 2)
            converted = round(converted, decimal_places)
            
            return {
                "original_amount": amount,
                "converted_amount": converted,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "timestamp": datetime.utcnow().isoformat(),
                "decimal_places": decimal_places
            }
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {e}")
            return {
                "original_amount": amount,
                "converted_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": 1.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_currency_info(self, currency_code: str) -> Optional[Dict]:
        """Get currency information"""
        return self.supported_currencies.get(currency_code.upper())
    
    async def format_currency(self, amount: float, currency_code: str) -> str:
        """Format amount with currency symbol and proper decimals"""
        try:
            currency_info = self.supported_currencies.get(currency_code.upper())
            if not currency_info:
                return f"{amount:.2f} {currency_code}"
            
            decimal_places = currency_info["decimal_places"]
            symbol = currency_info["symbol"]
            
            formatted_amount = f"{amount:.{decimal_places}f}"
            
            # Different positioning for different currencies
            if currency_code in ["USD", "GBP", "CAD", "AUD"]:
                return f"{symbol}{formatted_amount}"
            elif currency_code == "JPY":
                return f"¥{formatted_amount}"
            else:
                return f"{formatted_amount} {symbol}"
                
        except Exception as e:
            logger.error(f"Currency formatting failed: {e}")
            return f"{amount:.2f} {currency_code}"
    
    async def get_user_preferred_currency(self, user_id: str) -> str:
        """Get user's preferred currency"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            if user and "preferred_currency" in user:
                return user["preferred_currency"]
            return self.base_currency
            
        except Exception as e:
            logger.error(f"Failed to get user currency preference: {e}")
            return self.base_currency
    
    async def set_user_preferred_currency(self, user_id: str, currency_code: str) -> bool:
        """Set user's preferred currency"""
        try:
            if currency_code.upper() not in self.supported_currencies:
                return False
            
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"preferred_currency": currency_code.upper()}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set user currency preference: {e}")
            return False
    
    async def convert_listing_prices(self, listings: List[Dict], target_currency: str) -> List[Dict]:
        """Convert listing prices to target currency"""
        try:
            converted_listings = []
            
            for listing in listings:
                converted_listing = listing.copy()
                
                # Convert main price
                if "price" in listing:
                    conversion = await self.convert_currency(
                        listing["price"],
                        self.base_currency,  # Assuming all prices stored in base currency
                        target_currency
                    )
                    
                    converted_listing["price"] = conversion["converted_amount"]
                    converted_listing["original_price"] = listing["price"]
                    converted_listing["price_currency"] = target_currency
                    converted_listing["exchange_rate"] = conversion["exchange_rate"]
                    
                    # Format for display
                    converted_listing["formatted_price"] = await self.format_currency(
                        conversion["converted_amount"],
                        target_currency
                    )
                
                converted_listings.append(converted_listing)
            
            return converted_listings
            
        except Exception as e:
            logger.error(f"Failed to convert listing prices: {e}")
            return listings  # Return original on error
    
    async def create_currency_conversion_history(
        self, 
        user_id: str, 
        conversion_data: Dict
    ):
        """Store currency conversion history"""
        try:
            history_entry = {
                "user_id": user_id,
                "conversion_data": conversion_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.db.currency_conversion_history.insert_one(history_entry)
            
        except Exception as e:
            logger.error(f"Failed to store conversion history: {e}")
    
    async def get_supported_currencies(self) -> List[Dict]:
        """Get list of supported currencies with current rates"""
        try:
            rates = await self.get_exchange_rates()
            
            currencies = []
            for code, info in self.supported_currencies.items():
                currency_data = info.copy()
                currency_data["current_rate"] = rates.get(code, 1.0)
                currency_data["rate_vs_base"] = rates.get(code, 1.0)
                currencies.append(currency_data)
            
            return currencies
            
        except Exception as e:
            logger.error(f"Failed to get supported currencies: {e}")
            return list(self.supported_currencies.values())
    
    async def get_currency_trends(self, currency_code: str, days: int = 30) -> Dict:
        """Get currency trends over time (simplified)"""
        try:
            # In a real implementation, this would fetch historical data
            # For now, return mock trend data
            return {
                "currency": currency_code,
                "period_days": days,
                "trend": "stable",  # stable, rising, falling
                "change_percentage": 0.5,  # Mock 0.5% change
                "historical_rates": [],  # Would contain daily rates
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get currency trends: {e}")
            return {}
    
    async def calculate_fee_in_currency(
        self, 
        base_fee: float, 
        currency_code: str
    ) -> Dict:
        """Calculate platform fees in specific currency"""
        try:
            conversion = await self.convert_currency(
                base_fee,
                self.base_currency,
                currency_code
            )
            
            return {
                "base_fee": base_fee,
                "base_currency": self.base_currency,
                "converted_fee": conversion["converted_amount"],
                "fee_currency": currency_code,
                "formatted_fee": await self.format_currency(
                    conversion["converted_amount"],
                    currency_code
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate fee in currency: {e}")
            return {
                "base_fee": base_fee,
                "base_currency": self.base_currency,
                "converted_fee": base_fee,
                "fee_currency": currency_code,
                "error": str(e)
            }
    
    async def get_currency_stats(self) -> Dict:
        """Get currency service statistics"""
        try:
            rates = await self.get_exchange_rates()
            
            return {
                "supported_currencies": len(self.supported_currencies),
                "base_currency": self.base_currency,
                "rates_last_updated": self.rates_last_updated.isoformat() if self.rates_last_updated else None,
                "active_rates": len(rates),
                "cache_duration_seconds": self.rates_cache_duration,
                "currency_list": list(self.supported_currencies.keys()),
                "service_status": "operational" if rates else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Failed to get currency stats: {e}")
            return {
                "service_status": "error",
                "error": str(e)
            }

# Global multi-currency service instance
multicurrency_service = None

async def init_multicurrency_service(db):
    """Initialize multi-currency service"""
    global multicurrency_service
    multicurrency_service = MultiCurrencyService(db)
    return multicurrency_service

def get_multicurrency_service():
    """Get multi-currency service instance"""
    return multicurrency_service