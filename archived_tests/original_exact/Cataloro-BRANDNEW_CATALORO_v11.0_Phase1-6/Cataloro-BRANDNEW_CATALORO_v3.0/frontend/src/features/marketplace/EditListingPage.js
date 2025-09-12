/**
 * CATALORO - Edit Listing Page
 * Form for editing existing marketplace listings
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
  Loader
} from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';

function EditListingPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    category: 'General',
    condition: 'New',
    street: '',
    post_code: '',
    city: '',
    country: '',
    shipping: 'pickup',
    shipping_cost: '',
    tags: [],
    features: []
  });

  const [useProfileAddress, setUseProfileAddress] = useState(true);
  const [profileAddress, setProfileAddress] = useState({
    street: '',
    post_code: '',
    city: '',
    country: ''
  });

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

  // Load existing listing data on component mount
  useEffect(() => {
    loadListingData();
    loadProfileAddress();
  }, [id]);

  const loadListingData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Get user data to verify ownership
      const userData = localStorage.getItem('cataloro_user');
      const user = userData ? JSON.parse(userData) : null;
      
      if (!user) {
        setError('Please log in to edit listings');
        return;
      }

      // Fetch listing data from API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings/${id}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch listing data');
      }
      
      const listing = await response.json();
      
      // Verify user owns this listing
      if (listing.seller_id !== user.id) {
        setError('You can only edit your own listings');
        return;
      }
      
      // Populate form with existing data
      setFormData({
        title: listing.title || '',
        description: listing.description || '',
        price: listing.price?.toString() || '',
        category: listing.category || 'General',
        condition: listing.condition || 'New',
        street: listing.address?.street || listing.street || '',
        post_code: listing.address?.post_code || listing.post_code || '',
        city: listing.address?.city || listing.city || '',
        country: listing.address?.country || listing.country || '',
        shipping: listing.shipping || 'pickup',
        shipping_cost: listing.shipping_cost?.toString() || '',
        tags: listing.tags || [],
        features: listing.features || []
      });
      
      // Set existing images
      if (listing.images && listing.images.length > 0) {
        setImagePreviews(listing.images);
      }
      
      // Check if using profile address
      setUseProfileAddress(listing.address?.use_profile_address || false);
      
    } catch (err) {
      console.error('Failed to load listing:', err);
      setError('Failed to load listing data');
    } finally {
      setIsLoading(false);
    }
  };

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
      }
    } catch (error) {
      console.error('Failed to load profile address:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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
      // Keep current address values (don't clear them)
    }
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

    if (imagePreviews.length === 0) {
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
        alert('Please log in to update listing');
        navigate('/login');
        return;
      }

      // Prepare updated listing data
      const updatedListingData = {
        ...formData,
        price: parseFloat(formData.price),
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
        updated_at: new Date().toISOString()
      };

      // Update listing via API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedListingData)
      });

      if (!response.ok) {
        throw new Error('Failed to update listing');
      }

      // Show success message
      alert('Listing updated successfully!');

      // Navigate back to my listings page
      navigate('/my-listings');

    } catch (error) {
      console.error('Failed to update listing:', error);
      alert('Failed to update listing. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Loader className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Loading listing data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-16">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Error Loading Listing</h1>
            <p className="text-gray-600 dark:text-gray-400 mb-8">{error}</p>
            <Link 
              to="/my-listings"
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to My Listings
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Edit Listing</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Update your listing details below
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
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Enter item title"
                  className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Provide a detailed description of your item..."
                  rows={4}
                  className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  required
                />
              </div>

              {/* Price and Category Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Price * (€)
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
                      className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Category
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  >
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Address Section */}
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
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
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
                <h3 className="text-lg font-semibold mb-2">Ready to update your listing?</h3>
                <p className="text-blue-100">
                  Review all information above and click update to save your changes.
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
                      <span>Updating...</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5" />
                      <span>Update Listing</span>
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

export default EditListingPage;