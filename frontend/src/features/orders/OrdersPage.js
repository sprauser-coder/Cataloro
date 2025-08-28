import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { ordersAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Package, Truck, Clock, CheckCircle, XCircle, Eye, MessageSquare, RefreshCw } from 'lucide-react';
import { formatCurrency, formatDate, getImageUrl } from '../../utils/helpers';

const OrdersPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('purchases');
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, [activeTab]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await ordersAPI.getOrders();
      
      // Filter orders based on active tab
      let filteredOrders = response.data || [];
      if (activeTab === 'purchases') {
        filteredOrders = filteredOrders.filter(order => order.buyer_id === user.id);
      } else if (activeTab === 'sales') {
        filteredOrders = filteredOrders.filter(order => order.seller_id === user.id);
      }
      
      setOrders(filteredOrders);
    } catch (error) {
      console.error('Error fetching orders:', error);
      toast({
        title: "Error",
        description: "Failed to load orders. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'paid': return 'bg-blue-100 text-blue-800';
      case 'shipped': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'refunded': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending': return Clock;
      case 'paid': return CheckCircle;
      case 'shipped': return Truck;
      case 'delivered': return Package;
      case 'cancelled': return XCircle;
      case 'refunded': return RefreshCw;
      default: return Package;
    }
  };

  const OrderCard = ({ order }) => {
    const StatusIcon = getStatusIcon(order.status);
    
    return (
      <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            {/* Order Image */}
            <div className="flex-shrink-0">
              {order.listing?.images && order.listing.images.length > 0 ? (
                <img
                  src={getImageUrl(order.listing.images[0])}
                  alt={order.listing.title}
                  className="w-16 h-16 object-cover rounded-lg"
                />
              ) : (
                <div className="w-16 h-16 bg-slate-100 rounded-lg flex items-center justify-center">
                  <Package className="h-6 w-6 text-slate-400" />
                </div>
              )}
            </div>

            {/* Order Details */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-slate-900 truncate">
                    {order.listing?.title || 'Product Title'}
                  </h3>
                  <p className="text-sm text-slate-500">
                    Order #{order.id?.substring(0, 8)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-lg">{formatCurrency(order.total_amount)}</p>
                  <p className="text-sm text-slate-500">Qty: {order.quantity}</p>
                </div>
              </div>

              {/* Status and Date */}
              <div className="flex items-center justify-between mb-3">
                <Badge className={getStatusColor(order.status)}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {order.status}
                </Badge>
                <p className="text-sm text-slate-500">
                  {formatDate(order.created_at)}
                </p>
              </div>

              {/* Buyer/Seller Info */}
              <div className="mb-3">
                {activeTab === 'purchases' ? (
                  <p className="text-sm text-slate-600">
                    <span className="font-medium">Seller:</span> {order.seller_name || 'Unknown'}
                  </p>
                ) : (
                  <p className="text-sm text-slate-600">
                    <span className="font-medium">Buyer:</span> {order.buyer_name || 'Unknown'}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedOrder(order)}
                  className="border-slate-200 text-slate-600 hover:bg-slate-50"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </Button>
                
                {(order.status === 'delivered' || order.status === 'completed') && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-purple-200 text-purple-600 hover:bg-purple-50"
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Leave Review
                  </Button>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const OrderDetailsModal = ({ order, onClose }) => {
    if (!order) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <Card className="w-full max-w-2xl max-h-96 overflow-y-auto">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle>Order Details</CardTitle>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <XCircle className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Order Summary */}
            <div className="border-b pb-4">
              <div className="flex items-start gap-4">
                {order.listing?.images && order.listing.images.length > 0 && (
                  <img
                    src={getImageUrl(order.listing.images[0])}
                    alt={order.listing.title}
                    className="w-24 h-24 object-cover rounded-lg"
                  />
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">{order.listing?.title}</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Order ID:</span> {order.id}
                    </div>
                    <div>
                      <span className="font-medium">Date:</span> {formatDate(order.created_at)}
                    </div>
                    <div>
                      <span className="font-medium">Quantity:</span> {order.quantity}
                    </div>
                    <div>
                      <span className="font-medium">Status:</span> 
                      <Badge className={`ml-2 ${getStatusColor(order.status)}`}>
                        {order.status}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Pricing Breakdown */}
            <div>
              <h4 className="font-medium mb-3">Pricing</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Item price:</span>
                  <span>{formatCurrency(order.item_price)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Quantity:</span>
                  <span>{order.quantity}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping:</span>
                  <span>{order.shipping_cost ? formatCurrency(order.shipping_cost) : 'Free'}</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-medium">
                  <span>Total:</span>
                  <span>{formatCurrency(order.total_amount)}</span>
                </div>
              </div>
            </div>

            {/* Shipping Address */}
            {order.shipping_address && (
              <div>
                <h4 className="font-medium mb-3">Shipping Address</h4>
                <div className="text-sm text-slate-600 bg-slate-50 p-3 rounded">
                  {order.shipping_address}
                </div>
              </div>
            )}

            {/* Order Timeline */}
            <div>
              <h4 className="font-medium mb-3">Order Timeline</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Order placed - {formatDate(order.created_at)}</span>
                </div>
                {order.status !== 'pending' && (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm">Payment confirmed</span>
                  </div>
                )}
                {order.status === 'shipped' || order.status === 'delivered' && (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="text-sm">Item shipped</span>
                  </div>
                )}
                {order.status === 'delivered' && (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                    <span className="text-sm">Order delivered</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-light text-slate-900 mb-4 tracking-tight">
            My Orders
          </h1>
          <p className="text-lg text-slate-600 font-light">
            Track your purchases and sales
          </p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 bg-white shadow-sm mb-8">
            <TabsTrigger value="purchases" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              My Purchases
            </TabsTrigger>
            <TabsTrigger value="sales" className="flex items-center gap-2">
              <Truck className="h-4 w-4" />
              My Sales
            </TabsTrigger>
          </TabsList>

          {/* Purchases Tab */}
          <TabsContent value="purchases">
            {loading ? (
              <div className="flex justify-center py-16">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  <p className="mt-2 text-slate-600">Loading your purchases...</p>
                </div>
              </div>
            ) : orders.length === 0 ? (
              <Card className="border-0 shadow-sm">
                <CardContent className="text-center py-16">
                  <Package className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">No purchases yet</h3>
                  <p className="text-slate-500 mb-6">
                    Start shopping to see your orders here
                  </p>
                  <Button
                    onClick={() => window.location.href = '#/browse'}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    Browse Products
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {orders.map((order) => (
                  <OrderCard key={order.id} order={order} />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Sales Tab */}
          <TabsContent value="sales">
            {loading ? (
              <div className="flex justify-center py-16">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  <p className="mt-2 text-slate-600">Loading your sales...</p>
                </div>
              </div>
            ) : orders.length === 0 ? (
              <Card className="border-0 shadow-sm">
                <CardContent className="text-center py-16">
                  <Truck className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">No sales yet</h3>
                  <p className="text-slate-500 mb-6">
                    Create a listing to start selling
                  </p>
                  <Button
                    onClick={() => window.location.href = '#/sell'}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    Start Selling
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {orders.map((order) => (
                  <OrderCard key={order.id} order={order} />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Order Details Modal */}
        {selectedOrder && (
          <OrderDetailsModal
            order={selectedOrder}
            onClose={() => setSelectedOrder(null)}
          />
        )}
      </div>

      <Footer />
    </div>
  );
};

export default OrdersPage;