/**
 * Admin Layout Component - Main coordinator for AdminPanel
 * Extracted from AdminPanel.js for better organization
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Users, 
  Package, 
  Building, 
  Database, 
  Settings, 
  Shield 
} from 'lucide-react';

// Tab Configuration
const getTabConfig = () => [
  { id: 'dashboard', label: 'Dashboard', shortLabel: 'Dashboard', icon: BarChart3 },
  { id: 'users', label: 'Users', shortLabel: 'Users', icon: Users, 
    permission: 'canAccessUserManagement' },
  { id: 'listings', label: 'Listings', shortLabel: 'Listings', icon: Package, 
    permission: 'canAccessListingsManagement' },
  { id: 'business', label: 'Business', shortLabel: 'Business', icon: Building },
  { id: 'cats', label: "Cat's", shortLabel: "Cat's", icon: Database, 
    permission: 'canAccessDatDatabase' },
  { id: 'site-settings', label: 'Site Settings', shortLabel: 'Settings', icon: Settings, 
    adminOnly: true },
  { id: 'administration', label: 'Administration', shortLabel: 'Admin', icon: Shield, 
    adminOnly: true }
];

// Tab Navigation Component
function TabNavigation({ activeTab, setActiveTab, tabs, isMobile = false }) {
  return (
    <div className={isMobile ? 
      "flex overflow-x-auto scrollbar-hide bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6" :
      "flex flex-wrap bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6"
    }>
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center space-x-2 px-4 py-3 font-medium transition-all duration-200 whitespace-nowrap
              ${isActive 
                ? 'bg-purple-600 text-white shadow-lg scale-105' 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-purple-600 dark:hover:text-purple-400'
              }
              ${isMobile ? 'flex-shrink-0' : 'flex-1 justify-center first:rounded-l-lg last:rounded-r-lg'}
            `}
          >
            <Icon className="w-4 h-4" />
            <span className={isMobile ? "text-sm" : "hidden md:block"}>
              {isMobile ? tab.shortLabel : tab.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}

// Admin Header Component
function AdminHeader({ user, onShowToast }) {
  return (
    <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 text-white mb-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Admin Panel</h1>
          <p className="text-purple-100 text-lg">
            Manage your marketplace with comprehensive tools and insights
          </p>
        </div>
        <div className="hidden md:flex items-center space-x-4">
          <div className="bg-white/20 backdrop-blur-md rounded-lg px-4 py-2">
            <p className="text-sm text-purple-100">Welcome back,</p>
            <p className="font-semibold">{user?.first_name || user?.email || 'Admin'}</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm">System Operational</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export { getTabConfig, TabNavigation, AdminHeader };