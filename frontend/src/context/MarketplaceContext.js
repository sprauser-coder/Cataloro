/**
 * CATALORO - Comprehensive Marketplace State Management
 * Full state management for cart, favorites, search, and all interactions
 */

import { createContext, useContext, useReducer, useEffect } from 'react';
import { marketplaceService } from '../services/marketplaceService';
import { liveService } from '../services/liveService';

// Initial state
const initialState = {
  // Favorites/Wishlist
  favorites: [],
  favoriteCount: 0,
  
  // Search & Filters
  searchQuery: '',
  activeFilters: {
    type: 'all', // Changed from category to type (Private/Business)
    priceFrom: 0, // Changed from priceRange array to separate from/to values
    priceTo: 10000,
    rating: 0,
    location: 'all'
    // Removed condition filter
  },
  
  // Products & Listings
  allProducts: [],
  filteredProducts: [],
  categories: [],
  
  // User Interactions
  recentlyViewed: [],
  notifications: [],
  messages: [],
  
  // UI State
  viewMode: 'grid',
  sortBy: 'newest',
  isLoading: false,
  
  // Promo Codes
  appliedPromo: null,
  availablePromos: [
    { code: 'SAVE10', discount: 0.1, description: '10% off your order' },
    { code: 'FREESHIP', shippingDiscount: true, description: 'Free shipping' },
    { code: 'WELCOME20', discount: 0.2, description: '20% off first order', minAmount: 100 }
  ]
};

// Action types
const ACTIONS = {

  APPLY_PROMO: 'APPLY_PROMO',
  REMOVE_PROMO: 'REMOVE_PROMO',
  
  // Favorites Actions
  ADD_TO_FAVORITES: 'ADD_TO_FAVORITES',
  REMOVE_FROM_FAVORITES: 'REMOVE_FROM_FAVORITES',
  SET_FAVORITES: 'SET_FAVORITES',
  
  // Product Actions
  SET_PRODUCTS: 'SET_PRODUCTS',
  SET_FILTERED_PRODUCTS: 'SET_FILTERED_PRODUCTS',
  ADD_PRODUCT: 'ADD_PRODUCT',
  UPDATE_PRODUCT: 'UPDATE_PRODUCT',
  DELETE_PRODUCT: 'DELETE_PRODUCT',
  
  // Search & Filter Actions
  SET_SEARCH_QUERY: 'SET_SEARCH_QUERY',
  SET_FILTERS: 'SET_FILTERS',
  SET_SORT_BY: 'SET_SORT_BY',
  SET_VIEW_MODE: 'SET_VIEW_MODE',
  
  // UI Actions
  SET_LOADING: 'SET_LOADING',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  ADD_TO_RECENTLY_VIEWED: 'ADD_TO_RECENTLY_VIEWED',
  
  // Messages
  ADD_MESSAGE: 'ADD_MESSAGE',
  MARK_MESSAGE_READ: 'MARK_MESSAGE_READ'
};

