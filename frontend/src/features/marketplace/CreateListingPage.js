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
  Zap,
  User,
  Clock,
  AlertTriangle,
  TrendingUp
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { usePermissions } from '../../hooks/usePermissions';

function CreateListingPage() {
  const navigate = useNavigate();
  const permissions = usePermissions();
  
  // Safety check for permissions
  const isAdminOrManager = permissions?.userRole === 'Admin' || permissions?.userRole === 'Admin-Manager' || permissions?.ui?.showAdminPanelLink || false;
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSavingDraft, setIsSavingDraft] = useState(false);
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
    features: [],
    // Time limit functionality
    has_time_limit: false,
    time_limit_hours: 24,
    // Partners functionality
    show_partners_first: false,
    partners_visibility_hours: 24
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
  const [unifiedCalculations, setUnifiedCalculations] = useState([]);
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

  // Fetch Cat Database on component mount and load profile address
  useEffect(() => {
    // Fetch catalyst data for all authenticated users (buyers and sellers)
    fetchUnifiedCalculations(); // Use unified endpoint - now available to all users
    loadProfileAddress();
  }, []);
  
  // Debug permissions and state
  useEffect(() => {
    console.log('CreateListingPage - Debug Info:');
    console.log('  permissions:', permissions);
    console.log('  permissions.ui:', permissions?.ui);
    console.log('  permissions.ui.showAdminPanelLink:', permissions?.ui?.showAdminPanelLink);
    console.log('  isAdminOrManager:', isAdminOrManager);
    console.log('  selectedCatalyst:', selectedCatalyst);
    console.log('  unifiedCalculations length:', unifiedCalculations.length);
  }, [permissions, isAdminOrManager, selectedCatalyst, unifiedCalculations]);

  const loadProfileAddress = () => {
    try {
      const userData = localStorage.getItem('cataloro_user');
      if (userData) {
        const user = JSON.parse(userData);
        const address = {
          street: user.street || '',
          post_code: user.post_code || '',
          city: user.city || '',
          country: user.country || ''
        };
        setProfileAddress(address);
        
        // If checkbox is checked and profile has address data, use it
        if (useProfileAddress && (address.street || address.city)) {
          setFormData(prev => ({
            ...prev,
            street: address.street,
            post_code: address.post_code,
            city: address.city,
            country: address.country
          }));
        }
      }
    } catch (error) {
      console.error('Failed to load profile address:', error);
    }
  };

  const fetchCatalystData = async () => {
    try {
      setLoadingCatalysts(true);
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/data`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCatalystData(data);
        console.log('Loaded catalyst data:', data.length, 'entries');
        console.log('First catalyst structure:', data[0]); // Debug - check structure
        console.log('First catalyst add_info:', data[0]?.add_info); // Debug - check add_info
      } else {
        console.error('❌ Failed to fetch catalyst data - Status:', response.status);
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

  const fetchUnifiedCalculations = async () => {
    try {
      setLoadingCatalysts(true);
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/unified-calculations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUnifiedCalculations(data);
        console.log('Loaded unified calculations:', data.length, 'entries');
        console.log('Sample unified calculation:', data[0]);
      } else {
        console.error('Failed to fetch unified calculations - Status:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch unified calculations:', error);
    } finally {
      setLoadingCatalysts(false);
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

  const handleUseProfileAddressChange = (checked) => {
    setUseProfileAddress(checked);
    
    if (checked) {
      // Use profile address
      setFormData(prev => ({
        ...prev,
        street: profileAddress.street,
        post_code: profileAddress.post_code,
        city: profileAddress.city,
        country: profileAddress.country
      }));
    } else {
      // Clear address fields for manual input
      setFormData(prev => ({
        ...prev,
        street: '',
        post_code: '',
        city: '',
        country: ''
      }));
    }
  };

  const handleTitleChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({...prev, title: value}));

    if (value.length > 0) {
      // Filter unified calculations based on title input, name, cat_id, and additional info
      const filtered = unifiedCalculations.filter(catalyst => {
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
    
    // Build description with additional info from catalyst database (not content values)  
    let description = `Catalyst: ${catalyst.name || 'Professional Grade Catalyst'}\n\nSpecifications:\n• Weight: ${catalyst.weight || 'N/A'}g\n\nProfessional grade catalyst suitable for automotive and industrial applications.`;
    
    // Add additional info if available from the catalyst database
    if (catalyst.add_info && catalyst.add_info.trim()) {
      description += `\n\nAdditional Information:\n${catalyst.add_info}`;
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
    const calculation = unifiedCalculations.find(calc => calc.cat_id === catalystId);
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

  const handleSaveDraft = async () => {
    setIsSavingDraft(true);

    try {
      // Get user data from localStorage
      const userData = localStorage.getItem('cataloro_user');
      const user = userData ? JSON.parse(userData) : null;

      if (!user) {
        alert('Please log in to save draft');
        navigate('/login');
        return;
      }

      // Prepare draft data
      const draftData = {
        ...formData,
        price: formData.price ? parseFloat(formData.price) : 0,
        shipping_cost: formData.shipping_cost ? parseFloat(formData.shipping_cost) : 0,
        seller_id: user.id,
        seller: {
          name: user.name || user.full_name || user.email,
          username: user.username || user.name || user.email,
          email: user.email,
          verified: user.verified || false,
          is_business: user.is_business || false,
          company_name: user.company_name || null,
          location: [formData.street, formData.city, formData.country].filter(Boolean).join(', ') || 'Not specified'
        },
        address: {
          street: formData.street,
          post_code: formData.post_code,
          city: formData.city,
          country: formData.country,
          use_profile_address: useProfileAddress
        },
        images: imagePreviews,
        created_at: new Date().toISOString(),
        status: 'draft', // Mark as draft
        is_draft: true,
        // Include comprehensive catalyst data from unified calculations (Admin/Admin-Manager only)
        ...(selectedCatalyst && {
          catalyst_id: selectedCatalyst.cat_id,
          catalyst_name: selectedCatalyst.name,
          is_catalyst_listing: true,
          calculated_price: selectedCatalyst.total_price,
          // Weight data
          ceramic_weight: selectedCatalyst.weight,
          // Content calculations (Pt g, Pd g, Rh g)
          pt_g: selectedCatalyst.pt_g,
          pd_g: selectedCatalyst.pd_g, 
          rh_g: selectedCatalyst.rh_g,
          // Store comprehensive catalyst specs for inventory management
          catalyst_specs: {
            weight: selectedCatalyst.weight,
            total_price: selectedCatalyst.total_price,
            pt_g: selectedCatalyst.pt_g,
            pd_g: selectedCatalyst.pd_g,
            rh_g: selectedCatalyst.rh_g,
            is_override: selectedCatalyst.is_override
          }
        })
      };

      // Save as draft
      await marketplaceService.createListing(draftData);

      // Show success message
      alert('Draft saved successfully! You can finish it later from My Listings.');

      // Navigate to my listings page
      navigate('/my-listings');

    } catch (error) {
      console.error('Failed to save draft:', error);
      alert('Failed to save draft. Please try again.');
    } finally {
      setIsSavingDraft(false);
    }
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
          name: user.name || user.full_name || user.email,
          username: user.username || user.name || user.email,
          email: user.email,
          verified: user.verified || false,
          is_business: user.is_business || false, // Include business account status
          company_name: user.company_name || null,
          // Format address for seller display
          location: [formData.street, formData.city, formData.country].filter(Boolean).join(', ') || 'Not specified'
        },
        // Store detailed address information
        address: {
          street: formData.street,
          post_code: formData.post_code,
          city: formData.city,
          country: formData.country,
          use_profile_address: useProfileAddress
        },
        images: imagePreviews, // Use the base64 previews for demo
        created_at: new Date().toISOString(),
        // Time limit functionality
        has_time_limit: formData.has_time_limit,
        time_limit_hours: formData.has_time_limit ? formData.time_limit_hours : null,
        // Partners functionality
        show_partners_first: formData.show_partners_first,
        partners_visibility_hours: formData.show_partners_first ? formData.partners_visibility_hours : null,
        // Include comprehensive catalyst data from unified calculations (Admin/Admin-Manager only)
        ...(selectedCatalyst && {
          catalyst_id: selectedCatalyst.cat_id,
          catalyst_name: selectedCatalyst.name,
          is_catalyst_listing: true,
          calculated_price: selectedCatalyst.total_price,
          // Weight data
          ceramic_weight: selectedCatalyst.weight,
          // Content calculations (Pt g, Pd g, Rh g)
          pt_g: selectedCatalyst.pt_g,
          pd_g: selectedCatalyst.pd_g, 
          rh_g: selectedCatalyst.rh_g,
          // Store comprehensive catalyst specs for inventory management
          catalyst_specs: {
            weight: selectedCatalyst.weight,
            total_price: selectedCatalyst.total_price,
            pt_g: selectedCatalyst.pt_g,
            pd_g: selectedCatalyst.pd_g,
            rh_g: selectedCatalyst.rh_g,
            is_override: selectedCatalyst.is_override
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
                    (Type to search Cat Database - {unifiedCalculations.length} catalysts available)
                  </span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleTitleChange}
                  onFocus={() => formData.title && setShowSuggestions(filteredSuggestions.length > 0)}
                  placeholder="Enter item title or search catalyst name/ID/additional info..."
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
                    
                    {/* Option for Catalyst not in Database - moved to bottom */}
                    {filteredSuggestions.length > 0 && (
                      <div
                        onClick={() => {
                          setSelectedCatalyst(null);
                          setShowSuggestions(false);
                          // Clear any auto-filled data and enable free input
                          setFormData(prev => ({
                            ...prev,
                            // Keep the title as is
                            description: '',
                            price: '',
                            category: 'General'
                          }));
                        }}
                        className="p-4 hover:bg-orange-50 dark:hover:bg-orange-900/20 cursor-pointer border-t border-gray-200 dark:border-gray-600 transition-all duration-200 group"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className="font-semibold text-orange-600 dark:text-orange-400 group-hover:text-orange-700 dark:group-hover:text-orange-300 transition-colors">
                                🆓 Catalyst not in Database
                              </span>
                              <Plus className="w-4 h-4 text-orange-500" title="Create free listing" />
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-400">
                              Create a free listing with custom price and description
                            </div>
                          </div>
                          <div className="ml-4 text-right">
                            <div className="text-sm font-bold text-orange-600 dark:text-orange-400">
                              Custom Input
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* Show the "Catalyst not in Database" option if no matches found */}
                    {filteredSuggestions.length === 0 && formData.title.length > 2 && (
                      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                        <p className="mb-3">No catalysts found matching "{formData.title}"</p>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedCatalyst(null);
                            setShowSuggestions(false);
                            // Enable free input mode
                            setFormData(prev => ({
                              ...prev,
                              category: 'General'
                            }));
                          }}
                          className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors flex items-center space-x-2 mx-auto"
                        >
                          <Plus className="w-4 h-4" />
                          <span>Create Free Listing</span>
                        </button>
                      </div>
                    )}
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
                    Starting Price * (€)
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
                      <p className="font-bold text-gray-900 dark:text-white text-lg">{selectedCatalyst.weight}g</p>
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

              {/* Catalyst Content Preview - Show Pt g, Pd g, Rh g values when catalyst is selected */}
              {selectedCatalyst && (
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
                  <div className="flex items-center space-x-2 mb-4">
                    <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                    <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">Selected Catalyst Content</h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      Preview
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-green-100 dark:border-green-800">
                      <div className="text-xs text-gray-600 dark:text-gray-400 uppercase font-medium mb-1">Weight</div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">{selectedCatalyst.weight || 0}g</div>
                    </div>
                    
                    <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-green-100 dark:border-green-800">
                      <div className="text-xs text-blue-600 dark:text-blue-400 uppercase font-medium mb-1">Pt g</div>
                      <div className="text-lg font-bold text-blue-600 dark:text-blue-400">{(selectedCatalyst.pt_g || 0).toFixed(4)}</div>
                    </div>
                    
                    <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-green-100 dark:border-green-800">
                      <div className="text-xs text-green-600 dark:text-green-400 uppercase font-medium mb-1">Pd g</div>
                      <div className="text-lg font-bold text-green-600 dark:text-green-400">{(selectedCatalyst.pd_g || 0).toFixed(4)}</div>
                    </div>
                    
                    <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-green-100 dark:border-green-800">
                      <div className="text-xs text-purple-600 dark:text-purple-400 uppercase font-medium mb-1">Rh g</div>
                      <div className="text-lg font-bold text-purple-600 dark:text-purple-400">{(selectedCatalyst.rh_g || 0).toFixed(4)}</div>
                    </div>
                  </div>
                  
                  <div className="mt-4 text-xs text-green-600 dark:text-green-400 flex items-center">
                    <Database className="w-4 h-4 mr-1" />
                    Content values from unified catalyst calculations - will be saved with your listing
                  </div>
                </div>
              )}

              {/* Address Section with Profile Settings Integration */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-md font-semibold text-gray-900 dark:text-white flex items-center">
                    <MapPin className="w-4 h-4 mr-2" />
                    Address Information
                  </h4>
                  
                  {/* Profile Address Checkbox */}
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useProfileAddress}
                      onChange={(e) => handleUseProfileAddressChange(e.target.checked)}
                      style={{
                        appearance: 'none',
                        width: '18px',
                        height: '18px',
                        backgroundColor: '#f3f4f6',
                        border: '2px solid #6b7280',
                        borderRadius: '4px',
                        position: 'relative',
                        cursor: 'pointer',
                        outline: 'none'
                      }}
                      onMouseOver={(e) => {
                        e.target.style.backgroundColor = '#e5e7eb';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.backgroundColor = useProfileAddress ? '#2563eb' : '#f3f4f6';
                      }}
                      onClick={(e) => {
                        // Force visual update
                        setTimeout(() => {
                          e.target.style.backgroundColor = e.target.checked ? '#2563eb' : '#f3f4f6';
                          e.target.style.backgroundImage = e.target.checked ? 
                            `url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e")` : 
                            'none';
                          e.target.style.backgroundSize = '12px 12px';
                          e.target.style.backgroundPosition = 'center';
                          e.target.style.backgroundRepeat = 'no-repeat';
                        }, 10);
                      }}
                      ref={(el) => {
                        if (el) {
                          el.style.backgroundColor = useProfileAddress ? '#2563eb' : '#f3f4f6';
                          el.style.backgroundImage = useProfileAddress ? 
                            `url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e")` : 
                            'none';
                          el.style.backgroundSize = '12px 12px';
                          el.style.backgroundPosition = 'center';
                          el.style.backgroundRepeat = 'no-repeat';
                        }
                      }}
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300 flex items-center">
                      <User className="w-3 h-3 mr-1" />
                      Use profile address
                    </span>
                  </label>
                </div>

                {useProfileAddress ? (
                  /* Profile Address Display */
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg mr-3">
                        <User className="w-4 h-4 text-blue-600 dark:text-blue-300" />
                      </div>
                      <div>
                        <h5 className="font-medium text-blue-900 dark:text-blue-100">Using Profile Address</h5>
                        <p className="text-sm text-blue-600 dark:text-blue-300">Address from your profile settings</p>
                      </div>
                    </div>
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-blue-100 dark:border-blue-700">
                      {profileAddress.street || profileAddress.city ? (
                        <div className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
                          {profileAddress.street && <div>{profileAddress.street}</div>}
                          <div className="flex space-x-2">
                            {profileAddress.post_code && <span>{profileAddress.post_code}</span>}
                            {profileAddress.city && <span>{profileAddress.city}</span>}
                          </div>
                          {profileAddress.country && <div>{profileAddress.country}</div>}
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500 dark:text-gray-400 italic">
                          No address in profile. Please uncheck to enter address manually.
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  /* Manual Address Input Fields */
                  <div className="space-y-4 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg mr-3">
                        <MapPin className="w-4 h-4 text-green-600 dark:text-green-300" />
                      </div>
                      <div>
                        <h5 className="font-medium text-green-900 dark:text-green-100">Custom Address</h5>
                        <p className="text-sm text-green-600 dark:text-green-300">Enter address for this listing</p>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Street Address
                      </label>
                      <input
                        type="text"
                        name="street"
                        value={formData.street}
                        onChange={handleInputChange}
                        placeholder="Enter street address"
                        className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Post Code
                        </label>
                        <input
                          type="text"
                          name="post_code"
                          value={formData.post_code}
                          onChange={handleInputChange}
                          placeholder="Postal/ZIP code"
                          className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          City
                        </label>
                        <input
                          type="text"
                          name="city"
                          value={formData.city}
                          onChange={handleInputChange}
                          placeholder="Enter city"
                          className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Country
                      </label>
                      <input
                        type="text"
                        name="country"
                        value={formData.country}
                        onChange={handleInputChange}
                        placeholder="Enter country"
                        className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>




          {/* Time Limit Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Clock className="w-6 h-6 mr-2" />
              Time Limit (Optional)
            </h2>
            
            <div className="space-y-6">
              {/* Enable Time Limit Toggle */}
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="has_time_limit"
                  name="has_time_limit"
                  checked={formData.has_time_limit}
                  onChange={(e) => setFormData({...formData, has_time_limit: e.target.checked})}
                  style={{
                    appearance: 'none',
                    width: '20px',
                    height: '20px',
                    backgroundColor: '#f3f4f6',
                    border: '2px solid #6b7280',
                    borderRadius: '4px',
                    position: 'relative',
                    cursor: 'pointer',
                    outline: 'none'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = '#e5e7eb';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = formData.has_time_limit ? '#2563eb' : '#f3f4f6';
                  }}
                  onClick={(e) => {
                    // Force visual update
                    setTimeout(() => {
                      e.target.style.backgroundColor = e.target.checked ? '#2563eb' : '#f3f4f6';
                      e.target.style.backgroundImage = e.target.checked ? 
                        `url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e")` : 
                        'none';
                      e.target.style.backgroundSize = '14px 14px';
                      e.target.style.backgroundPosition = 'center';
                      e.target.style.backgroundRepeat = 'no-repeat';
                    }, 10);
                  }}
                  ref={(el) => {
                    if (el) {
                      el.style.backgroundColor = formData.has_time_limit ? '#2563eb' : '#f3f4f6';
                      el.style.backgroundImage = formData.has_time_limit ? 
                        `url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e")` : 
                        'none';
                      el.style.backgroundSize = '14px 14px';
                      el.style.backgroundPosition = 'center';
                      el.style.backgroundRepeat = 'no-repeat';
                    }
                  }}
                />
                <label htmlFor="has_time_limit" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Set a time limit for this listing
                </label>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Add urgency to your listing! When time runs out, the highest bidder automatically wins.
              </p>

              {formData.has_time_limit && (
                <div className="space-y-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                  {/* Duration Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Duration
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { value: 1, label: '1 Hour', desc: '1 hour' },
                        { value: 24, label: '24 Hours', desc: '1 day' },
                        { value: 48, label: '48 Hours', desc: '2 days' },
                        { value: 168, label: '1 Week', desc: '7 days' },
                        { value: 720, label: '1 Month', desc: '30 days' }
                      ].map((option) => (
                        <label key={option.value} className="relative">
                          <input
                            type="radio"
                            name="time_limit_hours"
                            value={option.value}
                            checked={formData.time_limit_hours === option.value}
                            onChange={(e) => setFormData({...formData, time_limit_hours: parseInt(e.target.value)})}
                            className="sr-only"
                          />
                          <div className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                            formData.time_limit_hours === option.value
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                          }`}>
                            <div className="text-center">
                              <div className="font-semibold text-sm">{option.label}</div>
                              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{option.desc}</div>
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Preview */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Preview</h4>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Your listing will expire in <span className="font-mono text-blue-600 dark:text-blue-400">
                        {formData.time_limit_hours === 1 ? '1 hour' :
                         formData.time_limit_hours === 24 ? '1 day' : 
                         formData.time_limit_hours === 48 ? '2 days' :
                         formData.time_limit_hours === 168 ? '1 week' : '1 month'}
                      </span> after publication.
                      <br />
                      The countdown timer will appear as a <span className="font-medium">separate badge below the market range</span> of your listing image.
                    </div>
                  </div>

                  {/* Warning */}
                  <div className="flex items-start space-x-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" />
                    <div className="text-sm text-amber-700 dark:text-amber-300">
                      <strong>Important:</strong> When your listing expires, the highest bidder at that moment will automatically win, regardless of how many bids were placed. You can extend the time limit later if needed.
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Partners First Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <User className="w-6 h-6 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Partner Preview</h3>
            </div>
            
            <div className="space-y-6">
              {/* Enable Partners First Toggle */}
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="show_partners_first"
                  name="show_partners_first"
                  checked={formData.show_partners_first}
                  onChange={(e) => setFormData({...formData, show_partners_first: e.target.checked})}
                  style={{
                    appearance: 'none',
                    width: '20px',
                    height: '20px',
                    backgroundColor: '#f3f4f6',
                    border: '2px solid #6b7280',
                    borderRadius: '4px',
                    position: 'relative',
                    cursor: 'pointer',
                    outline: 'none'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = '#e5e7eb';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = formData.show_partners_first ? '#9333ea' : '#f3f4f6';
                  }}
                  onClick={(e) => {
                    // Force visual update
                    setTimeout(() => {
                      e.target.style.backgroundColor = e.target.checked ? '#9333ea' : '#f3f4f6';
                      e.target.style.backgroundImage = e.target.checked ? 
                        `url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e")` : 
                        'none';
                      e.target.style.backgroundSize = '14px 14px';
                      e.target.style.backgroundPosition = 'center';
                      e.target.style.backgroundRepeat = 'no-repeat';
                    }, 10);
                  }}
                  ref={(el) => {
                    if (el) {
                      el.style.backgroundColor = formData.show_partners_first ? '#9333ea' : '#f3f4f6';
                      el.style.backgroundImage = formData.show_partners_first ? 
                        `url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e")` : 
                        'none';
                      el.style.backgroundSize = '14px 14px';
                      el.style.backgroundPosition = 'center';
                      el.style.backgroundRepeat = 'no-repeat';
                    }
                  }}
                />
                <label htmlFor="show_partners_first" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Show Partners First
                </label>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Give your preferred partners exclusive early access to your listing before it becomes public.
              </p>

              {formData.show_partners_first && (
                <div className="space-y-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  {/* Duration Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Partner Preview Duration
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { label: '1 Minute', value: 1/60 },
                        { label: '1 Day', value: 24 },
                        { label: '2 Days', value: 48 },
                        { label: '1 Week', value: 168 }
                      ].map((option) => (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => setFormData({...formData, partners_visibility_hours: option.value})}
                          className={`p-3 rounded-lg border-2 text-center transition-colors ${
                            formData.partners_visibility_hours === option.value
                              ? 'border-purple-500 bg-purple-500 text-white'
                              : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-purple-300'
                          }`}
                        >
                          <div className="font-medium">{option.label}</div>
                          <div className="text-xs opacity-75">{option.value}h</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Preview Info */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Your listing will be visible only to your partners for <span className="font-mono text-purple-600 dark:text-purple-400">
                        {formData.partners_visibility_hours === 24 ? '1 day' : 
                         formData.partners_visibility_hours === 48 ? '2 days' :
                         formData.partners_visibility_hours === 168 ? '1 week' : `${formData.partners_visibility_hours} hours`}
                      </span> after publication.
                      <br />
                      After this period, it will become visible to all users. Partners can place offers during the exclusive period.
                    </div>
                  </div>

                  {/* Info */}
                  <div className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <User className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                    <div className="text-sm text-blue-700 dark:text-blue-300">
                      <strong>Note:</strong> You can manage your preferred partners in Profile Settings &gt; Partners. Partners will be notified when you post listings with early access enabled.
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>


          {/* Submit Section - Redesigned */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 shadow-sm">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Ready to publish your listing?</h3>
              <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                Review all information above and choose how you'd like to proceed with your listing.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-2xl mx-auto">
              {/* Cancel Button */}
              <Link
                to="/browse"
                className="w-full sm:w-auto px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg font-medium transition-all duration-200 text-center flex items-center justify-center space-x-2 group"
              >
                <X className="w-4 h-4 group-hover:rotate-90 transition-transform duration-200" />
                <span>Cancel</span>
              </Link>
              
              {/* Save as Draft Button */}
              <button
                type="button"
                onClick={handleSaveDraft}
                disabled={isSavingDraft || isSubmitting}
                className="w-full sm:w-auto px-6 py-3 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-300 text-white rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 disabled:cursor-not-allowed shadow-md hover:shadow-lg transform hover:-translate-y-0.5 disabled:transform-none"
              >
                {isSavingDraft ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Save as Draft</span>
                  </>
                )}
              </button>
              
              {/* Create Listing Button */}
              <button
                type="submit"
                disabled={isSubmitting || isSavingDraft}
                className="w-full sm:w-auto px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-lg font-semibold transition-all duration-200 flex items-center justify-center space-x-2 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-1 disabled:transform-none"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Publishing...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span>Create Listing</span>
                  </>
                )}
              </button>
            </div>
            
            {/* Additional Info */}
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                By creating a listing, you agree to our terms of service and marketplace guidelines.
              </p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateListingPage;