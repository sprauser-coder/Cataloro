/**
 * CATALORO - Mobile Admin Drawer Component
 * Optimized admin panel access for mobile devices
 */

import React, { useState } from 'react';
import { 
  X, 
  Shield, 
  Users, 
  Package, 
  BarChart3, 
  Settings, 
  Star,
  MessageCircle,
  DollarSign,
  Globe,
  Bell,
  Database,
  Zap,
  TrendingUp,
  Activity,
  ChevronRight,
  Grid3X3,
  Clock
} from 'lucide-react';
import { Link } from 'react-router-dom';

function MobileAdminDrawer({ isOpen, onClose }) {
  const [activeSection, setActiveSection] = useState(null);

  const adminSections = [
    {
      id: 'overview',
      title: 'Dashboard Overview',
      icon: BarChart3,
      color: 'bg-blue-500',
      items: [
        { label: 'Admin Dashboard', path: '/admin', icon: Shield },
        { label: 'Site Analytics', path: '/admin/analytics', icon: Activity },
        { label: 'Performance Monitor', path: '/admin/performance', icon: TrendingUp }
      ]
    },
    {
      id: 'users',
      title: 'User Management',
      icon: Users,
      color: 'bg-green-500',
      items: [
        { label: 'All Users', path: '/admin#users', icon: Users },
        { label: 'User Roles', path: '/admin#user-roles', icon: Shield },
        { label: 'User Analytics', path: '/admin#user-analytics', icon: BarChart3 }
      ]
    },
    {
      id: 'listings',
      title: 'Content Management',
      icon: Package,
      color: 'bg-purple-500',
      items: [
        { label: 'All Listings', path: '/admin#listings', icon: Package },
        { label: 'Pending Approval', path: '/admin#pending', icon: Clock },
        { label: 'Categories', path: '/admin#categories', icon: Grid3X3 }
      ]
    },
    {
      id: 'site',
      title: 'Site Settings',
      icon: Settings,
      color: 'bg-orange-500',
      items: [
        { label: 'Site Branding', path: '/admin#site-branding', icon: Globe },
        { label: 'Hero Selection', path: '/admin#hero', icon: Star },
        { label: 'Notifications', path: '/admin#notifications', icon: Bell }
      ]
    },
    {
      id: 'advanced',
      title: 'Advanced Tools',
      icon: Database,
      color: 'bg-red-500',
      items: [
        { label: 'System Monitor', path: '/admin#system', icon: Activity },
        { label: 'Cache Management', path: '/admin#cache', icon: Zap },
        { label: 'Database Tools', path: '/admin#database', icon: Database }
      ]
    }
  ];

  const handleSectionClick = (sectionId) => {
    if (activeSection === sectionId) {
      setActiveSection(null);
    } else {
      setActiveSection(sectionId);
    }
  };

  const handleItemClick = () => {
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Admin Drawer */}
      <div className={`fixed top-0 right-0 h-full w-80 bg-white dark:bg-gray-900 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out lg:hidden ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Admin Panel</h2>
              <p className="text-sm opacity-80">Mobile Dashboard</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Admin Sections */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 space-y-3">
            {adminSections.map((section) => {
              const SectionIcon = section.icon;
              const isActive = activeSection === section.id;
              
              return (
                <div key={section.id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                  {/* Section Header */}
                  <button
                    onClick={() => handleSectionClick(section.id)}
                    className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${section.color} rounded-lg flex items-center justify-center`}>
                        <SectionIcon className="w-4 h-4 text-white" />
                      </div>
                      <div className="text-left">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                          {section.title}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {section.items.length} tools
                        </p>
                      </div>
                    </div>
                    
                    <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform ${
                      isActive ? 'rotate-90' : ''
                    }`} />
                  </button>

                  {/* Section Items */}
                  {isActive && (
                    <div className="border-t border-gray-200 dark:border-gray-700">
                      {section.items.map((item, index) => {
                        const ItemIcon = item.icon;
                        return (
                          <Link
                            key={index}
                            to={item.path}
                            onClick={handleItemClick}
                            className="flex items-center space-x-3 p-3 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                          >
                            <ItemIcon className="w-4 h-4" />
                            <span className="text-sm">{item.label}</span>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Quick Actions Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="grid grid-cols-3 gap-2">
            <Link
              to="/admin#users"
              onClick={handleItemClick}
              className="flex flex-col items-center p-3 text-center bg-white dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <Users className="w-5 h-5 text-blue-500 mb-1" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Users</span>
            </Link>
            
            <Link
              to="/admin#listings"
              onClick={handleItemClick}
              className="flex flex-col items-center p-3 text-center bg-white dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <Package className="w-5 h-5 text-green-500 mb-1" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Listings</span>
            </Link>
            
            <Link
              to="/admin#analytics"
              onClick={handleItemClick}
              className="flex flex-col items-center p-3 text-center bg-white dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <BarChart3 className="w-5 h-5 text-purple-500 mb-1" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Analytics</span>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}

export default MobileAdminDrawer;