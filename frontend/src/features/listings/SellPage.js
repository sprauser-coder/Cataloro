import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { marketplaceAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import { useNavigate } from 'react-router-dom';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import ImageUploader from '../../components/marketplace/ImageUploader';
import CategorySelector from '../../components/marketplace/CategorySelector';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Label } from '../../components/ui/label';
import { Switch } from '../../components/ui/switch';
import { Badge } from '../../components/ui/badge';
import { AlertCircle, DollarSign, Package, FileText, Gavel, ShoppingCart, ArrowRight, ArrowLeft, Check } from 'lucide-react';

const SellPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    condition: '',
    price: '',
    quantity: 1,
    location: '',
    listing_type: 'fixed_price', // 'fixed_price' or 'auction'
    auction_duration: '7', // days
    starting_bid: '',
    buy_it_now_price: '',
    shipping_cost: '',
    shipping_included: true,
    returns_accepted: true,
    return_period: '30', // days
    tags: []
  });

  const [errors, setErrors] = useState({});

  const steps = [
    { number: 1, title: 'Basic Info', icon: FileText },
    { number: 2, title: 'Images', icon: Package },
    { number: 3, title: 'Pricing', icon: DollarSign },
    { number: 4, title: 'Review', icon: Check }
  ];

  const conditions = [
    { value: 'new', label: 'New', description: 'Brand new, never used' },
    { value: 'like new', label: 'Like New', description: 'Gently used, excellent condition' },
    { value: 'good', label: 'Good', description: 'Used with minor signs of wear' },
    { value: 'fair', label: 'Fair', description: 'Used with noticeable signs of wear' },
    { value: 'poor', label: 'Poor', description: 'Heavily used, functional but worn' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      if (!formData.title.trim()) newErrors.title = 'Title is required';
      if (formData.title.length < 5) newErrors.title = 'Title must be at least 5 characters';
      if (!formData.description.trim()) newErrors.description = 'Description is required';
      if (formData.description.length < 20) newErrors.description = 'Description must be at least 20 characters';
      if (!formData.category) newErrors.category = 'Category is required';
      if (!formData.condition) newErrors.condition = 'Condition is required';
      if (!formData.location.trim()) newErrors.location = 'Location is required';
    }

    if (step === 2) {
      if (images.length === 0) newErrors.images = 'At least one image is required';
    }

    if (step === 3) {
      if (formData.listing_type === 'fixed_price') {
        if (!formData.price || parseFloat(formData.price) <= 0) {
          newErrors.price = 'Valid price is required';
        }
      } else {
        if (!formData.starting_bid || parseFloat(formData.starting_bid) <= 0) {
          newErrors.starting_bid = 'Valid starting bid is required';
        }
      }
      if (!formData.quantity || parseInt(formData.quantity) <= 0) {
        newErrors.quantity = 'Valid quantity is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setLoading(true);

    try {
      const listingData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category,
        condition: formData.condition,
        price: formData.listing_type === 'fixed_price' ? parseFloat(formData.price) : null,
        starting_bid: formData.listing_type === 'auction' ? parseFloat(formData.starting_bid) : null,
        buy_it_now_price: formData.buy_it_now_price ? parseFloat(formData.buy_it_now_price) : null,
        quantity: parseInt(formData.quantity),
        location: formData.location.trim(),
        listing_type: formData.listing_type,
        auction_duration: formData.listing_type === 'auction' ? parseInt(formData.auction_duration) : null,
        shipping_cost: formData.shipping_included ? 0 : parseFloat(formData.shipping_cost || 0),
        images: images.map(img => img.url),
        tags: formData.tags,
        returns_accepted: formData.returns_accepted,
        return_period: formData.returns_accepted ? parseInt(formData.return_period) : null
      };

      const response = await marketplaceAPI.createListing(listingData);

      toast({
        title: "Success!",
        description: "Your listing has been created successfully"
      });

      // Navigate to the listing or browse page
      navigate('/browse');

    } catch (error) {
      console.error('Error creating listing:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create listing. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Title */}
                <div>
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    placeholder="What are you selling?"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className={errors.title ? 'border-red-300' : 'border-slate-200'}
                  />
                  {errors.title && (
                    <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                      <AlertCircle className="h-4 w-4" />
                      {errors.title}
                    </p>
                  )}
                  <p className="text-sm text-slate-500 mt-1">
                    {formData.title.length}/80 characters
                  </p>
                </div>

                {/* Description */}
                <div>
                  <Label htmlFor="description">Description *</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe your item in detail..."
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    className={`min-h-32 ${errors.description ? 'border-red-300' : 'border-slate-200'}`}
                  />
                  {errors.description && (
                    <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                      <AlertCircle className="h-4 w-4" />
                      {errors.description}
                    </p>
                  )}
                  <p className="text-sm text-slate-500 mt-1">
                    {formData.description.length}/1000 characters
                  </p>
                </div>

                {/* Category */}
                <div>
                  <CategorySelector
                    selectedCategory={formData.category}
                    onCategorySelect={(category) => handleInputChange('category', category.id)}
                    required
                  />
                  {errors.category && (
                    <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                      <AlertCircle className="h-4 w-4" />
                      {errors.category}
                    </p>
                  )}
                </div>

                {/* Condition & Location */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="condition">Condition *</Label>
                    <Select value={formData.condition} onValueChange={(value) => handleInputChange('condition', value)}>
                      <SelectTrigger className={errors.condition ? 'border-red-300' : 'border-slate-200'}>
                        <SelectValue placeholder="Select condition" />
                      </SelectTrigger>
                      <SelectContent>
                        {conditions.map(condition => (
                          <SelectItem key={condition.value} value={condition.value}>
                            <div>
                              <div className="font-medium">{condition.label}</div>
                              <div className="text-sm text-slate-500">{condition.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.condition && (
                      <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.condition}
                      </p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="location">Location *</Label>
                    <Input
                      id="location"
                      placeholder="City, Country"
                      value={formData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      className={errors.location ? 'border-red-300' : 'border-slate-200'}
                    />
                    {errors.location && (
                      <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.location}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Product Images</CardTitle>
              </CardHeader>
              <CardContent>
                <ImageUploader
                  onImagesChange={setImages}
                  maxImages={5}
                  existingImages={images}
                />
                {errors.images && (
                  <p className="text-red-600 text-sm mt-4 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.images}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            {/* Listing Type */}
            <Card>
              <CardHeader>
                <CardTitle>Listing Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div
                    onClick={() => handleInputChange('listing_type', 'fixed_price')}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                      formData.listing_type === 'fixed_price'
                        ? 'border-purple-400 bg-purple-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <ShoppingCart className="h-6 w-6 text-green-600" />
                      <h3 className="font-semibold">Fixed Price</h3>
                    </div>
                    <p className="text-sm text-slate-600">Set a fixed price for immediate purchase</p>
                  </div>

                  <div
                    onClick={() => handleInputChange('listing_type', 'auction')}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                      formData.listing_type === 'auction'
                        ? 'border-purple-400 bg-purple-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <Gavel className="h-6 w-6 text-orange-600" />
                      <h3 className="font-semibold">Auction</h3>
                    </div>
                    <p className="text-sm text-slate-600">Let buyers bid on your item</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Pricing */}
            <Card>
              <CardHeader>
                <CardTitle>Pricing & Quantity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {formData.listing_type === 'fixed_price' ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="price">Price *</Label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500">€</span>
                        <Input
                          id="price"
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={formData.price}
                          onChange={(e) => handleInputChange('price', e.target.value)}
                          className={`pl-8 ${errors.price ? 'border-red-300' : 'border-slate-200'}`}
                        />
                      </div>
                      {errors.price && (
                        <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                          <AlertCircle className="h-4 w-4" />
                          {errors.price}
                        </p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="quantity">Quantity *</Label>
                      <Input
                        id="quantity"
                        type="number"
                        min="1"
                        value={formData.quantity}
                        onChange={(e) => handleInputChange('quantity', e.target.value)}
                        className={errors.quantity ? 'border-red-300' : 'border-slate-200'}
                      />
                      {errors.quantity && (
                        <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                          <AlertCircle className="h-4 w-4" />
                          {errors.quantity}
                        </p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Label htmlFor="starting_bid">Starting Bid *</Label>
                        <div className="relative">
                          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500">€</span>
                          <Input
                            id="starting_bid"
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={formData.starting_bid}
                            onChange={(e) => handleInputChange('starting_bid', e.target.value)}
                            className={`pl-8 ${errors.starting_bid ? 'border-red-300' : 'border-slate-200'}`}
                          />
                        </div>
                        {errors.starting_bid && (
                          <p className="text-red-600 text-sm mt-1 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.starting_bid}
                          </p>
                        )}
                      </div>

                      <div>
                        <Label htmlFor="auction_duration">Auction Duration</Label>
                        <Select value={formData.auction_duration} onValueChange={(value) => handleInputChange('auction_duration', value)}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="3">3 days</SelectItem>
                            <SelectItem value="5">5 days</SelectItem>
                            <SelectItem value="7">7 days</SelectItem>
                            <SelectItem value="10">10 days</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="buy_it_now_price">Buy It Now Price (Optional)</Label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500">€</span>
                        <Input
                          id="buy_it_now_price"
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={formData.buy_it_now_price}
                          onChange={(e) => handleInputChange('buy_it_now_price', e.target.value)}
                          className="pl-8 border-slate-200"
                        />
                      </div>
                      <p className="text-sm text-slate-500 mt-1">Allow buyers to purchase immediately at this price</p>
                    </div>
                  </div>
                )}

                {/* Shipping */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Free Shipping</Label>
                      <p className="text-sm text-slate-500">Include shipping cost in item price</p>
                    </div>
                    <Switch
                      checked={formData.shipping_included}
                      onCheckedChange={(checked) => handleInputChange('shipping_included', checked)}
                    />
                  </div>

                  {!formData.shipping_included && (
                    <div>
                      <Label htmlFor="shipping_cost">Shipping Cost</Label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500">€</span>
                        <Input
                          id="shipping_cost"
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={formData.shipping_cost}
                          onChange={(e) => handleInputChange('shipping_cost', e.target.value)}
                          className="pl-8 border-slate-200"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Returns */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Accept Returns</Label>
                      <p className="text-sm text-slate-500">Allow buyers to return items</p>
                    </div>
                    <Switch
                      checked={formData.returns_accepted}
                      onCheckedChange={(checked) => handleInputChange('returns_accepted', checked)}
                    />
                  </div>

                  {formData.returns_accepted && (
                    <div>
                      <Label htmlFor="return_period">Return Period</Label>
                      <Select value={formData.return_period} onValueChange={(value) => handleInputChange('return_period', value)}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="14">14 days</SelectItem>
                          <SelectItem value="30">30 days</SelectItem>
                          <SelectItem value="60">60 days</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Review Your Listing</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Preview */}
                <div className="border border-slate-200 rounded-lg p-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Images */}
                    <div>
                      {images.length > 0 ? (
                        <div className="aspect-square rounded-lg overflow-hidden">
                          <img
                            src={images[0]?.url}
                            alt={formData.title}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ) : (
                        <div className="aspect-square bg-slate-100 rounded-lg flex items-center justify-center">
                          <Package className="h-12 w-12 text-slate-400" />
                        </div>
                      )}
                      {images.length > 1 && (
                        <p className="text-sm text-slate-500 mt-2">+{images.length - 1} more images</p>
                      )}
                    </div>

                    {/* Details */}
                    <div className="md:col-span-2">
                      <h3 className="text-xl font-semibold text-slate-900 mb-2">{formData.title}</h3>
                      <p className="text-slate-600 mb-4 line-clamp-3">{formData.description}</p>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        <Badge variant="outline">{formData.category}</Badge>
                        <Badge variant="outline">{formData.condition}</Badge>
                        <Badge variant="outline">{formData.listing_type === 'fixed_price' ? 'Buy Now' : 'Auction'}</Badge>
                      </div>

                      <div className="space-y-2 text-sm">
                        <p><span className="font-medium">Location:</span> {formData.location}</p>
                        <p><span className="font-medium">Quantity:</span> {formData.quantity}</p>
                        <p><span className="font-medium">Shipping:</span> {formData.shipping_included ? 'Free' : `€${formData.shipping_cost}`}</p>
                        <p><span className="font-medium">Returns:</span> {formData.returns_accepted ? `Accepted (${formData.return_period} days)` : 'Not accepted'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mt-6 pt-6 border-t border-slate-200">
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-medium">
                        {formData.listing_type === 'fixed_price' ? 'Price:' : 'Starting bid:'}
                      </span>
                      <span className="text-2xl font-bold text-purple-600">
                        €{formData.listing_type === 'fixed_price' ? formData.price : formData.starting_bid}
                      </span>
                    </div>
                    {formData.listing_type === 'auction' && formData.buy_it_now_price && (
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm text-slate-600">Buy It Now:</span>
                        <span className="font-medium">€{formData.buy_it_now_price}</span>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-light text-slate-900 mb-4 tracking-tight">
            Create New Listing
          </h1>
          <p className="text-lg text-slate-600 font-light">
            Sell your items to millions of buyers worldwide
          </p>
        </div>

        {/* Progress Steps */}
        <Card className="border-0 shadow-sm mb-8">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = currentStep === step.number;
                const isCompleted = currentStep > step.number;
                
                return (
                  <div key={step.number} className="flex items-center">
                    <div className={`
                      flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors
                      ${isActive 
                        ? 'bg-purple-600 border-purple-600 text-white' 
                        : isCompleted 
                          ? 'bg-green-500 border-green-500 text-white'
                          : 'border-slate-300 text-slate-400'
                      }
                    `}>
                      {isCompleted ? (
                        <Check className="h-5 w-5" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </div>
                    <div className="ml-3">
                      <p className={`font-medium ${isActive ? 'text-purple-600' : isCompleted ? 'text-green-600' : 'text-slate-400'}`}>
                        Step {step.number}
                      </p>
                      <p className="text-sm text-slate-600">{step.title}</p>
                    </div>
                    {index < steps.length - 1 && (
                      <div className={`mx-8 h-px w-16 ${isCompleted ? 'bg-green-500' : 'bg-slate-300'}`} />
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Step Content */}
        {renderStepContent()}

        {/* Navigation */}
        <Card className="border-0 shadow-sm mt-8">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className="border-slate-200 text-slate-600 hover:bg-slate-50"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>

              <div className="text-sm text-slate-500">
                Step {currentStep} of {steps.length}
              </div>

              {currentStep < steps.length ? (
                <Button
                  onClick={handleNext}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  {loading ? (
                    <>
                      <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating...
                    </>
                  ) : (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Create Listing
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default SellPage;