// Reducer
function marketplaceReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADD_TO_FAVORITES: {
      if (state.favorites.some(item => item.id === action.payload.id)) {
        return state; // Already in favorites
      }
      
      return {
        ...state,
        favorites: [...state.favorites, action.payload],
        favoriteCount: state.favoriteCount + 1
      };
    }
    
    case ACTIONS.REMOVE_FROM_FAVORITES: {
      return {
        ...state,
        favorites: state.favorites.filter(item => item.id !== action.payload),
        favoriteCount: Math.max(0, state.favoriteCount - 1)
      };
    }
    
    case ACTIONS.SET_FAVORITES:
      return {
        ...state,
        favorites: action.payload,
        favoriteCount: action.payload.length
      };
    
    case ACTIONS.SET_PRODUCTS: {
      // Apply current sort when setting products
      const sortedProducts = [...action.payload].sort((a, b) => {
        switch (state.sortBy) {
          case 'price_low':
            return a.price - b.price;
          case 'price_high':
            return b.price - a.price;
          case 'rating':
            return (b.rating || 0) - (a.rating || 0);
          case 'popular':
            return (b.views || 0) - (a.views || 0);
          case 'newest':
          default:
            return new Date(b.created_at || b.createdAt) - new Date(a.created_at || a.createdAt);
        }
      });
      
      return {
        ...state,
        allProducts: action.payload,
        filteredProducts: sortedProducts
      };
    }
    
    case ACTIONS.SET_FILTERED_PRODUCTS:
      return {
        ...state,
        filteredProducts: action.payload
      };
    
    case ACTIONS.SET_SEARCH_QUERY:
      return {
        ...state,
        searchQuery: action.payload
      };
    
    case ACTIONS.SET_FILTERS:
      return {
        ...state,
        activeFilters: { ...state.activeFilters, ...action.payload }
      };
    
    case ACTIONS.SET_SORT_BY:
      return {
        ...state,
        sortBy: action.payload
      };
    
    case ACTIONS.SET_VIEW_MODE:
      return {
        ...state,
        viewMode: action.payload
      };
    
    case ACTIONS.APPLY_PROMO: {
      const promo = state.availablePromos.find(p => p.code === action.payload);
      return {
        ...state,
        appliedPromo: promo || null
      };
    }
    
    case ACTIONS.REMOVE_PROMO:
      return {
        ...state,
        appliedPromo: null
      };
    
    case ACTIONS.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [action.payload, ...state.notifications]
      };
    
    case ACTIONS.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    
    case ACTIONS.ADD_TO_RECENTLY_VIEWED: {
      const filtered = state.recentlyViewed.filter(item => item.id !== action.payload.id);
      return {
        ...state,
        recentlyViewed: [action.payload, ...filtered].slice(0, 10) // Keep last 10
      };
    }
    
    case ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    default:
      return state;
  }
}

// Create context
const MarketplaceContext = createContext();

