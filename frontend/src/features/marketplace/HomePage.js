import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { Search, Package, TrendingUp, Shield, Star } from 'lucide-react';

const HomePage = () => {
  const { user } = useAuth();
  const [siteSettings, setSiteSettings] = useState({
    site_name: 'Cataloro',
    hero_title: 'Your Trusted Marketplace',
    hero_subtitle: 'Discover amazing deals and sell with confidence on Cataloro',
    hero_height: '600px'
  });

  const getHeroStyle = () => ({
    minHeight: siteSettings?.hero_height || '600px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6366f1 100%)'
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      {/* Dynamic Hero Section */}
      <div className="border-b border-gray-200" style={getHeroStyle()}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-light text-white mb-6 tracking-tight">
              {siteSettings.hero_title}
            </h1>
            <p className="text-xl text-purple-100 mb-8 font-light max-w-2xl mx-auto">
              {siteSettings.hero_subtitle}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/browse">
                <Button size="lg" className="bg-white text-purple-700 hover:bg-purple-50 font-light px-8 py-3 rounded-xl text-lg">
                  🛍️ Start Shopping
                </Button>
              </Link>
              {user && (
                <Link to="/sell">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-purple-700 font-light px-8 py-3 rounded-xl text-lg">
                    💰 Start Selling
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-light text-slate-900 mb-4">Why Choose Cataloro?</h2>
          <p className="text-lg text-slate-600 font-light">Experience the future of online marketplace</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="text-center border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 rounded-2xl flex items-center justify-center">
                <Shield className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">Secure Transactions</h3>
              <p className="text-slate-600 font-light">Advanced security measures protect every transaction on our platform.</p>
            </CardContent>
          </Card>

          <Card className="text-center border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-2xl flex items-center justify-center">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">Best Prices</h3>
              <p className="text-slate-600 font-light">Find the most competitive prices from verified sellers worldwide.</p>
            </CardContent>
          </Card>

          <Card className="text-center border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-2xl flex items-center justify-center">
                <Star className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">Quality Guaranteed</h3>
              <p className="text-slate-600 font-light">Every product is verified for quality and authenticity.</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white border-t border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-purple-600 mb-2">10K+</div>
              <div className="text-slate-600 font-light">Happy Customers</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">50K+</div>
              <div className="text-slate-600 font-light">Products Listed</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600 mb-2">99.9%</div>
              <div className="text-slate-600 font-light">Uptime</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-600 mb-2">24/7</div>
              <div className="text-slate-600 font-light">Support</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-3xl p-12 text-center">
          <h2 className="text-3xl font-light text-white mb-4">Ready to Get Started?</h2>
          <p className="text-xl text-purple-100 mb-8 font-light">Join thousands of satisfied buyers and sellers today</p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/browse">
              <Button size="lg" className="bg-white text-purple-700 hover:bg-purple-50 font-light px-8 py-3 rounded-xl">
                Browse Products
              </Button>
            </Link>
            {!user && (
              <Link to="/auth">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-purple-700 font-light px-8 py-3 rounded-xl">
                  Join Now
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default HomePage;