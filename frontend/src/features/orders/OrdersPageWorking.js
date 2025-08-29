import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { ordersAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { 
  Package, Truck, Clock, CheckCircle, XCircle, 
  Search, Filter, Calendar, Euro, Star, 
  Eye, MessageCircle, Download, RefreshCw,
  ShoppingBag, AlertTriangle, TrendingUp
} from 'lucide-react';
import { formatCurrency, formatDate } from '../../utils/helpers';

const OrdersPageWorking = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  // State management
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState([]);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  
  // Mock orders data with comprehensive information
  const mockOrders = [
    {
      id: 'ORD-2024-001',
      listing_title: 'BMW X5 E70 Catalytic Converter',
      seller_name: 'AutoParts Pro',
      buyer_name: 'John Mueller',
      amount: 245.00,
      status: 'delivered',
      order_date: '2024-08-15T10:30:00Z',
      shipping_date: '2024-08-16T14:20:00Z',
      delivery_date: '2024-08-20T09:15:00Z',
      payment_method: 'Credit Card',
      shipping_address: 'Hauptstraße 123, 10115 Berlin',
      tracking_number: 'DHL123456789',
      rating: 5,
      review: 'Perfect condition, fast shipping!',
      type: user?.role === 'admin' ? 'sale' : 'purchase'
    },
    {
      id: 'ORD-2024-002',
      listing_title: 'Mercedes C-Class W204 DPF Filter',
      seller_name: 'Diesel Parts GmbH',
      buyer_name: 'Anna Schmidt',
      amount: 180.50,
      status: 'shipped',
      order_date: '2024-08-20T16:45:00Z',
      shipping_date: '2024-08-21T11:30:00Z',
      delivery_date: null,
      payment_method: 'PayPal',
      shipping_address: 'Friedrichstraße 45, 20095 Hamburg',
      tracking_number: 'UPS987654321',
      rating: null,
      review: null,
      type: user?.role === 'admin' ? 'sale' : 'purchase'
    },
    {
      id: 'ORD-2024-003',
      listing_title: 'Audi A4 B8 Exhaust System Complete',
      seller_name: 'Performance Parts',
      buyer_name: 'Michael Weber',
      amount: 320.00,
      status: 'pending',
      order_date: '2024-08-25T09:15:00Z',
      shipping_date: null,
      delivery_date: null,
      payment_method: 'Bank Transfer',
      shipping_address: 'Münchener Straße 78, 80331 München',
      tracking_number: null,
      rating: null,
      review: null,
      type: user?.role === 'admin' ? 'purchase' : 'sale'
    },
    {
      id: 'ORD-2024-004',
      listing_title: 'VW Golf MK7 Catalytic Converter',
      seller_name: 'Euro Auto Parts',
      buyer_name: 'Lisa Hoffmann',
      amount: 95.75,
      status: 'cancelled',
      order_date: '2024-08-18T14:20:00Z',
      shipping_date: null,
      delivery_date: null,
      payment_method: 'Credit Card',
      shipping_address: 'Kölner Ring 12, 50678 Köln',
      tracking_number: null,
      rating: null,
      review: null,
      cancellation_reason: 'Item no longer available',
      type: user?.role === 'admin' ? 'sale' : 'purchase'
    }
  ];

  useEffect(() => {
    fetchOrders();
  }, []);

  useEffect(() => {
    filterOrders();
  }, [orders, searchTerm, statusFilter, dateRange, activeTab]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      // Using mock data for now
      setOrders(mockOrders);
    } catch (error) {
      console.error('Error fetching orders:', error);
      toast({
        title: "Error",
        description: "Failed to load orders",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const filterOrders = () => {
    let filtered = [...orders];

    // Filter by tab (all, purchases, sales)
    if (activeTab === 'purchases') {
      filtered = filtered.filter(order => order.type === 'purchase');
    } else if (activeTab === 'sales') {
      filtered = filtered.filter(order => order.type === 'sale');
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(order =>
        order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.listing_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.seller_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.buyer_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    // Filter by date range
    if (dateRange !== 'all') {
      const now = new Date();
      const orderDate = new Date(order.order_date);
      
      switch (dateRange) {
        case 'week':
          filtered = filtered.filter(order => {
            const orderDate = new Date(order.order_date);
            return (now - orderDate) <= 7 * 24 * 60 * 60 * 1000;
          });
          break;
        case 'month':
          filtered = filtered.filter(order => {
            const orderDate = new Date(order.order_date);
            return (now - orderDate) <= 30 * 24 * 60 * 60 * 1000;
          });
          break;
        case 'quarter':
          filtered = filtered.filter(order => {
            const orderDate = new Date(order.order_date);
            return (now - orderDate) <= 90 * 24 * 60 * 60 * 1000;
          });
          break;
      }
    }

    setFilteredOrders(filtered);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'paid': return <CheckCircle className="h-4 w-4 text-blue-600" />;
      case 'shipped': return <Truck className="h-4 w-4 text-purple-600" />;
      case 'delivered': return <Package className="h-4 w-4 text-green-600" />;
      case 'cancelled': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'paid': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'shipped': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'delivered': return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const OrderCard = ({ order }) => (
    <Card className="border-0 shadow-sm hover:shadow-lg transition-all duration-300 hover:scale-[1.02]">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg font-semibold text-slate-900 mb-2">
              {order.listing_title}
            </CardTitle>
            <div className="flex items-center gap-4 text-sm text-slate-600">
              <span className="font-medium">#{order.id}</span>
              <span>{formatDate(order.order_date)}</span>
            </div>
          </div>
          <Badge className={`${getStatusColor(order.status)} border font-medium`}>
            <div className="flex items-center gap-1">
              {getStatusIcon(order.status)}
              {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
            </div>
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm font-medium text-slate-700 mb-1">
              {order.type === 'sale' ? 'Buyer' : 'Seller'}
            </p>
            <p className="text-sm text-slate-600">
              {order.type === 'sale' ? order.buyer_name : order.seller_name}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-slate-700 mb-1">Amount</p>
            <p className="text-lg font-bold text-purple-600">
              {formatCurrency(order.amount)}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-slate-700 mb-1">Payment Method</p>
            <p className="text-sm text-slate-600">{order.payment_method}</p>
          </div>
          {order.tracking_number && (
            <div>
              <p className="text-sm font-medium text-slate-700 mb-1">Tracking</p>
              <p className="text-sm text-blue-600 font-mono">{order.tracking_number}</p>
            </div>
          )}
        </div>

        {order.shipping_address && (
          <div className="mb-4 p-3 bg-slate-50 rounded-lg">
            <p className="text-sm font-medium text-slate-700 mb-1">Shipping Address</p>
            <p className="text-sm text-slate-600">{order.shipping_address}</p>
          </div>
        )}

        {order.status === 'delivered' && order.rating && (
          <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-4 w-4 ${
                      i < order.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm font-medium text-green-800">
                Customer Review
              </span>
            </div>
            {order.review && (
              <p className="text-sm text-green-700 italic">"{order.review}"</p>
            )}
          </div>
        )}

        {order.status === 'cancelled' && order.cancellation_reason && (
          <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
            <p className="text-sm font-medium text-red-800 mb-1">Cancellation Reason</p>
            <p className="text-sm text-red-600">{order.cancellation_reason}</p>
          </div>
        )}

        <div className="flex gap-2 pt-2">
          <Button variant="outline" size="sm" className="flex-1">
            <Eye className="h-4 w-4 mr-2" />
            View Details
          </Button>
          <Button variant="outline" size="sm" className="flex-1">
            <MessageCircle className="h-4 w-4 mr-2" />
            Message
          </Button>
          {(order.status === 'delivered' || order.status === 'paid') && (
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Invoice
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  // Calculate summary statistics
  const summaryStats = {
    total: filteredOrders.length,
    pending: filteredOrders.filter(o => o.status === 'pending').length,
    shipped: filteredOrders.filter(o => o.status === 'shipped').length,
    delivered: filteredOrders.filter(o => o.status === 'delivered').length,
    totalValue: filteredOrders.reduce((sum, order) => sum + order.amount, 0)
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50/30">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">My Orders</h1>
          <p className="text-lg text-slate-600">
            Track and manage your purchases and sales
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Total Orders</p>
                  <p className="text-3xl font-bold">{summaryStats.total}</p>
                </div>
                <ShoppingBag className="h-8 w-8 text-blue-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-sm bg-gradient-to-br from-yellow-500 to-orange-500 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-100 text-sm">Pending</p>
                  <p className="text-3xl font-bold">{summaryStats.pending}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-sm bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm">In Transit</p>
                  <p className="text-3xl font-bold">{summaryStats.shipped}</p>
                </div>
                <Truck className="h-8 w-8 text-purple-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-sm bg-gradient-to-br from-green-500 to-emerald-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm">Total Value</p>
                  <p className="text-3xl font-bold">{formatCurrency(summaryStats.totalValue)}</p>
                </div>
                <Euro className="h-8 w-8 text-green-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="border-0 shadow-sm mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                  <Input
                    placeholder="Search orders by ID, item, or seller..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="flex gap-3">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="paid">Paid</SelectItem>
                    <SelectItem value="shipped">Shipped</SelectItem>
                    <SelectItem value="delivered">Delivered</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={dateRange} onValueChange={setDateRange}>
                  <SelectTrigger className="w-36">
                    <Calendar className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Date" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Time</SelectItem>
                    <SelectItem value="week">Last Week</SelectItem>
                    <SelectItem value="month">Last Month</SelectItem>
                    <SelectItem value="quarter">Last Quarter</SelectItem>
                  </SelectContent>
                </Select>
                
                <Button variant="outline" onClick={fetchOrders}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Orders Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-white shadow-sm">
            <TabsTrigger value="all" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              All Orders
              <Badge variant="secondary" className="ml-1">
                {orders.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="purchases" className="flex items-center gap-2">
              <ShoppingBag className="h-4 w-4" />
              My Purchases
              <Badge variant="secondary" className="ml-1">
                {orders.filter(o => o.type === 'purchase').length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="sales" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              My Sales
              <Badge variant="secondary" className="ml-1">
                {orders.filter(o => o.type === 'sale').length}
              </Badge>
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            {loading ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {[...Array(4)].map((_, index) => (
                  <Card key={index} className="animate-pulse">
                    <CardHeader>
                      <div className="h-6 bg-slate-200 rounded w-3/4 mb-2"></div>
                      <div className="h-4 bg-slate-200 rounded w-1/2"></div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="h-4 bg-slate-200 rounded w-full"></div>
                        <div className="h-4 bg-slate-200 rounded w-2/3"></div>
                        <div className="h-8 bg-slate-200 rounded w-1/3"></div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filteredOrders.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filteredOrders.map((order) => (
                  <OrderCard key={order.id} order={order} />
                ))}
              </div>
            ) : (
              <Card className="text-center py-16">
                <CardContent>
                  <Package className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">
                    No orders found
                  </h3>
                  <p className="text-slate-600 mb-4">
                    {activeTab === 'all' 
                      ? "You don't have any orders yet. Start browsing to make your first purchase!"
                      : `You don't have any ${activeTab} yet.`
                    }
                  </p>
                  <Button className="bg-purple-600 hover:bg-purple-700">
                    <ShoppingBag className="h-4 w-4 mr-2" />
                    Browse Products
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
      
      <Footer />
    </div>
  );
};

export default OrdersPageWorking;