// Provider component
export function MarketplaceProvider({ children }) {
  const [state, dispatch] = useReducer(marketplaceReducer, initialState);

  // Load from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('cataloro_cart');
    const savedFavorites = localStorage.getItem('cataloro_favorites');
    
    if (savedCart) {
      try {
        const cart = JSON.parse(savedCart);
        cart.forEach(item => {
          dispatch({ type: ACTIONS.ADD_TO_CART, payload: item });
        });
      } catch (error) {
        console.error('Error loading cart from storage:', error);
      }
    }
    
    if (savedFavorites) {
      try {
        const favorites = JSON.parse(savedFavorites);
        favorites.forEach(item => {
          dispatch({ type: ACTIONS.ADD_TO_FAVORITES, payload: item });
        });
      } catch (error) {
        console.error('Error loading favorites from storage:', error);
      }
    }

    // Load initial products
    loadInitialProducts();
  }, []);

  // Save to localStorage when cart or favorites change
  useEffect(() => {
    localStorage.setItem('cataloro_cart', JSON.stringify(state.cartItems));
  }, [state.cartItems]);

  useEffect(() => {
    localStorage.setItem('cataloro_favorites', JSON.stringify(state.favorites));
  }, [state.favorites]);

  const loadInitialProducts = async (filters = null) => {
    // Set loading state
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    
    try {
      // Use provided filters or current state filters
      const currentFilters = filters || state.activeFilters;
      
      // Convert filter format for API call
      const apiFilters = {};
      if (currentFilters.type && currentFilters.type !== 'all') {
        apiFilters.type = currentFilters.type;
      }
      if (currentFilters.priceFrom > 0) {
        apiFilters.price_from = currentFilters.priceFrom;
      }
      if (currentFilters.priceTo < 10000) {
        apiFilters.price_to = currentFilters.priceTo;
      }
      
      // Try to fetch real listings from API using marketplaceService
      const apiResponse = await marketplaceService.browseListings(apiFilters);
      console.log('✅ Loaded real listings from API with filters:', apiFilters, apiResponse);
      
      // The browse endpoint returns array format directly
      let apiListings;
      if (Array.isArray(apiResponse)) {
        apiListings = apiResponse;
      } else {
        throw new Error('Invalid API response format: expected array');
      }
      
      console.log('📋 Processing listings:', apiListings.length);
      
      // Debug: Log first listing to see data structure
      if (apiListings.length > 0) {
        console.log('🔍 First listing raw data:', JSON.stringify(apiListings[0], null, 2));
        console.log('🔍 First listing seller data:', apiListings[0].seller);
      }
      
      // Transform API listings to match expected format
      const transformedListings = apiListings.map((listing, index) => {
        const transformed = {
          id: listing.id,
          title: listing.title,
          description: listing.description,
          price: parseFloat(listing.price) || 0, // Ensure price is a number
          originalPrice: (parseFloat(listing.price) || 0) * 1.1, // Add 10% as original price for demo
          category: listing.category,
          condition: listing.condition,
          location: listing.location || 'Unknown',
          images: listing.images || [],
          // CRITICAL: Preserve bid_info from API for price display logic
          bid_info: listing.bid_info || {
            has_bids: false,
            total_bids: 0,
            highest_bid: parseFloat(listing.price) || 0,
            highest_bidder_id: ''
          },
          // CRITICAL: Preserve time_info from API for countdown timer display
          time_info: listing.time_info || {
            has_time_limit: false,
            is_expired: false,
            time_remaining_seconds: null,
            expires_at: null,
            status_text: null
          },
          // Preserve complete seller object with business information
          seller: {
            ...listing.seller,
            name: listing.seller?.name || 'Unknown Seller',
            username: listing.seller?.username || 'Unknown',
            email: listing.seller?.email || '',
            is_business: listing.seller?.is_business || false,
            business_name: listing.seller?.business_name || '',
            verified: listing.seller?.verified || false,
            location: listing.seller?.location || 'Unknown'
          },
          // Also add the address information for location display
          address: listing.address || {},
          // CRITICAL: Preserve created_at for date display
          created_at: listing.created_at,
          updated_at: listing.updated_at,
          rating: 4.5, // Default rating for demo
          reviewCount: Math.floor(Math.random() * 100) + 10,
          isHotDeal: Math.random() > 0.7,
          hasFastShipping: Math.random() > 0.6,
          verified: listing.seller?.verified || false,
          inStock: true,
          quantity: 1,
          tags: listing.tags || [],
          features: listing.features || []
        };
        
        // Debug: Log transformed data for first listing
        if (index === 0) {
          console.log('🔄 First listing transformed:', JSON.stringify(transformed, null, 2));
          console.log('🔄 First listing seller after transform:', transformed.seller);
        }
        
        return transformed;
      });
      
      // Use real listings even if empty (don't fall back to demo data)
      dispatch({ type: ACTIONS.SET_PRODUCTS, payload: transformedListings });
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
      console.log('🎉 Successfully loaded', transformedListings.length, 'real listings from API');
      return;
        
    } catch (error) {
      console.error('Failed to load listings from API:', error);
    }
    
    // Fallback to demo data if API fails or returns no data
    console.log('⚠️ Using demo data - no real listings found');
    const products = [
      {
        id: '1',
        title: 'MacBook Pro 16-inch M3 Max',
        description: 'Professional laptop with M3 Max chip, perfect for developers and creators. Includes original box and all accessories.',
        price: 2499,
        originalPrice: 2799,
        category: 'Electronics',
        subcategory: 'Laptops',
        seller: {
          name: 'TechGuru123',
          username: 'TechGuru123',
          email: 'techguru123@example.com',
          rating: 4.9,
          reviews: 156,
          verified: true,
          is_business: false, // Private seller
          location: 'San Francisco, CA'
        },
        images: [
          'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500',
          'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500',
          'https://images.unsplash.com/photo-1585337701044-7305994ea6fb?w=500'
        ],
        condition: 'Like New',
        views: 234,
        favorites: 45,
        createdAt: new Date().toISOString(),
        features: ['M3 Max Chip', '64GB RAM', '2TB SSD', 'Space Gray', '16-inch Display'],
        shipping: 'Free shipping',
        estimatedDelivery: '2-3 business days',
        rating: 4.8,
        reviewCount: 156,
        tags: ['Hot Deal', 'Fast Shipping', 'Professional'],
        inStock: true,
        quantity: 1
      },
      {
        id: '2',
        title: 'Vintage Gibson Les Paul Standard 1959',
        description: 'Authentic 1959 Gibson Les Paul in museum-quality condition. This is a collector\'s dream with incredible tone and playability.',
        price: 45000,
        originalPrice: 55000,
        category: 'Music',
        subcategory: 'Guitars',
        seller: {
          name: 'VintageGuitars_Pro',
          username: 'VintageGuitars_Pro',
          email: 'vintage.guitars.pro@example.com',
          rating: 4.9,
          reviews: 89,
          verified: true,
          is_business: true, // Business seller
          company_name: 'Vintage Guitars Pro LLC',
          location: 'Nashville, TN'
        },
        images: [
          'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=500',
          'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=500',
          'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500'
        ],
        condition: 'Excellent',
        views: 1289,
        favorites: 267,
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        features: ['1959 Model', 'Original Case', 'Certificate of Authenticity', 'Museum Quality'],
        shipping: 'Insured shipping - $150',
        estimatedDelivery: '3-5 business days',
        rating: 4.9,
        reviewCount: 89,
        tags: ['Vintage', 'Authenticated', 'Collector Item'],
        inStock: true,
        quantity: 1
      },
      {
        id: '3',
        title: 'Louis Vuitton Neverfull MM',
        description: 'Authentic Louis Vuitton handbag in pristine condition. Perfect for daily use with elegant design.',
        price: 1850,
        originalPrice: 2200,
        category: 'Fashion',
        subcategory: 'Handbags',
        seller: {
          name: 'LuxuryItems_NYC',
          username: 'LuxuryItems_NYC',
          email: 'luxury.items.nyc@example.com',
          rating: 4.7,
          reviews: 245,
          verified: true,
          is_business: true, // Business seller
          company_name: 'Luxury Items NYC Inc.',
          location: 'New York, NY'
        },
        images: [
          'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500',
          'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500'
        ],
        condition: 'Excellent',
        views: 456,
        favorites: 189,
        createdAt: new Date(Date.now() - 172800000).toISOString(),
        features: ['Authentic', 'Dust Bag Included', 'Care Instructions', 'Serial Number'],
        shipping: 'Express delivery - $25',
        estimatedDelivery: '1-2 business days',
        rating: 4.6,
        reviewCount: 245,
        tags: ['Luxury', 'Authentic', 'Designer'],
        inStock: true,
        quantity: 1
      },
      {
        id: '4',
        title: 'Gaming PC - RTX 4090 Build',
        description: 'Ultimate gaming PC with RTX 4090, perfect for 4K gaming, streaming, and content creation.',
        price: 4200,
        originalPrice: 4800,
        category: 'Electronics',
        subcategory: 'Computers',
        seller: {
          name: 'PCBuilder_Expert',
          rating: 4.9,
          reviews: 78,
          verified: true,
          location: 'Austin, TX'
        },
        images: [
          'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=500'
        ],
        condition: 'New',
        views: 698,
        favorites: 212,
        createdAt: new Date(Date.now() - 43200000).toISOString(),
        features: ['RTX 4090', 'Intel i9-13900K', '64GB RAM', 'Custom Cooling'],
        shipping: 'Free shipping',
        estimatedDelivery: '3-5 business days',
        rating: 5.0,
        reviewCount: 78,
        tags: ['Gaming', 'Custom Built', 'High Performance'],
        inStock: true,
        quantity: 1
      },
      {
        id: '5',
        title: 'iPhone 15 Pro Max 1TB',
        description: 'Latest iPhone 15 Pro Max in Natural Titanium with maximum storage capacity.',
        price: 1599,
        category: 'Electronics',
        subcategory: 'Smartphones',
        seller: {
          name: 'AppleStore_Certified',
          rating: 4.8,
          reviews: 324,
          verified: true,
          location: 'Cupertino, CA'
        },
        images: [
          'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500'
        ],
        condition: 'New',
        views: 1205,
        favorites: 398,
        createdAt: new Date(Date.now() - 21600000).toISOString(),
        features: ['1TB Storage', 'Natural Titanium', 'Pro Camera System', 'A17 Pro Chip'],
        shipping: 'Free shipping',
        estimatedDelivery: '1-2 business days',
        rating: 4.8,
        reviewCount: 324,
        tags: ['Latest Model', 'Premium', 'Fast Shipping'],
        inStock: true,
        quantity: 1
      }
    ];

    dispatch({ type: ACTIONS.SET_PRODUCTS, payload: products });
  };

  // Action creators
  const actions = {
    // Favorites actions with live API
    addToFavorites: async (product, userId = null) => {
      if (state.favorites.some(item => item.id === product.id)) {
        showNotification('Already in favorites!', 'info');
        return;
      }
      
      try {
        if (userId) {
          await liveService.addToFavorites(userId, product.id);
        }
        dispatch({ type: ACTIONS.ADD_TO_FAVORITES, payload: product });
        showNotification(`Added ${product.title} to favorites!`, 'success');
      } catch (error) {
        console.error('Error adding to favorites:', error);
        // Fallback to local action
        dispatch({ type: ACTIONS.ADD_TO_FAVORITES, payload: product });
        showNotification(`Added ${product.title} to favorites!`, 'success');
      }
    },
    
    removeFromFavorites: async (productId, userId = null) => {
      try {
        if (userId) {
          await liveService.removeFromFavorites(userId, productId);
        }
        dispatch({ type: ACTIONS.REMOVE_FROM_FAVORITES, payload: productId });
        showNotification('Removed from favorites', 'info');
      } catch (error) {
        console.error('Error removing from favorites:', error);
        // Fallback to local action
        dispatch({ type: ACTIONS.REMOVE_FROM_FAVORITES, payload: productId });
        showNotification('Removed from favorites', 'info');
      }
    },
    
    // Load live data from backend
    loadUserFavorites: async (userId) => {
      try {
        const favorites = await liveService.getUserFavorites(userId);
        dispatch({ type: ACTIONS.SET_FAVORITES, payload: favorites });
      } catch (error) {
        console.error('Error loading user favorites:', error);
      }
    },
    
    loadUserCart: async (userId) => {
      try {
        const cartItems = await liveService.getUserCart(userId);
        dispatch({ type: ACTIONS.SET_CART, payload: cartItems });
      } catch (error) {
        console.error('Error loading user cart:', error);
      }
    },
    
    // Search and filter actions
    setSearchQuery: async (query) => {
      dispatch({ type: ACTIONS.SET_SEARCH_QUERY, payload: query });
      
      // If we have active backend filters, reload with them and then apply search locally
      if (state.activeFilters.type !== 'all' || state.activeFilters.priceFrom > 0 || state.activeFilters.priceTo < 10000) {
        await loadInitialProducts(state.activeFilters);
      }
      
      // Apply search and sorting locally
      applyFiltersAndSearch(query, state.activeFilters, state.sortBy);
    },
    
    setFilters: async (filters) => {
      const newFilters = { ...state.activeFilters, ...filters };
      dispatch({ type: ACTIONS.SET_FILTERS, payload: filters });
      
      // For type and price filters, reload from backend
      if (filters.type !== undefined || filters.priceFrom !== undefined || filters.priceTo !== undefined) {
        await loadInitialProducts(newFilters);
      } else {
        // For other filters (search, sorting), use local filtering
        applyFiltersAndSearch(state.searchQuery, newFilters, state.sortBy);
      }
    },
    
    setSortBy: (sortBy) => {
      dispatch({ type: ACTIONS.SET_SORT_BY, payload: sortBy });
      applyFiltersAndSearch(state.searchQuery, state.activeFilters, sortBy);
    },
    
    setViewMode: (mode) => {
      dispatch({ type: ACTIONS.SET_VIEW_MODE, payload: mode });
    },
    
    // Promo actions
    applyPromo: (code) => {
      const promo = state.availablePromos.find(p => p.code === code.toUpperCase());
      if (promo) {
        if (promo.minAmount && state.cartTotal < promo.minAmount) {
          showNotification(`Minimum order of $${promo.minAmount} required for this promo`, 'error');
          return false;
        }
        dispatch({ type: ACTIONS.APPLY_PROMO, payload: code.toUpperCase() });
        showNotification(`Promo code applied: ${promo.description}`, 'success');
        return true;
      } else {
        showNotification('Invalid promo code', 'error');
        return false;
      }
    },
    
    removePromo: () => {
      dispatch({ type: ACTIONS.REMOVE_PROMO });
      showNotification('Promo code removed', 'info');
    },
    
    // Refresh listings function (can be called from other components)
    refreshListings: async (filters = null) => {
      await loadInitialProducts(filters);
    },
    
    // Other actions
    addToRecentlyViewed: (product) => {
      dispatch({ type: ACTIONS.ADD_TO_RECENTLY_VIEWED, payload: product });
    },
    
    setLoading: (loading) => {
      dispatch({ type: ACTIONS.SET_LOADING, payload: loading });
    }
  };

  const applyFiltersAndSearch = (query, filters, sortBy) => {
    let filtered = [...state.allProducts];

    // Apply search
    if (query) {
      filtered = filtered.filter(product =>
        product.title.toLowerCase().includes(query.toLowerCase()) ||
        product.description.toLowerCase().includes(query.toLowerCase()) ||
        product.category.toLowerCase().includes(query.toLowerCase()) ||
        product.features?.some(feature => feature.toLowerCase().includes(query.toLowerCase())) ||
        // Include add_info in search (but don't display it)
        (product.add_info && product.add_info.toLowerCase().includes(query.toLowerCase()))
      );
    }

    // Apply filters
    if (filters.type !== 'all') {
      filtered = filtered.filter(product => {
        const isBusinessSeller = product.seller?.is_business === true;
        if (filters.type === 'Business') {
          return isBusinessSeller;
        } else if (filters.type === 'Private') {
          return !isBusinessSeller;
        }
        return true;
      });
    }

    // Apply price range filter (from/to instead of array)
    if (filters.priceFrom !== undefined && filters.priceTo !== undefined) {
      filtered = filtered.filter(product => 
        product.price >= filters.priceFrom && product.price <= filters.priceTo
      );
    }

    // Removed condition filter

    if (filters.rating > 0) {
      filtered = filtered.filter(product => (product.rating || 0) >= filters.rating);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price_low':
          return a.price - b.price;
        case 'price_high':
          return b.price - a.price;
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        case 'popular':
          return (b.views || 0) - (a.views || 0);
        case 'newest':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

    dispatch({ type: ACTIONS.SET_FILTERED_PRODUCTS, payload: filtered });
  };

  const showNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toISOString()
    };
    
    dispatch({ type: ACTIONS.ADD_NOTIFICATION, payload: notification });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      dispatch({ type: ACTIONS.REMOVE_NOTIFICATION, payload: notification.id });
    }, 5000);
  };

  const value = {
    ...state,
    ...actions,
    showNotification
  };

  return (
    <MarketplaceContext.Provider value={value}>
      {children}
    </MarketplaceContext.Provider>
  );
}

// Custom hook to use marketplace context
export function useMarketplace() {
  const context = useContext(MarketplaceContext);
  if (!context) {
    throw new Error('useMarketplace must be used within a MarketplaceProvider');
  }
  return context;
}

export default MarketplaceContext;