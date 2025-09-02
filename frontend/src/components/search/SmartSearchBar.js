/**
 * CATALORO - Smart Search Bar with AI-Powered Suggestions
 * Enhanced search component with intelligent suggestions and real-time search
 */

import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, Clock, TrendingUp, X } from 'lucide-react';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';

function SmartSearchBar({ onSearch, placeholder = "Search with AI...", className = "" }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const { user } = useAuth();
  const searchInputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Debounced search suggestions
  useEffect(() => {
    if (query.length >= 2) {
      const timeoutId = setTimeout(() => {
        fetchAISuggestions(query);
      }, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query]);

  // Load search history on component mount
  useEffect(() => {
    if (user?.id) {
      loadSearchHistory();
    }
  }, [user]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        !searchInputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchAISuggestions = async (searchQuery) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search/ai-suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          context: {
            previous_searches: searchHistory.slice(0, 3).map(h => h.query)
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('Error fetching AI suggestions:', error);
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSearchHistory = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search/history/${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setSearchHistory(data.history || []);
      }
    } catch (error) {
      console.error('Error loading search history:', error);
    }
  };

  const saveSearchHistory = async (searchQuery) => {
    if (!user?.id || !searchQuery.trim()) return;

    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search/save-history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          query: searchQuery.trim(),
          results_count: 0 // Will be updated after search results
        })
      });
      
      // Refresh search history
      loadSearchHistory();
    } catch (error) {
      console.error('Error saving search history:', error);
    }
  };

  const handleSearch = (searchQuery) => {
    const trimmedQuery = searchQuery.trim();
    if (trimmedQuery) {
      setQuery(trimmedQuery);
      setShowSuggestions(false);
      saveSearchHistory(trimmedQuery);
      onSearch(trimmedQuery);
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch(query);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSearch(suggestion);
  };

  const handleHistoryClick = (historyItem) => {
    handleSearch(historyItem.query);
  };

  const clearQuery = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    searchInputRef.current?.focus();
  };

  const handleInputFocus = () => {
    if (query.length >= 2 && suggestions.length > 0) {
      setShowSuggestions(true);
    } else if (query.length === 0 && searchHistory.length > 0) {
      setShowSuggestions(true);
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          {isLoading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
          ) : (
            <Search className="h-5 w-5 text-gray-400" />
          )}
        </div>
        
        <input
          ref={searchInputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          onFocus={handleInputFocus}
          placeholder={placeholder}
          className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-medium placeholder-gray-500 transition-all duration-200"
        />
        
        {/* AI Indicator */}
        <div className="absolute inset-y-0 right-0 flex items-center">
          {query && (
            <button
              onClick={clearQuery}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <div className="flex items-center px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-r-xl">
            <Sparkles className="h-4 w-4 text-white animate-pulse" />
            <span className="ml-1 text-xs font-medium text-white">AI</span>
          </div>
        </div>
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white rounded-xl shadow-lg border border-gray-200 max-h-96 overflow-y-auto"
        >
          {/* AI Suggestions */}
          {suggestions.length > 0 && (
            <div className="p-2">
              <div className="flex items-center px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                <Sparkles className="h-4 w-4 mr-2 text-blue-500" />
                AI Suggestions
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={`suggestion-${index}`}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-50 rounded-lg transition-colors duration-150 group"
                >
                  <div className="flex items-center">
                    <Search className="h-4 w-4 text-gray-400 mr-3 group-hover:text-blue-500" />
                    <span className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                      {suggestion}
                    </span>
                    <TrendingUp className="h-3 w-3 text-gray-300 ml-auto group-hover:text-blue-400" />
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Search History */}
          {query.length === 0 && searchHistory.length > 0 && (
            <div className="border-t border-gray-100 p-2">
              <div className="flex items-center px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                <Clock className="h-4 w-4 mr-2 text-gray-400" />
                Recent Searches
              </div>
              {searchHistory.slice(0, 5).map((historyItem, index) => (
                <button
                  key={`history-${index}`}
                  onClick={() => handleHistoryClick(historyItem)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-50 rounded-lg transition-colors duration-150 group"
                >
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 text-gray-400 mr-3 group-hover:text-blue-500" />
                    <span className="text-sm text-gray-700 group-hover:text-blue-600">
                      {historyItem.query}
                    </span>
                    <span className="text-xs text-gray-400 ml-auto">
                      {new Date(historyItem.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* No Suggestions */}
          {query.length >= 2 && suggestions.length === 0 && !isLoading && (
            <div className="p-4 text-center text-gray-500">
              <Search className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">No suggestions found</p>
              <p className="text-xs text-gray-400 mt-1">Try a different search term</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SmartSearchBar;