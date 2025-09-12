import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  Languages, 
  MapPin, 
  Shield, 
  RefreshCw,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Users,
  Settings
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import LanguageSelector from './LanguageSelector';
import RegionSelector from './RegionSelector';

const LocalizationDashboard = ({ className = '' }) => {
  const [analytics, setAnalytics] = useState(null);
  const [languages, setLanguages] = useState([]);
  const [regions, setRegions] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [selectedRegion, setSelectedRegion] = useState('US');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLocalizationData();
    
    // Load from localStorage
    const savedLanguage = localStorage.getItem('preferred_language');
    const savedRegion = localStorage.getItem('preferred_region');
    if (savedLanguage) setSelectedLanguage(savedLanguage);
    if (savedRegion) setSelectedRegion(savedRegion);
  }, []);

  const fetchLocalizationData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const [analyticsRes, languagesRes, regionsRes] = await Promise.all([
        fetch(`${backendUrl}/api/v2/phase6/i18n/analytics`),
        fetch(`${backendUrl}/api/v2/phase6/i18n/languages`),
        fetch(`${backendUrl}/api/v2/phase6/i18n/regions`)
      ]);

      const [analyticsData, languagesData, regionsData] = await Promise.all([
        analyticsRes.json(),
        languagesRes.json(),
        regionsRes.json()
      ]);

      if (analyticsData.success) setAnalytics(analyticsData.analytics);
      if (languagesData.success) setLanguages(languagesData.languages);
      if (regionsData.success) setRegions(regionsData.regions);

    } catch (error) {
      console.error('Failed to fetch localization data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getComplianceStatus = async (regionCode) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/i18n/compliance/${regionCode}`);
      const data = await response.json();
      
      if (data.success) {
        return data.compliance_status;
      }
    } catch (error) {
      console.error('Failed to fetch compliance status:', error);
    }
    return null;
  };

  const handleLanguageChange = (language) => {
    setSelectedLanguage(language.code);
    // Here you would typically apply the language change to the entire app
    console.log('Language changed to:', language);
  };

  const handleRegionChange = (region) => {
    setSelectedRegion(region.code);
    // Here you would typically apply the region change to the entire app
    console.log('Region changed to:', region);
  };

  const getCompletionColor = (percentage) => {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading localization dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <Globe className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Localization & Internationalization
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Multi-language support and regional compliance management
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchLocalizationData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Language and Region Selectors */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Current Localization Settings
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Language Preference
            </label>
            <LanguageSelector
              selectedLanguage={selectedLanguage}
              onLanguageChange={handleLanguageChange}
              showNativeName={true}
              size="large"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Region & Currency
            </label>
            <RegionSelector
              selectedRegion={selectedRegion}
              onRegionChange={handleRegionChange}
              showCurrency={true}
              showCompliance={true}
              size="large"
            />
          </div>
        </div>
      </div>

      {/* Overview Stats */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Languages className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.overview.enabled_languages}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Enabled Languages</div>
                <div className="text-sm text-blue-600">
                  {analytics.overview.total_languages} total available
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <MapPin className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.overview.enabled_regions}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Supported Regions</div>
                <div className="text-sm text-green-600">
                  Global marketplace coverage
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <BarChart3 className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.overview.translation_keys}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Translation Keys</div>
                <div className="text-sm text-purple-600">
                  Ready for localization
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <Shield className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Object.keys(analytics.regions).length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Compliance Regions</div>
                <div className="text-sm text-orange-600">
                  GDPR, CCPA, and more
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Language Translation Status */}
      {analytics && analytics.languages && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Translation Completion Status
            </h3>
            
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(analytics.languages).map(([name, data]) => ({
                name: name,
                completion: data.completion_percentage
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="completion" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Language Details
            </h3>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {Object.entries(analytics.languages).map(([name, data], index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="font-medium text-gray-900 dark:text-white">{name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">({data.code})</div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-20 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          data.completion_percentage >= 90 ? 'bg-green-500' :
                          data.completion_percentage >= 70 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${data.completion_percentage}%` }}
                      />
                    </div>
                    <span className={`text-sm font-medium ${getCompletionColor(data.completion_percentage)}`}>
                      {data.completion_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Regional Compliance */}
      {analytics && analytics.regions && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Regional Compliance Overview
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(analytics.regions).map(([name, data], index) => (
              <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900 dark:text-white">{name}</h4>
                  <div className="text-sm text-gray-600 dark:text-gray-400">({data.code})</div>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Requirements:</span>
                    <span className="font-medium text-gray-900 dark:text-white">{data.requirements}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Languages:</span>
                    <span className="font-medium text-gray-900 dark:text-white">{data.supported_languages}</span>
                  </div>
                </div>
                
                <button
                  onClick={() => getComplianceStatus(data.code)}
                  className="mt-3 w-full flex items-center justify-center space-x-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                >
                  <Shield className="w-4 h-4" />
                  <span>Check Compliance</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analytics && analytics.recommendations && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Localization Recommendations
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analytics.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="p-1 bg-blue-100 dark:bg-blue-900/30 rounded">
                  <Settings className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white">{recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LocalizationDashboard;