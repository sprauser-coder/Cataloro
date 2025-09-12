/**
 * CATALORO - Comprehensive PDF Export Center
 * Advanced data export functionality with customizable reports
 */

import React, { useState, useEffect } from 'react';
import { 
  Download,
  FileText,
  Users,
  Package,
  DollarSign,
  TrendingUp,
  Calendar,
  Filter,
  Settings,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  Eye,
  BarChart3,
  PieChart,
  Database,
  Server,
  Bell,
  Mail,
  ShoppingCart,
  CreditCard,
  Target,
  Activity
} from 'lucide-react';

const PDFExportCenter = ({ showToast }) => {
  const [selectedExports, setSelectedExports] = useState([]);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
    end: new Date().toISOString().split('T')[0] // Today
  });
  const [exportFormat, setExportFormat] = useState('comprehensive');
  const [customOptions, setCustomOptions] = useState({
    includeCharts: true,
    includeImages: true,
    includeAnalytics: true,
    watermark: true,
    headerFooter: true
  });

  // Available export types
  const exportTypes = [
    {
      id: 'users',
      title: 'User Management Report',
      description: 'Complete user database with profiles, activity, and statistics',
      icon: Users,
      color: 'blue',
      estimatedSize: '2-5 MB',
      includes: ['User profiles', 'Registration dates', 'Activity logs', 'Ratings', 'Transaction history']
    },
    {
      id: 'listings',
      title: 'Listings & Products Report',
      description: 'All marketplace listings with details and performance metrics',
      icon: Package,
      color: 'green',
      estimatedSize: '3-8 MB',
      includes: ['Product details', 'Images', 'Pricing history', 'Views & favorites', 'Seller information']
    },
    {
      id: 'transactions',
      title: 'Financial Transactions Report',
      description: 'Complete transaction history and revenue analytics',
      icon: DollarSign,
      color: 'yellow',
      estimatedSize: '1-3 MB',
      includes: ['Transaction records', 'Payment methods', 'Revenue by period', 'Fee calculations', 'Refunds']
    },
    {
      id: 'analytics',
      title: 'Platform Analytics Report',
      description: 'Comprehensive performance metrics and user behavior',
      icon: BarChart3,
      color: 'purple',
      estimatedSize: '4-10 MB',
      includes: ['Traffic analytics', 'Conversion rates', 'User engagement', 'Popular listings', 'Growth metrics']
    },
    {
      id: 'orders',
      title: 'Orders & Fulfillment Report',
      description: 'Order management and delivery tracking information',
      icon: ShoppingCart,
      color: 'orange',
      estimatedSize: '2-6 MB',
      includes: ['Order details', 'Delivery status', 'Customer feedback', 'Processing times', 'Returns']
    },
    {
      id: 'communications',
      title: 'Communications Log',
      description: 'Message history, notifications, and system communications',
      icon: Mail,
      color: 'indigo',
      estimatedSize: '1-4 MB',
      includes: ['Message threads', 'Notifications sent', 'Email campaigns', 'System alerts', 'Support tickets']
    },
    {
      id: 'system',
      title: 'System Health Report',
      description: 'Technical performance, errors, and maintenance logs',
      icon: Server,
      color: 'red',
      estimatedSize: '1-2 MB',
      includes: ['Error logs', 'Performance metrics', 'Database status', 'Security events', 'Backup history']
    },
    {
      id: 'business',
      title: 'Business Intelligence Report',
      description: 'Strategic insights, trends, and forecasting data',
      icon: Target,
      color: 'teal',
      estimatedSize: '3-7 MB',
      includes: ['Market trends', 'Competitor analysis', 'Growth forecasts', 'ROI calculations', 'KPI dashboard']
    }
  ];

  // Handle export type selection
  const toggleExportType = (typeId) => {
    setSelectedExports(prev => 
      prev.includes(typeId) 
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    );
  };

  // Select all exports
  const selectAll = () => {
    setSelectedExports(exportTypes.map(type => type.id));
  };

  // Clear all selections
  const clearAll = () => {
    setSelectedExports([]);
  };

  // Handle PDF export
  const handleExport = async () => {
    if (selectedExports.length === 0) {
      showToast('Please select at least one export type', 'warning');
      return;
    }

    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulate export progress
      const progressInterval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + Math.random() * 15;
        });
      }, 500);

      // Get backend URL from environment
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      const exportData = {
        types: selectedExports,
        dateRange,
        format: exportFormat,
        options: customOptions
      };

      const response = await fetch(`${backendUrl}/api/admin/export-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(exportData)
      });

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      link.download = `cataloro-export-${timestamp}.pdf`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      clearInterval(progressInterval);
      setExportProgress(100);
      
      setTimeout(() => {
        setIsExporting(false);
        setExportProgress(0);
        showToast('PDF export completed successfully!', 'success');
      }, 1000);

    } catch (error) {
      console.error('Export error:', error);
      setIsExporting(false);
      setExportProgress(0);
      showToast(`Export failed: ${error.message}`, 'error');
    }
  };

  // Get estimated total file size
  const getEstimatedSize = () => {
    if (selectedExports.length === 0) return '0 MB';
    
    const selectedTypes = exportTypes.filter(type => selectedExports.includes(type.id));
    const totalMin = selectedTypes.reduce((sum, type) => {
      const [min] = type.estimatedSize.split('-').map(s => parseInt(s));
      return sum + min;
    }, 0);
    const totalMax = selectedTypes.reduce((sum, type) => {
      const max = type.estimatedSize.includes('-') 
        ? parseInt(type.estimatedSize.split('-')[1])
        : parseInt(type.estimatedSize);
      return sum + max;
    }, 0);
    
    return `${totalMin}-${totalMax} MB`;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2 flex items-center">
              <Download className="w-8 h-8 mr-3" />
              PDF Export Center
            </h2>
            <p className="text-green-100">Export comprehensive reports and data in professional PDF format</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-green-100">Selected: {selectedExports.length} reports</div>
              <div className="text-sm text-green-100">Est. Size: {getEstimatedSize()}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Export Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Date Range & Format Selection */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Export Settings
          </h3>
          
          <div className="space-y-4">
            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date Range
              </label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="date"
                  value={dateRange.start}
                  onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                />
                <input
                  type="date"
                  value={dateRange.end}
                  onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                />
              </div>
            </div>

            {/* Export Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Format
              </label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="comprehensive">Comprehensive Report</option>
                <option value="summary">Executive Summary</option>
                <option value="detailed">Detailed Analysis</option>
                <option value="technical">Technical Report</option>
              </select>
            </div>

            {/* Custom Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Include Options
              </label>
              <div className="space-y-2">
                {[
                  { key: 'includeCharts', label: 'Charts & Graphs' },
                  { key: 'includeImages', label: 'Product Images' },
                  { key: 'includeAnalytics', label: 'Analytics Data' },
                  { key: 'watermark', label: 'Company Watermark' },
                  { key: 'headerFooter', label: 'Header & Footer' }
                ].map((option) => (
                  <label key={option.key} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={customOptions[option.key]}
                      onChange={(e) => setCustomOptions(prev => ({
                        ...prev,
                        [option.key]: e.target.checked
                      }))}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{option.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Export Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Export Controls
          </h3>
          
          <div className="space-y-4">
            {/* Selection Controls */}
            <div className="flex space-x-2">
              <button
                onClick={selectAll}
                className="flex-1 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg text-sm font-medium hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              >
                Select All
              </button>
              <button
                onClick={clearAll}
                className="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                Clear All
              </button>
            </div>

            {/* Export Progress */}
            {isExporting && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Generating PDF...</span>
                  <span className="text-gray-900 dark:text-white font-medium">{Math.round(exportProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${exportProgress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Export Button */}
            <button
              onClick={handleExport}
              disabled={isExporting || selectedExports.length === 0}
              className={`w-full px-6 py-3 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center space-x-2 ${
                isExporting || selectedExports.length === 0
                  ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-600 to-blue-600 text-white hover:from-green-700 hover:to-blue-700 transform hover:scale-105'
              }`}
            >
              {isExporting ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Generating PDF...</span>
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  <span>Export Selected Reports</span>
                </>
              )}
            </button>

            {/* Export Summary */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Export Summary:</div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Reports Selected:</span>
                  <span className="font-medium text-gray-900 dark:text-white">{selectedExports.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Date Range:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {Math.ceil((new Date(dateRange.end) - new Date(dateRange.start)) / (1000 * 60 * 60 * 24))} days
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Format:</span>
                  <span className="font-medium text-gray-900 dark:text-white capitalize">{exportFormat}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Exports */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Recent Exports
          </h3>
          
          <div className="space-y-3">
            {[
              { date: '2025-09-08', type: 'Complete Report', size: '12.5 MB', status: 'completed' },
              { date: '2025-09-07', type: 'User Analytics', size: '4.2 MB', status: 'completed' },
              { date: '2025-09-06', type: 'Financial Report', size: '2.8 MB', status: 'completed' }
            ].map((export_, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">{export_.type}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{export_.date} • {export_.size}</div>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <button className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Export Types Grid */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Available Export Types</h3>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Select the reports you want to include in your PDF export
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {exportTypes.map((type) => {
            const Icon = type.icon;
            const isSelected = selectedExports.includes(type.id);
            
            return (
              <div
                key={type.id}
                onClick={() => toggleExportType(type.id)}
                className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 transform hover:scale-105 ${
                  isSelected
                    ? `border-${type.color}-500 bg-${type.color}-50 dark:bg-${type.color}-900/20 shadow-lg`
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute top-2 right-2">
                    <CheckCircle className={`w-5 h-5 text-${type.color}-600`} />
                  </div>
                )}

                {/* Icon */}
                <div className={`w-12 h-12 rounded-lg bg-${type.color}-100 dark:bg-${type.color}-900/30 flex items-center justify-center mb-3`}>
                  <Icon className={`w-6 h-6 text-${type.color}-600 dark:text-${type.color}-400`} />
                </div>

                {/* Content */}
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1 text-sm">{type.title}</h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">{type.description}</p>
                  
                  {/* Details */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500 dark:text-gray-400">Size:</span>
                      <span className="font-medium text-gray-700 dark:text-gray-300">{type.estimatedSize}</span>
                    </div>
                    
                    <div className="space-y-1">
                      <div className="text-xs text-gray-500 dark:text-gray-400">Includes:</div>
                      <div className="flex flex-wrap gap-1">
                        {type.includes.slice(0, 2).map((item, index) => (
                          <span key={index} className={`text-xs px-2 py-1 bg-${type.color}-100 dark:bg-${type.color}-900/20 text-${type.color}-700 dark:text-${type.color}-300 rounded`}>
                            {item}
                          </span>
                        ))}
                        {type.includes.length > 2 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            +{type.includes.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PDFExportCenter;