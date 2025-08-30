/**
 * CATALORO - Ultra-Modern Shopping Cart
 * Advanced cart with wishlist, recommendations, and checkout
 * Now fully integrated with MarketplaceContext
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import { 
  ShoppingCart, 
  Minus, 
  Plus, 
  Trash2, 
  Heart, 
  ArrowRight,
  Gift,
  Truck,
  Shield,
  CreditCard,
  Tag,
  AlertCircle,
  CheckCircle,
  Star,
  Clock,
  MapPin
} from 'lucide-react';

function ShoppingCartPage() {
  const {
    cartItems,
    cartCount,
    cartTotal,
    favorites,
    updateQuantity,
    removeFromCart,
    addToCart,
    addToFavorites,
    removeFromFavorites,
    appliedPromo,
    applyPromo,
    removePromo,
    showNotification,
    allProducts
  } = useMarketplace();

  const [promoCode, setPromoCode] = useState('');

  const handleApplyPromo = () => {
    const success = applyPromo(promoCode);
    if (success) {
      setPromoCode('');
    }
  };

  const moveToSaved = (item) => {
    addToFavorites(item);
    removeFromCart(item.id);
    showNotification(`Moved ${item.title} to favorites`, 'info');
  };

  const moveToCart = (item) => {
    const cartItem = { ...item, quantity: 1 };
    addToCart(cartItem);
    removeFromFavorites(item.id);
  };

  // Get saved items (favorites that aren't in cart)
  const savedItems = favorites.filter(fav => 
    !cartItems.some(cartItem => cartItem.id === fav.id)
  );

  // Get recommended items (products not in cart or favorites)
  const recommendedItems = allProducts
    .filter(product => 
      !cartItems.some(cartItem => cartItem.id === product.id) &&
      !favorites.some(fav => fav.id === product.id)
    )
    .slice(0, 4);

  // Calculate totals
  const subtotal = cartTotal;
  const discount = appliedPromo ? subtotal * (appliedPromo.discount || 0) : 0;
  const shipping = appliedPromo?.shippingDiscount ? 0 : (subtotal > 0 ? 25 : 0);
  const tax = (subtotal - discount) * 0.08; // 8% tax
  const total = subtotal - discount + shipping + tax;

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <ShoppingCart className="w-8 h-8 mr-3" />
            Shopping Cart
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {cartCount} item{cartCount !== 1 ? 's' : ''} in your cart
          </p>
        </div>
        
        {cartItems.length > 0 && (
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              €{total.toFixed(2)}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
          </div>
        )}
      </div>

      {cartItems.length === 0 ? (
        // Empty Cart State
        <div className="text-center py-16">
          <div className="w-32 h-32 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShoppingCart className="w-16 h-16 text-gray-400" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Your cart is empty
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
            Looks like you haven't added anything to your cart yet. Start browsing to find amazing products!
          </p>
          <Link
            to="/browse"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
          >
            Start Shopping
            <ArrowRight className="w-5 h-5 ml-2" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Cart Items List */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Cart Items ({cartItems.length})
                </h2>
              </div>
              
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {cartItems.map((item) => (
                  <div key={item.id} className="p-6">
                    <div className="flex space-x-4">
                      
                      {/* Product Image */}
                      <div className="w-24 h-24 flex-shrink-0">
                        <img
                          src={item.images?.[0] || item.image || 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=200'}
                          alt={item.title}
                          className="w-full h-full object-cover rounded-lg"
                        />
                      </div>

                      {/* Product Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                              {item.title}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              Sold by {item.seller?.name || item.seller || 'Unknown Seller'}
                            </p>
                          </div>
                          
                          <div className="text-right">
                            <div className="flex items-center space-x-2">
                              <span className="text-xl font-bold text-gray-900 dark:text-white">
                                €{item.price}
                              </span>
                              {item.originalPrice && (
                                <span className="text-sm text-gray-500 line-through">
                                  €{item.originalPrice}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Rating and Reviews */}
                        <div className="flex items-center space-x-2 mb-3">
                          <div className="flex items-center">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">
                              {item.rating || 4.5} ({item.reviewCount || item.reviews || 0} reviews)
                            </span>
                          </div>
                        </div>

                        {/* Condition and Shipping */}
                        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
                          <span className="flex items-center">
                            <CheckCircle className="w-4 h-4 mr-1 text-green-500" />
                            {item.condition || 'New'}
                          </span>
                          <span className="flex items-center">
                            <Truck className="w-4 h-4 mr-1" />
                            {item.shipping || 'Standard shipping'}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {item.estimatedDelivery || '3-5 business days'}
                          </span>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center justify-end">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => moveToSaved(item)}
                              className="p-2 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                              title="Save for later"
                            >
                              <Heart className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => removeFromCart(item.id)}
                              className="p-2 text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                              title="Remove from cart"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Saved Items */}
            {savedItems.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                    <Heart className="w-6 h-6 mr-2 text-red-500" />
                    Saved for Later ({savedItems.length})
                  </h2>
                </div>
                
                <div className="p-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {savedItems.map((item) => (
                      <div key={item.id} className="flex space-x-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                        <img
                          src={item.images?.[0] || item.image || 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=200'}
                          alt={item.title}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                            {item.title}
                          </h4>
                          <p className="text-lg font-bold text-blue-600">€{item.price}</p>
                          <button
                            onClick={() => moveToCart(item)}
                            className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-1"
                          >
                            Add to Cart
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Recommended Items */}
            {recommendedItems.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    You might also like
                  </h2>
                </div>
                
                <div className="p-6">
                  <div className="grid grid-cols-2 gap-4">
                    {recommendedItems.map((item) => (
                      <div key={item.id} className="text-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                        <img
                          src={item.images?.[0] || 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=200'}
                          alt={item.title}
                          className="w-full h-24 object-cover rounded-lg mb-3"
                        />
                        <h4 className="font-medium text-gray-900 dark:text-white text-sm mb-1">
                          {item.title}
                        </h4>
                        <p className="text-lg font-bold text-blue-600 mb-2">€{item.price}</p>
                        <button 
                          onClick={() => addToCart(item)}
                          className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                        >
                          Add to Cart
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
                
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                  Order Summary
                </h2>

                {/* Promo Code */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Promo Code
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value)}
                      placeholder="Enter code"
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <button
                      onClick={handleApplyPromo}
                      className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors font-medium"
                    >
                      Apply
                    </button>
                  </div>
                  
                  {appliedPromo && (
                    <div className="mt-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                          <span className="text-sm text-green-800 dark:text-green-200 font-medium">
                            {appliedPromo.description}
                          </span>
                        </div>
                        <button
                          onClick={removePromo}
                          className="text-green-600 hover:text-green-700"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Price Breakdown */}
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-gray-600 dark:text-gray-400">
                    <span>Subtotal ({cartItems.length} items)</span>
                    <span>€{subtotal.toFixed(2)}</span>
                  </div>
                  
                  {discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount ({appliedPromo.code})</span>
                      <span>-${discount.toFixed(2)}</span>
                    </div>
                  )}
                  
                  <div className="flex justify-between text-gray-600 dark:text-gray-400">
                    <span>Shipping</span>
                    <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
                  </div>
                  
                  <div className="flex justify-between text-gray-600 dark:text-gray-400">
                    <span>Tax</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>
                  
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                    <div className="flex justify-between text-xl font-bold text-gray-900 dark:text-white">
                      <span>Total</span>
                      <span>${total.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {/* Trust Indicators */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <Shield className="w-4 h-4 mr-2 text-green-500" />
                    <span>Secure checkout with SSL encryption</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <Truck className="w-4 h-4 mr-2 text-blue-500" />
                    <span>Fast and reliable shipping</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <Gift className="w-4 h-4 mr-2 text-purple-500" />
                    <span>Gift wrapping available</span>
                  </div>
                </div>

                {/* Checkout Button */}
                <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-4 rounded-xl font-semibold text-lg transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center">
                  <CreditCard className="w-6 h-6 mr-2" />
                  Proceed to Checkout
                </button>

                <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-3">
                  By proceeding, you agree to our Terms and Privacy Policy
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ShoppingCartPage;