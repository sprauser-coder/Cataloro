import React, { useState, useEffect } from 'react';
import { ChevronDown, Package, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';

const CategorySelector = ({ selectedCategory, onCategorySelect, required = false }) => {
  const [categories, setCategories] = useState([]);
  const [filteredCategories, setFilteredCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  // Default categories with icons and descriptions
  const defaultCategories = [
    {
      id: 'electronics',
      name: 'Electronics',
      icon: '📱',
      description: 'Phones, computers, gadgets, and tech accessories',
      subcategories: ['Mobile Phones', 'Laptops', 'Gaming', 'Audio', 'Smart Home', 'Cameras']
    },
    {
      id: 'fashion',
      name: 'Fashion & Clothing',
      icon: '👕',
      description: 'Clothing, shoes, accessories, and jewelry',
      subcategories: ['Men\'s Clothing', 'Women\'s Clothing', 'Shoes', 'Accessories', 'Jewelry', 'Bags']
    },
    {
      id: 'home-garden',
      name: 'Home & Garden',
      icon: '🏡',
      description: 'Furniture, home decor, appliances, and garden items',
      subcategories: ['Furniture', 'Home Decor', 'Kitchen', 'Garden', 'Tools', 'Lighting']
    },
    {
      id: 'sports',
      name: 'Sports & Fitness',
      icon: '⚽',
      description: 'Exercise equipment, sporting goods, and outdoor gear',
      subcategories: ['Fitness Equipment', 'Team Sports', 'Outdoor Activities', 'Water Sports', 'Winter Sports']
    },
    {
      id: 'books',
      name: 'Books & Media',
      icon: '📚',
      description: 'Books, magazines, movies, music, and educational materials',
      subcategories: ['Fiction', 'Non-Fiction', 'Textbooks', 'Movies', 'Music', 'Games']
    },
    {
      id: 'toys',
      name: 'Toys & Games',
      icon: '🧸',
      description: 'Children\'s toys, board games, and educational items',
      subcategories: ['Action Figures', 'Board Games', 'Educational', 'Outdoor Toys', 'Arts & Crafts']
    },
    {
      id: 'automotive',
      name: 'Automotive',
      icon: '🚗',
      description: 'Car parts, accessories, motorcycles, and vehicle maintenance',
      subcategories: ['Car Parts', 'Accessories', 'Motorcycles', 'Maintenance', 'GPS & Electronics']
    },
    {
      id: 'health-beauty',
      name: 'Health & Beauty',
      icon: '💄',
      description: 'Skincare, makeup, health supplements, and wellness products',
      subcategories: ['Skincare', 'Makeup', 'Hair Care', 'Health Supplements', 'Fitness']
    },
    {
      id: 'collectibles',
      name: 'Collectibles & Art',
      icon: '🎨',
      description: 'Antiques, collectibles, artwork, and vintage items',
      subcategories: ['Antiques', 'Coins', 'Stamps', 'Artwork', 'Vintage', 'Memorabilia']
    },
    {
      id: 'other',
      name: 'Other',
      icon: '📦',
      description: 'Items that don\'t fit into other categories',
      subcategories: ['Miscellaneous', 'Specialty Items']
    }
  ];

  useEffect(() => {
    // In a real app, this would fetch from API
    setCategories(defaultCategories);
    setFilteredCategories(defaultCategories);
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = categories.filter(category =>
        category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        category.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        category.subcategories.some(sub => sub.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredCategories(filtered);
    } else {
      setFilteredCategories(categories);
    }
  }, [searchTerm, categories]);

  const handleCategorySelect = (category) => {
    onCategorySelect(category);
    setShowDropdown(false);
    setSearchTerm('');
  };

  const selectedCategoryData = categories.find(cat => cat.id === selectedCategory);

  return (
    <div className="relative">
      <Card className="border-slate-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5 text-purple-600" />
            Category Selection
            {required && <span className="text-red-500">*</span>}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Selected Category Display */}
          {selectedCategoryData ? (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{selectedCategoryData.icon}</span>
                  <div>
                    <h4 className="font-medium text-slate-900">{selectedCategoryData.name}</h4>
                    <p className="text-sm text-slate-600">{selectedCategoryData.description}</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="border-purple-200 text-purple-600 hover:bg-purple-50"
                >
                  Change
                  <ChevronDown className="h-4 w-4 ml-2" />
                </Button>
              </div>
              
              {/* Subcategories */}
              {selectedCategoryData.subcategories.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-slate-500 mb-2">Popular subcategories:</p>
                  <div className="flex flex-wrap gap-1">
                    {selectedCategoryData.subcategories.slice(0, 4).map((sub, index) => (
                      <Badge key={index} variant="secondary" className="text-xs bg-white text-slate-600">
                        {sub}
                      </Badge>
                    ))}
                    {selectedCategoryData.subcategories.length > 4 && (
                      <Badge variant="secondary" className="text-xs bg-white text-slate-600">
                        +{selectedCategoryData.subcategories.length - 4} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Button
              variant="outline"
              onClick={() => setShowDropdown(!showDropdown)}
              className="w-full justify-between border-slate-200 text-slate-600 hover:bg-slate-50"
            >
              <span className="flex items-center gap-2">
                <Package className="h-4 w-4" />
                Select a category
              </span>
              <ChevronDown className="h-4 w-4" />
            </Button>
          )}

          {/* Category Dropdown */}
          {showDropdown && (
            <Card className="border border-slate-200 shadow-lg">
              <CardContent className="p-4">
                {/* Search */}
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                  <Input
                    placeholder="Search categories..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 border-slate-200"
                  />
                </div>

                {/* Categories Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                  {filteredCategories.map((category) => (
                    <div
                      key={category.id}
                      onClick={() => handleCategorySelect(category)}
                      className="p-3 border border-slate-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 cursor-pointer transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-xl">{category.icon}</span>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-slate-900 text-sm">{category.name}</h4>
                          <p className="text-xs text-slate-600 line-clamp-2">{category.description}</p>
                          {category.subcategories.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {category.subcategories.slice(0, 3).map((sub, index) => (
                                <Badge key={index} variant="secondary" className="text-xs bg-slate-100 text-slate-600">
                                  {sub}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {filteredCategories.length === 0 && (
                  <div className="text-center py-8 text-slate-500">
                    <Package className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No categories found matching "{searchTerm}"</p>
                  </div>
                )}

                {/* Close Button */}
                <div className="mt-4 pt-4 border-t border-slate-200">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setShowDropdown(false);
                      setSearchTerm('');
                    }}
                    className="w-full text-slate-600 hover:text-slate-800"
                  >
                    Close
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CategorySelector;