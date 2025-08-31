/**
 * CATALORO - Enhanced Create Listing Page with Cat Database Integration
 * Comprehensive form for creating new marketplace listings with catalyst autocomplete
 */

import React, { useState, useEffect } from 'react';
import { 
  Camera, 
  Upload, 
  X, 
  MapPin, 
  DollarSign, 
  Tag, 
  FileText, 
  Image as ImageIcon,
  Save,
  ArrowLeft,
  Plus,
  Trash2,
  CheckCircle,
  Database,
  Search,
  Zap
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';

function CreateListingPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    category: 'General', // Default category
    condition: 'New', // Default condition
    // Address fields for listing
    street: '',
    post_code: '',
    city: '',
    country: '',
    shipping: 'pickup',
    shipping_cost: '',
    tags: [],
    features: []
  });

  // Address from profile settings
  const [useProfileAddress, setUseProfileAddress] = useState(true); // Auto-activated checkbox
  const [profileAddress, setProfileAddress] = useState({
    street: '',
    post_code: '',
    city: '',
    country: ''
  });

  // Cat Database integration
  const [catalystData, setCatalystData] = useState([]);
  const [calculations, setCalculations] = useState([]);
  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedCatalyst, setSelectedCatalyst] = useState(null);
  const [loadingCatalysts, setLoadingCatalysts] = useState(false);

  // Location suggestions
  const [locationSuggestions, setLocationSuggestions] = useState([]);
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false);
  const [loadingLocations, setLoadingLocations] = useState(false);

  const [currentTag, setCurrentTag] = useState('');
  const [currentFeature, setCurrentFeature] = useState('');

  const categories = [
    'Catalysts', 'Electronics', 'Fashion & Clothing', 'Home & Garden', 'Sports & Outdoors', 
    'Books & Media', 'Music & Instruments', 'Automotive', 'Real Estate',
    'Jobs & Services', 'Collectibles & Antiques', 'Health & Beauty', 'Toys & Games'
  ];

  const conditions = [
    'New', 'Like New', 'Excellent', 'Good', 'Fair', 'For Parts'
  ];

  // Popular European cities and locations for suggestions
  const popularLocations = [
    // Germany
    'Berlin, Germany', 'Munich, Germany', 'Hamburg, Germany', 'Frankfurt, Germany', 'Cologne, Germany', 'Stuttgart, Germany', 'Düsseldorf, Germany', 'Dortmund, Germany', 'Essen, Germany', 'Bremen, Germany',
    
    // France  
    'Paris, France', 'Lyon, France', 'Marseille, France', 'Toulouse, France', 'Nice, France', 'Nantes, France', 'Strasbourg, France', 'Montpellier, France', 'Bordeaux, France', 'Lille, France',
    
    // Netherlands
    'Amsterdam, Netherlands', 'Rotterdam, Netherlands', 'The Hague, Netherlands', 'Utrecht, Netherlands', 'Eindhoven, Netherlands', 'Tilburg, Netherlands', 'Groningen, Netherlands', 'Almere, Netherlands',
    
    // Belgium
    'Brussels, Belgium', 'Antwerp, Belgium', 'Ghent, Belgium', 'Bruges, Belgium', 'Leuven, Belgium', 'Liège, Belgium',
    
    // Spain
    'Madrid, Spain', 'Barcelona, Spain', 'Valencia, Spain', 'Seville, Spain', 'Bilbao, Spain', 'Málaga, Spain', 'Zaragoza, Spain',
    
    // Italy
    'Rome, Italy', 'Milan, Italy', 'Naples, Italy', 'Turin, Italy', 'Palermo, Italy', 'Genoa, Italy', 'Bologna, Italy', 'Florence, Italy', 'Venice, Italy',
    
    // United Kingdom
    'London, UK', 'Birmingham, UK', 'Manchester, UK', 'Glasgow, UK', 'Liverpool, UK', 'Leeds, UK', 'Sheffield, UK', 'Edinburgh, UK', 'Bristol, UK', 'Cardiff, UK',
    
    // Other European cities
    'Vienna, Austria', 'Zurich, Switzerland', 'Geneva, Switzerland', 'Copenhagen, Denmark', 'Stockholm, Sweden', 'Oslo, Norway', 'Helsinki, Finland',
    'Prague, Czech Republic', 'Warsaw, Poland', 'Budapest, Hungary', 'Dublin, Ireland', 'Lisbon, Portugal', 'Athens, Greece'
  ];

  // Fetch Cat Database on component mount
  useEffect(() => {
    fetchCatalystData();
    fetchCalculations();
  }, []);

  const fetchCatalystData = async () => {
    try {
      setLoadingCatalysts(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/data`);
      if (response.ok) {
        const data = await response.json();
        setCatalystData(data);
        console.log('Loaded catalyst data:', data.length, 'entries');
        console.log('First catalyst structure:', data[0]); // Debug - check structure
        console.log('First catalyst add_info:', data[0]?.add_info); // Debug - check add_info
      }
    } catch (error) {
      console.error('Failed to fetch catalyst data:', error);
    } finally {
      setLoadingCatalysts(false);
    }
  };

  const fetchCalculations = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/calculations`);
      if (response.ok) {
        const data = await response.json();
        setCalculations(data);
        console.log('Loaded calculations:', data.length, 'entries');
        console.log('Sample calculation:', data[0]); // Debug: Check structure
      }
    } catch (error) {
      console.error('Failed to fetch calculations:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLocationChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({...prev, location: value}));

    if (value.length > 1) {
      // Filter popular locations based on input
      const filtered = popularLocations.filter(location => 
        location.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 8); // Limit to 8 suggestions

      setLocationSuggestions(filtered);
      setShowLocationSuggestions(filtered.length > 0);
    } else {
      setLocationSuggestions([]);
      setShowLocationSuggestions(false);
    }
  };

  const selectLocation = (location) => {
    setFormData(prev => ({...prev, location: location}));
    setShowLocationSuggestions(false);
    setLocationSuggestions([]);
  };

  const handleTitleChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({...prev, title: value}));

    if (value.length > 0) {
      // Filter catalyst data based on title input, name, cat_id, AND add_info
      const filtered = catalystData.filter(catalyst => {
        const searchTerm = value.toLowerCase();
        return (
          catalyst.name?.toLowerCase().includes(searchTerm) ||
          catalyst.cat_id?.toLowerCase().includes(searchTerm) ||
          catalyst.add_info?.toLowerCase().includes(searchTerm)
        );
      }).slice(0, 8); // Limit to 8 suggestions for better UX

      setFilteredSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setFilteredSuggestions([]);
      setShowSuggestions(false);
      setSelectedCatalyst(null);
    }
  };

  const selectCatalyst = (catalyst) => {
    setSelectedCatalyst(catalyst);
    
    console.log('Selected catalyst:', catalyst); // Debug
    console.log('Catalyst add_info:', catalyst.add_info); // Debug
    
    // Build description with add_info if available
    let description = `Catalyst: ${catalyst.name || 'Professional Grade Catalyst'}\n\nSpecifications:\n• Ceramic Weight: ${catalyst.ceramic_weight || 'N/A'}g\n\nProfessional grade catalyst suitable for automotive and industrial applications.`;
    
    if (catalyst.add_info && catalyst.add_info.trim()) {
      console.log('Adding add_info to description:', catalyst.add_info); // Debug
      description += `\n\nAdditional Information:\n${catalyst.add_info}`;
    } else {
      console.log('No add_info available or empty:', catalyst.add_info); // Debug
    }
    
    console.log('Final description:', description); // Debug
    
    setFormData(prev => ({
      ...prev, 
      title: catalyst.name || catalyst.cat_id,
      category: 'Catalysts',
      description: description
    }));
    setShowSuggestions(false);
  };

  const getCalculatedPrice = (catalystId) => {
    const calculation = calculations.find(calc => calc.cat_id === catalystId);
    console.log('Looking for price for catalyst:', catalystId, 'Found calculation:', calculation); // Debug
    return calculation?.total_price || null;
  };

  const getCalculatedPriceRange = (catalystId) => {
    const basePrice = getCalculatedPrice(catalystId);
    if (!basePrice) return null;
    
    const minPrice = basePrice * 0.9;
    const maxPrice = basePrice * 1.1;
    
    return {
      basePrice: parseFloat(basePrice),
      minPrice: parseFloat(minPrice.toFixed(2)),
      maxPrice: parseFloat(maxPrice.toFixed(2))
    };
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    
    files.forEach(file => {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select only image files');
        return;
      }

      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      // Add to images array
      setImages(prev => [...prev, file]);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreviews(prev => [...prev, e.target.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const addTag = () => {
    if (currentTag.trim() && !formData.tags.includes(currentTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, currentTag.trim()]
      }));
      setCurrentTag('');
    }
  };

  const removeTag = (tag) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const addFeature = () => {
    if (currentFeature.trim() && !formData.features.includes(currentFeature.trim())) {
      setFormData(prev => ({
        ...prev,
        features: [...prev.features, currentFeature.trim()]
      }));
      setCurrentFeature('');
    }
  };

  const removeFeature = (feature) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.filter(f => f !== feature)
    }));
  };

  const validateForm = () => {
    const required = ['title', 'description', 'price'];
    
    for (let field of required) {
      if (!formData[field].trim()) {
        alert(`Please fill in the ${field.replace('_', ' ')} field`);
        return false;
      }
    }

    if (parseFloat(formData.price) <= 0) {
      alert('Please enter a valid price');
      return false;
    }

    if (images.length === 0) {
      alert('Please add at least one image');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      // Get user data from localStorage
      const userData = localStorage.getItem('cataloro_user');
      const user = userData ? JSON.parse(userData) : null;

      if (!user) {
        alert('Please log in to create a listing');
        navigate('/login');
        return;
      }

      // Prepare listing data
      const listingData = {
        ...formData,
        price: parseFloat(formData.price),
        shipping_cost: formData.shipping_cost ? parseFloat(formData.shipping_cost) : 0,
        seller_id: user.id,
        seller: {
          name: user.name || user.email,
          email: user.email,
          verified: user.verified || false,
          location: formData.location || 'Not specified'
        },
        images: imagePreviews, // Use the base64 previews for demo
        created_at: new Date().toISOString(),
        // Include catalyst metadata if selected
        ...(selectedCatalyst && {
          catalyst_id: selectedCatalyst.cat_id,
          catalyst_name: selectedCatalyst.name,
          is_catalyst_listing: true,
          calculated_price: getCalculatedPrice(selectedCatalyst.cat_id),
          catalyst_specs: {
            ceramic_weight: selectedCatalyst.ceramic_weight,
            pt_ppm: selectedCatalyst.pt_ppm,
            pd_ppm: selectedCatalyst.pd_ppm,
            rh_ppm: selectedCatalyst.rh_ppm
          }
        })
      };

      // Create listing
      await marketplaceService.createListing(listingData);

      // Show success message
      alert('Listing created successfully!');

      // Navigate to my listings page
      navigate('/my-listings');

    } catch (error) {
      console.error('Failed to create listing:', error);
      alert('Failed to create listing. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <Link 
              to="/my-listings"
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Create New Listing</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Fill in the details below to create your marketplace listing
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Image Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <ImageIcon className="w-6 h-6 mr-2" />
              Product Images
            </h2>
            
            {/* Image Previews */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              {imagePreviews.map((preview, index) => (
                <div key={index} className="relative group">
                  <img 
                    src={preview} 
                    alt={`Preview ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg border-2 border-gray-200 dark:border-gray-600"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-2 right-2 p-1 bg-red-500 hover:bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
              
              {/* Upload Button */}
              <label className="w-full h-32 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                <Upload className="w-8 h-8 text-gray-400 mb-2" />
                <span className="text-sm text-gray-500 dark:text-gray-400 text-center">
                  Add Images
                </span>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </label>
            </div>
            
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Upload up to 8 images. First image will be the main photo. Max 5MB per image.
            </p>
          </div>

          {/* Basic Information */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <FileText className="w-6 h-6 mr-2" />
              Basic Information
            </h2>
            
            <div className="space-y-4">
              {/* Enhanced Title with Cat Database Integration */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title *
                  <span className="text-blue-600 dark:text-blue-400 text-xs ml-2 flex items-center">
                    <Database className="w-3 h-3 mr-1" />
                    (Type to search Cat Database - {catalystData.length} catalysts available)
                  </span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleTitleChange}
                  onFocus={() => formData.title && setShowSuggestions(filteredSuggestions.length > 0)}
                  placeholder="Enter item title or start typing catalyst name/ID..."
                  className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  required
                />
                
                {/* Catalyst Suggestions Dropdown */}
                {showSuggestions && (
                  <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl max-h-80 overflow-y-auto">
                    <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-b border-gray-200 dark:border-gray-600">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                        <Database className="w-4 h-4 mr-2 text-blue-500" />
                        Cat Database Matches ({filteredSuggestions.length})
                        <span className="ml-2 text-xs text-gray-500">Click to auto-fill</span>
                      </p>
                    </div>
                    {filteredSuggestions.map((catalyst) => {
                      const priceRange = getCalculatedPriceRange(catalyst.cat_id);
                      return (
                        <div
                          key={catalyst.cat_id}
                          onClick={() => selectCatalyst(catalyst)}
                          className="p-4 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-all duration-200 group"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <span className="font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                  {catalyst.name}
                                </span>
                                <Zap className="w-4 h-4 text-yellow-500" title="Auto-fill enabled" />
                              </div>
                              <div className="text-xs text-gray-600 dark:text-gray-400">
                                <div className="flex flex-col">
                                  <span className="text-gray-500">Weight</span>
                                  <span className="font-medium">{catalyst.ceramic_weight}g</span>
                                </div>
                              </div>
                            </div>
                            {priceRange && (
                              <div className="ml-4 text-right">
                                <div className="text-sm font-bold text-green-600 dark:text-green-400">
                                  €{priceRange.minPrice.toFixed(2)} - €{priceRange.maxPrice.toFixed(2)}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                                  <Database className="w-3 h-3 mr-1" />
                                  Market Range
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Enhanced Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description *
                  {selectedCatalyst && (
                    <span className="text-purple-600 dark:text-purple-400 text-xs ml-2 flex items-center">
                      <Zap className="w-3 h-3 mr-1" />
                      Auto-generated from catalyst specifications
                    </span>
                  )}
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Provide a detailed description of your item..."
                  rows={selectedCatalyst ? 8 : 4}
                  className={`w-full px-4 py-3 border-2 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 transition-all duration-200 ${
                    selectedCatalyst 
                      ? 'border-purple-300 dark:border-purple-600 focus:border-purple-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-blue-500'
                  }`}
                  required
                />
                {selectedCatalyst && (
                  <p className="text-xs text-purple-600 dark:text-purple-400 mt-2 flex items-center">
                    <Database className="w-3 h-3 mr-1" />
                    Description includes catalyst specifications and current market information
                  </p>
                )}
              </div>

              {/* Price and Category Row - Enhanced */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Price * (€)
                    {selectedCatalyst && (
                      <span className="text-green-600 dark:text-green-400 text-xs ml-2 flex items-center">
                        <Zap className="w-3 h-3 mr-1" />
                        Auto-calculated from catalyst data
                      </span>
                    )}
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 text-lg">
                      €
                    </span>
                    <input
                      type="number"
                      name="price"
                      value={formData.price}
                      onChange={handleInputChange}
                      placeholder="0.00"
                      min="0"
                      step="0.01"
                      className={`w-full pl-10 pr-4 py-3 border-2 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all duration-200 ${
                        selectedCatalyst 
                          ? 'border-green-300 dark:border-green-600 focus:border-green-500' 
                          : 'border-gray-300 dark:border-gray-600 focus:border-blue-500'
                      }`}
                      required
                    />
                    {selectedCatalyst && (
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded text-xs font-medium">
                          Auto-filled
                        </span>
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {/* Selected Catalyst Summary */}
              {selectedCatalyst && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl p-6 mt-6">
                  <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-4 flex items-center text-lg">
                    <Database className="w-5 h-5 mr-2" />
                    Selected Catalyst: {selectedCatalyst.name}
                    <span className="ml-3 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                      Auto-filled
                    </span>
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                      <span className="text-gray-600 dark:text-gray-400 text-sm block mb-1">Catalyst Name</span>
                      <p className="font-bold text-gray-900 dark:text-white text-lg">{selectedCatalyst.name}</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                      <span className="text-gray-600 dark:text-gray-400 text-sm block mb-1">Ceramic Weight</span>
                      <p className="font-bold text-gray-900 dark:text-white text-lg">{selectedCatalyst.ceramic_weight}g</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                      <span className="text-gray-600 dark:text-gray-400 text-sm block mb-1">Market Range</span>
                      <p className="font-bold text-green-600 dark:text-green-400 text-lg">
                        {getCalculatedPriceRange(selectedCatalyst.cat_id) ? (
                          <>
                            €{getCalculatedPriceRange(selectedCatalyst.cat_id).minPrice.toFixed(2)} - €{getCalculatedPriceRange(selectedCatalyst.cat_id).maxPrice.toFixed(2)}
                          </>
                        ) : 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <p className="text-blue-800 dark:text-blue-200 text-sm">
                      <strong>Auto-filled fields:</strong> Title, Category, Price, and Description have been automatically populated based on this catalyst's data and current market calculations.
                    </p>
                  </div>
                </div>
              )}

              {/* Location Row with Suggestions */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Location
                  <span className="text-blue-600 dark:text-blue-400 text-xs ml-2">
                    (Type to search popular cities)
                  </span>
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleLocationChange}
                    onFocus={() => formData.location && setShowLocationSuggestions(locationSuggestions.length > 0)}
                    placeholder="Start typing city name (e.g., Amsterdam, Berlin, Paris...)"
                    className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  />
                </div>
                
                {/* Location Suggestions Dropdown */}
                {showLocationSuggestions && (
                  <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl max-h-60 overflow-y-auto">
                    <div className="p-3 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border-b border-gray-200 dark:border-gray-600">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                        <MapPin className="w-4 h-4 mr-2 text-green-500" />
                        Popular Locations ({locationSuggestions.length})
                        <span className="ml-2 text-xs text-gray-500">Click to select</span>
                      </p>
                    </div>
                    {locationSuggestions.map((location, index) => {
                      const [city, country] = location.split(', ');
                      return (
                        <div
                          key={index}
                          onClick={() => selectLocation(location)}
                          className="p-4 hover:bg-green-50 dark:hover:bg-green-900/20 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-all duration-200 group"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                              {city.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-gray-900 dark:text-white group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                                {city}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                {country}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Shipping Information */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Shipping & Delivery
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Shipping Options
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="shipping"
                      value="pickup"
                      checked={formData.shipping === 'pickup'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    <span className="text-gray-700 dark:text-gray-300">Local pickup only</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="shipping"
                      value="shipping"
                      checked={formData.shipping === 'shipping'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    <span className="text-gray-700 dark:text-gray-300">I can ship this item</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="shipping"
                      value="both"
                      checked={formData.shipping === 'both'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    <span className="text-gray-700 dark:text-gray-300">Both pickup and shipping</span>
                  </label>
                </div>
              </div>

              {(formData.shipping === 'shipping' || formData.shipping === 'both') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Shipping Cost (€)
                  </label>
                  <input
                    type="number"
                    name="shipping_cost"
                    value={formData.shipping_cost}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Tags and Features */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Tag className="w-6 h-6 mr-2" />
              Tags & Features
            </h2>
            
            <div className="space-y-6">
              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tags (Optional)
                </label>
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="text"
                    value={currentTag}
                    onChange={(e) => setCurrentTag(e.target.value)}
                    placeholder="Add a tag"
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  />
                  <button
                    type="button"
                    onClick={addTag}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-2 text-blue-600 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-100"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Features */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Key Features (Optional)
                </label>
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="text"
                    value={currentFeature}
                    onChange={(e) => setCurrentFeature(e.target.value)}
                    placeholder="Add a feature"
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFeature())}
                  />
                  <button
                    type="button"
                    onClick={addFeature}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
                <div className="space-y-2">
                  {formData.features.map((feature, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800"
                    >
                      <span className="text-green-800 dark:text-green-200">{feature}</span>
                      <button
                        type="button"
                        onClick={() => removeFeature(feature)}
                        className="text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Submit Section */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Ready to publish your listing?</h3>
                <p className="text-blue-100">
                  Review all information above and click create to publish your listing to the marketplace.
                </p>
              </div>
              <div className="flex space-x-4">
                <Link
                  to="/my-listings"
                  className="px-6 py-3 bg-white/20 hover:bg-white/30 text-white rounded-lg font-medium transition-colors"
                >
                  Cancel
                </Link>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-8 py-3 bg-white/20 hover:bg-white/30 disabled:bg-white/10 text-white rounded-lg font-semibold transition-colors flex items-center space-x-2 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      <span>Create Listing</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateListingPage;