import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { marketplaceAPI, favoritesAPI, ordersAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Input } from '../../components/ui/input';
import { 
  Heart, Share2, Flag, Star, MapPin, Clock, Package, 
  Truck, Shield, ArrowLeft, Plus, Minus, ShoppingCart, 
  MessageCircle, User, Eye, Camera
} from 'lucide-react';
import { formatCurrency, formatDate, getImageUrl } from '../../utils/helpers';

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteId, setFavoriteId] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [bidAmount, setBidAmount] = useState('');
  const [relatedProducts, setRelatedProducts] = useState([]);
  
  const [purchasing, setPurchasing] = useState(false);
  const [bidding, setBidding] = useState(false);

  useEffect(() => {
    fetchListingDetails();
    checkFavoriteStatus();
  }, [id]);

  useEffect(() => {
    if (listing) {
      fetchRelatedProducts();
    }
  }, [listing]);

  const fetchListingDetails = async () => {
    try {
      setLoading(true);
      const response = await marketplaceAPI.getListingById(id);
      setListing(response.data);
    } catch (error) {
      console.error('Error fetching listing:', error);
      toast({
        title: "Error",
        description: "Failed to load product details. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const checkFavoriteStatus = async () => {
    if (!user) return;
    
    try {
      const response = await favoritesAPI.getFavorites();
      const favorite = response.data.find(fav => fav.listing_id === id);
      if (favorite) {
        setIsFavorited(true);
        setFavoriteId(favorite.id);
      }
    } catch (error) {
      console.error('Error checking favorite status:', error);
    }
  };

  const fetchRelatedProducts = async () => {
    try {
      const response = await marketplaceAPI.getListings({
        category: listing.category,
        limit: 4,
        exclude: id
      });
      setRelatedProducts(response.data || []);
    } catch (error) {
      console.error('Error fetching related products:', error);
    }
  };

  const handleFavoriteToggle = async () => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to add favorites",
        variant: "destructive"
      });
      return;
    }

    try {
      if (isFavorited) {
        await favoritesAPI.removeFavorite(favoriteId);
        setIsFavorited(false);
        setFavoriteId(null);
        toast({
          title: "Removed from favorites",
          description: "Item removed successfully"
        });
      } else {
        const response = await favoritesAPI.addFavorite(id);
        setIsFavorited(true);
        setFavoriteId(response.data.id);
        toast({
          title: "Added to favorites",
          description: "Item saved successfully"
        });
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast({
        title: "Error",
        description: "Failed to update favorites",
        variant: "destructive"
      });
    }
  };

  const handlePurchase = async () => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to make a purchase",
        variant: "destructive"
      });
      return;
    }

    setPurchasing(true);
    
    try {
      const orderData = {
        listing_id: id,
        quantity: quantity,
        total_amount: listing.price * quantity + (listing.shipping_cost || 0)
      };

      const response = await ordersAPI.createOrder(orderData);
      
      toast({
        title: "Order Created!",
        description: "Your order has been placed successfully"
      });
      
      navigate('/orders');
    } catch (error) {
      console.error('Error creating order:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create order. Please try again.",
        variant: "destructive"
      });
    } finally {
      setPurchasing(false);
    }
  };

  const handlePlaceBid = async () => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to place a bid",
        variant: "destructive"
      });
      return;
    }

    if (!bidAmount || parseFloat(bidAmount) <= (listing.current_bid || listing.starting_bid)) {
      toast({
        title: "Invalid Bid",
        description: "Bid must be higher than the current bid",
        variant: "destructive"
      });
      return;
    }

    setBidding(true);
    
    try {
      await marketplaceAPI.placeBid(id, parseFloat(bidAmount));
      
      toast({
        title: "Bid Placed!",
        description: "Your bid has been placed successfully"
      });
      
      // Refresh listing to get updated bid info
      fetchListingDetails();
      setBidAmount('');
    } catch (error) {
      console.error('Error placing bid:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to place bid. Please try again.",
        variant: "destructive"
      });
    } finally {
      setBidding(false);
    }
  };

  const getConditionColor = (condition) => {
    switch (condition?.toLowerCase()) {
      case 'new': return 'bg-green-100 text-green-800';
      case 'like new': return 'bg-blue-100 text-blue-800';
      case 'good': return 'bg-yellow-100 text-yellow-800';
      case 'fair': return 'bg-orange-100 text-orange-800';
      case 'poor': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
        <Header />
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <p className="mt-2 text-slate-600">Loading product details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <Package className="h-16 w-16 mx-auto text-slate-400 mb-4" />
          <h2 className="text-2xl font-semibold text-slate-700 mb-2">Product Not Found</h2>
          <p className="text-slate-500 mb-6">The product you're looking for doesn't exist or has been removed.</p>
          <Button onClick={() => navigate('/browse')} className="bg-purple-600 hover:bg-purple-700">
            Browse Products
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/browse')}
            className="text-slate-600 hover:text-slate-800"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Browse
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Image Gallery */}
          <div className="space-y-4">
            <Card className="border-0 shadow-sm overflow-hidden">
              <CardContent className="p-0">
                <div className="aspect-square relative">
                  {listing.images && listing.images.length > 0 ? (
                    <img
                      src={getImageUrl(listing.images[selectedImageIndex])}
                      alt={listing.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center">
                      <Camera className="h-16 w-16 text-slate-400" />
                    </div>
                  )}
                  
                  {/* Image Counter */}
                  {listing.images && listing.images.length > 1 && (
                    <div className="absolute top-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
                      {selectedImageIndex + 1} / {listing.images.length}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Thumbnail Gallery */}
            {listing.images && listing.images.length > 1 && (
              <div className="flex gap-2 overflow-x-auto">
                {listing.images.map((image, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                      selectedImageIndex === index ? 'border-purple-500' : 'border-slate-200'
                    }`}
                  >
                    <img
                      src={getImageUrl(image)}
                      alt={`View ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            {/* Title & Basic Info */}
            <div>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h1 className="text-3xl font-light text-slate-900 mb-2">{listing.title}</h1>
                  <div className="flex items-center gap-2 mb-4">
                    <Badge variant="outline">{listing.category}</Badge>
                    <Badge className={getConditionColor(listing.condition)}>
                      {listing.condition}
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Eye className="h-3 w-3" />
                      {listing.views || 0} views
                    </Badge>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleFavoriteToggle}
                    className="border-red-200 text-red-600 hover:bg-red-50"
                  >
                    <Heart className={`h-4 w-4 ${isFavorited ? 'fill-current' : ''}`} />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Share2 className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Flag className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Price */}
              <div className="space-y-2">
                {listing.listing_type === 'fixed_price' ? (
                  <div className="text-4xl font-bold text-purple-600">
                    {formatCurrency(listing.price)}
                  </div>
                ) : (
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      Current Bid: {formatCurrency(listing.current_bid || listing.starting_bid)}
                    </div>
                    {listing.buy_it_now_price && (
                      <div className="text-lg text-slate-600">
                        Buy It Now: {formatCurrency(listing.buy_it_now_price)}
                      </div>
                    )}
                  </div>
                )}
                
                {listing.shipping_cost > 0 ? (
                  <p className="text-slate-600">+ {formatCurrency(listing.shipping_cost)} shipping</p>
                ) : (
                  <p className="text-green-600 font-medium">Free shipping</p>
                )}
              </div>
            </div>

            {/* Seller Info */}
            <Card className="border-0 shadow-sm">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <User className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-slate-900">{listing.seller_name || 'Anonymous Seller'}</h4>
                    <div className="flex items-center gap-2">
                      {listing.seller_rating && (
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm text-slate-600">{listing.seller_rating.toFixed(1)}</span>
                        </div>
                      )}
                      <span className="text-sm text-slate-500">Member since {formatDate(listing.seller_joined || listing.created_at)}</span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Contact
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Purchase/Bid Section */}
            <Card className="border-0 shadow-sm">
              <CardContent className="p-6">
                {listing.listing_type === 'fixed_price' ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4">
                      <span className="text-sm font-medium">Quantity:</span>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setQuantity(Math.max(1, quantity - 1))}
                        >
                          <Minus className="h-4 w-4" />
                        </Button>
                        <Input
                          type="number"
                          min="1"
                          max={listing.quantity}
                          value={quantity}
                          onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                          className="w-20 text-center"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setQuantity(Math.min(listing.quantity, quantity + 1))}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                      <span className="text-sm text-slate-500">({listing.quantity} available)</span>
                    </div>

                    <div className="space-y-2">
                      <Button
                        onClick={handlePurchase}
                        disabled={purchasing}
                        className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3"
                      >
                        {purchasing ? (
                          <>
                            <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Processing...
                          </>
                        ) : (
                          <>
                            <ShoppingCart className="h-4 w-4 mr-2" />
                            Buy Now - {formatCurrency((listing.price * quantity) + (listing.shipping_cost || 0))}
                          </>
                        )}
                      </Button>
                      
                      <Button variant="outline" className="w-full">
                        Add to Cart
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-center">
                      <p className="text-sm text-slate-600 mb-2">Auction ends in:</p>
                      <div className="text-2xl font-bold text-red-600">2d 14h 23m</div>
                    </div>

                    <div className="space-y-2">
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Enter bid amount"
                        value={bidAmount}
                        onChange={(e) => setBidAmount(e.target.value)}
                      />
                      <Button
                        onClick={handlePlaceBid}
                        disabled={bidding}
                        className="w-full bg-orange-600 hover:bg-orange-700 text-white"
                      >
                        {bidding ? (
                          <>
                            <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Placing Bid...
                          </>
                        ) : (
                          'Place Bid'
                        )}
                      </Button>
                      
                      {listing.buy_it_now_price && (
                        <Button 
                          onClick={handlePurchase}
                          variant="outline" 
                          className="w-full"
                        >
                          Buy It Now - {formatCurrency(listing.buy_it_now_price)}
                        </Button>
                      )}
                    </div>
                  </div>
                )}

                {/* Item Details */}
                <div className="mt-6 pt-6 border-t border-slate-200 space-y-3 text-sm">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-slate-400" />
                    <span>Ships from {listing.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Truck className="h-4 w-4 text-slate-400" />
                    <span>Standard shipping: 3-7 business days</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-slate-400" />
                    <span>{listing.returns_accepted ? `Returns accepted (${listing.return_period} days)` : 'Returns not accepted'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Product Details Tabs */}
        <Card className="border-0 shadow-sm mb-8">
          <CardContent className="p-6">
            <Tabs defaultValue="description">
              <TabsList className="grid grid-cols-3 w-full">
                <TabsTrigger value="description">Description</TabsTrigger>
                <TabsTrigger value="shipping">Shipping & Returns</TabsTrigger>
                <TabsTrigger value="reviews">Reviews</TabsTrigger>
              </TabsList>

              <TabsContent value="description" className="mt-6">
                <div className="prose max-w-none">
                  <h3 className="text-lg font-semibold mb-4">Product Description</h3>
                  <p className="text-slate-600 whitespace-pre-wrap leading-relaxed">
                    {listing.description}
                  </p>
                  
                  {listing.tags && listing.tags.length > 0 && (
                    <div className="mt-6">
                      <h4 className="font-medium mb-2">Tags:</h4>
                      <div className="flex flex-wrap gap-2">
                        {listing.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="shipping" className="mt-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Shipping Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <h4 className="font-medium mb-2">Shipping Cost</h4>
                      <p className="text-slate-600">
                        {listing.shipping_cost > 0 
                          ? `${formatCurrency(listing.shipping_cost)} standard shipping`
                          : 'Free standard shipping'
                        }
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Estimated Delivery</h4>
                      <p className="text-slate-600">3-7 business days</p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Return Policy</h4>
                      <p className="text-slate-600">
                        {listing.returns_accepted 
                          ? `Returns accepted within ${listing.return_period} days`
                          : 'Returns not accepted'
                        }
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Ships From</h4>
                      <p className="text-slate-600">{listing.location}</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="reviews" className="mt-6">
                <div className="text-center py-8">
                  <Star className="h-12 w-12 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">No Reviews Yet</h3>
                  <p className="text-slate-500">Be the first to review this product</p>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <div>
            <h2 className="text-2xl font-light text-slate-900 mb-6">Related Products</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {relatedProducts.map((product) => (
                <Card key={product.id} className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-0">
                    <div className="aspect-square relative overflow-hidden rounded-t-lg">
                      {product.images && product.images.length > 0 ? (
                        <img
                          src={getImageUrl(product.images[0])}
                          alt={product.title}
                          className="w-full h-full object-cover"
                          onClick={() => navigate(`/listing/${product.id}`)}
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center">
                          <Package className="h-8 w-8 text-slate-400" />
                        </div>
                      )}
                    </div>
                    <div className="p-4">
                      <h3 className="font-medium text-slate-900 mb-2 line-clamp-2">{product.title}</h3>
                      <p className="text-lg font-bold text-purple-600">{formatCurrency(product.price)}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default ProductDetailPage;