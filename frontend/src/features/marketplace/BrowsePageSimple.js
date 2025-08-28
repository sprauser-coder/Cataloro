import React from 'react';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';

const BrowsePageSimple = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-4xl font-light text-slate-900 mb-4 tracking-tight">
          Discover Amazing Deals
        </h1>
        <p className="text-lg text-slate-600 font-light mb-8">
          Browse thousands of products from trusted sellers
        </p>
        
        <div className="bg-white rounded-2xl p-12 text-center">
          <div className="text-6xl mb-4">🛍️</div>
          <h3 className="text-xl font-semibold text-slate-700 mb-2">New Browse Page Working!</h3>
          <p className="text-slate-500">This confirms the new routing and components are loaded correctly</p>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default BrowsePageSimple;