/**
 * CATALORO - Ultra-Modern Categories Page
 * Beautiful category browsing with subcategories and trending items
 * Integrated with MarketplaceContext for real functionality
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import { 
  Smartphone, 
  Laptop, 
  Shirt, 
  Home, 
  Dumbbell, 
  Book, 
  Music, 
  Car, 
  Building, 
  Briefcase,
  TrendingUp,
  Users,
  Package,
  ArrowRight,
  Star,
  Eye,
  ChevronRight,
  ShoppingCart
} from 'lucide-react';

function CategoriesPage() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  // Use marketplace context for real data and functionality
  const {
    allProducts,
    setFilters,
    addToCart,
    showNotification
  } = useMarketplace();

  // Get real categories from products
  const getProductsByCategory = () => {
    const categoryMap = {};
    allProducts.forEach(product => {
      const category = product.category || 'Other';
      if (!categoryMap[category]) {
        categoryMap[category] = [];
      }
      categoryMap[category].push(product);
    });
    return categoryMap;
  };

  const productsByCategory = getProductsByCategory();

  // Filter categories to show available products
  const handleCategoryClick = (categoryName) => {
    setFilters({ category: categoryName });
    showNotification(`Browsing ${categoryName} category`, 'info');
  };

  const handleAddToCart = (product) => {
    addToCart(product);
  };

  const categories = [
    {
      id: 'electronics',
      name: 'Electronics',
      icon: Smartphone,
      color: 'from-blue-500 to-cyan-500',
      count: productsByCategory['Electronics']?.length || 0,
      trending: true,
      subcategories: ['Smartphones', 'Laptops', 'Tablets', 'Gaming', 'Audio', 'Cameras'],
      featuredProducts: productsByCategory['Electronics']?.slice(0, 2).map(product => ({
        name: product.title,
        price: product.price,
        image: product.images?.[0] || 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=200'
      })) || []
    },
    {
      id: 'fashion',
      name: 'Fashion',
      icon: Shirt,
      color: 'from-pink-500 to-rose-500',
      count: productsByCategory['Fashion']?.length || 0,
      trending: false,
      subcategories: ['Clothing', 'Shoes', 'Accessories', 'Bags', 'Jewelry', 'Watches'],
      featuredProducts: productsByCategory['Fashion']?.slice(0, 2).map(product => ({
        name: product.title,
        price: product.price,
        image: product.images?.[0] || 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=200'
      })) || []
    },
    {
      id: 'music',
      name: 'Music',
      icon: Music,
      color: 'from-purple-500 to-indigo-500',
      count: productsByCategory['Music']?.length || 0,
      trending: true,
      subcategories: ['Instruments', 'Audio Equipment', 'Records', 'Sheet Music'],
      featuredProducts: productsByCategory['Music']?.slice(0, 2).map(product => ({
        name: product.title,
        price: product.price,
        image: product.images?.[0] || 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=200'
      })) || []
    },
    {
      id: 'home',
      name: 'Home & Garden',
      icon: Home,
      color: 'from-green-500 to-emerald-500',
      count: 890,
      trending: false,
      subcategories: ['Furniture', 'Decor', 'Garden', 'Kitchen', 'Tools', 'Appliances'],
      featuredProducts: [
        { name: 'Modern Sofa', price: 899, image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=200' },
        { name: 'Coffee Table', price: 299, image: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=200' }
      ]
    }
  ];

  const trendingCategories = categories.filter(cat => cat.trending);
  const popularSubcategories = [
    'Smartphones', 'Laptops', 'Designer Bags', 'Gaming', 'Furniture', 
    'Fitness Equipment', 'Guitars', 'Sneakers', 'Home Decor', 'Audio Equipment'
  ];

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          Explore Categories
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Discover millions of products across all categories. From electronics to fashion, 
          find exactly what you're looking for.
        </p>
      </div>

      {/* Trending Categories Banner */}
      <div className="bg-gradient-to-r from-orange-400 via-pink-500 to-purple-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2 flex items-center">
              <TrendingUp className="w-8 h-8 mr-3" />
              Trending Now
            </h2>
            <p className="text-lg opacity-90">
              Hot categories with the most activity this week
            </p>
          </div>
          <div className="hidden md:flex space-x-4">
            {trendingCategories.slice(0, 3).map((category) => {
              const Icon = category.icon;
              return (
                <div key={category.id} className="text-center">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mb-2 backdrop-blur-sm">
                    <Icon className="w-8 h-8" />
                  </div>
                  <p className="text-sm font-medium">{category.name}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {categories.reduce((sum, cat) => sum + cat.count, 0).toLocaleString()}
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Total Products</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">{categories.length}</div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Categories</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {categories.reduce((sum, cat) => sum + cat.subcategories.length, 0)}
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Subcategories</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 text-center">
          <div className="text-3xl font-bold text-orange-600 mb-2">24/7</div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">New Listings</p>
        </div>
      </div>

      {/* Popular Subcategories */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Star className="w-6 h-6 mr-2 text-yellow-500" />
          Popular Right Now
        </h3>
        <div className="flex flex-wrap gap-2">
          {popularSubcategories.map((subcategory) => (
            <Link
              key={subcategory}
              to={`/browse?category=${encodeURIComponent(subcategory)}`}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-700 dark:hover:text-blue-300 transition-all duration-200 text-sm font-medium"
            >
              {subcategory}
            </Link>
          ))}
        </div>
      </div>

      {/* Main Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {categories.map((category) => {
          const Icon = category.icon;
          return (
            <div
              key={category.id}
              className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer"
              onClick={() => setSelectedCategory(selectedCategory === category.id ? null : category.id)}
            >
              {/* Category Header */}
              <div className={`bg-gradient-to-br ${category.color} p-6 text-white relative`}>
                <div className="flex items-center justify-between mb-4">
                  <Icon className="w-12 h-12" />
                  {category.trending && (
                    <span className="bg-white/20 text-white text-xs px-2 py-1 rounded-full font-medium backdrop-blur-sm">
                      Trending
                    </span>
                  )}
                </div>
                <h3 className="text-xl font-bold mb-2">{category.name}</h3>
                <div className="flex items-center justify-between">
                  <span className="text-white/90">{category.count.toLocaleString()} items</span>
                  <ChevronRight className={`w-5 h-5 transition-transform duration-300 ${
                    selectedCategory === category.id ? 'rotate-90' : ''
                  }`} />
                </div>
              </div>

              {/* Subcategories (Expandable) */}
              <div className={`transition-all duration-300 overflow-hidden ${
                selectedCategory === category.id ? 'max-h-96' : 'max-h-0'
              }`}>
                <div className="p-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Subcategories</h4>
                  <div className="space-y-2">
                    {category.subcategories.map((subcategory) => (
                      <Link
                        key={subcategory}
                        to={`/browse?category=${encodeURIComponent(subcategory)}`}
                        className="block text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors py-1"
                      >
                        • {subcategory}
                      </Link>
                    ))}
                  </div>
                  
                  {/* Featured Products */}
                  {category.featuredProducts && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Featured</h4>
                      <div className="space-y-3">
                        {category.featuredProducts.map((product) => (
                          <div key={product.name} className="flex items-center space-x-3">
                            <img
                              src={product.image}
                              alt={product.name}
                              className="w-12 h-12 object-cover rounded-lg"
                            />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {product.name}
                              </p>
                              <p className="text-sm text-blue-600 font-semibold">
                                ${product.price.toLocaleString()}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Browse Button */}
              <div className="p-4 pt-0">
                <button
                  onClick={() => {
                    handleCategoryClick(category.name);
                    // Navigate to browse page with category filter
                    window.location.href = `/browse?category=${encodeURIComponent(category.name)}`;
                  }}
                  className="w-full flex items-center justify-center space-x-2 bg-gray-100 dark:bg-gray-700 hover:bg-blue-100 dark:hover:bg-blue-900/30 text-gray-700 dark:text-gray-300 hover:text-blue-700 dark:hover:text-blue-300 py-3 rounded-lg transition-all duration-200 font-medium"
                >
                  <span>Browse {category.name}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Browse All Categories CTA */}
      <div className="text-center bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white">
        <h2 className="text-2xl font-bold mb-4">Can't find what you're looking for?</h2>
        <p className="text-lg mb-6 opacity-90">
          Browse all products or use our advanced search to find exactly what you need
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/browse"
            className="px-8 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-gray-100 transition-colors"
          >
            Browse All Products
          </Link>
          <Link
            to="/search"
            className="px-8 py-3 border border-white text-white rounded-xl font-semibold hover:bg-white/10 transition-colors"
          >
            Advanced Search
          </Link>
        </div>
      </div>
    </div>
  );
}

export default CategoriesPage;