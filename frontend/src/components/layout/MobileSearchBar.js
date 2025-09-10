/**
 * CATALORO - Mobile Search Bar Component
 * Enhanced mobile search with voice search, suggestions, and touch optimization
 */

import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Mic, Camera, Filter, ScanLine } from 'lucide-react';

function MobileSearchBar({ onSearch, placeholder = "Search catalysts...", className = "", initialValue = "" }) {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const inputRef = useRef(null);
  const recognition = useRef(null);

  useEffect(() => {
    // Load recent searches
    const saved = localStorage.getItem('cataloro_recent_searches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (error) {
        console.error('Error loading recent searches:', error);
      }
    }

    // Initialize speech recognition for mobile
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = 'en-US';

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setQuery(transcript);
        handleSearch(transcript);
        setIsListening(false);
      };

      recognition.current.onerror = () => {
        setIsListening(false);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Generate suggestions based on query
  useEffect(() => {
    if (query.length > 1) {
      const mockSuggestions = [
        'BMW catalytic converter',
        'Mercedes catalyst',
        'Ford exhaust catalyst',
        'Audi catalytic converter',
        'Volkswagen catalyst',
        'Ceramic catalyst',
        'Metallic catalyst',
        'Diesel particulate filter'
      ].filter(suggestion => 
        suggestion.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5);
      
      setSuggestions(mockSuggestions);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query]);

  const handleSearch = (searchQuery = query) => {
    if (searchQuery.trim()) {
      // Save to recent searches
      const newRecentSearches = [
        searchQuery,
        ...recentSearches.filter(s => s !== searchQuery)
      ].slice(0, 10);
      
      setRecentSearches(newRecentSearches);
      localStorage.setItem('cataloro_recent_searches', JSON.stringify(newRecentSearches));
      
      // Perform search
      onSearch(searchQuery);
      setShowSuggestions(false);
      inputRef.current?.blur();
    }
  };

  const handleVoiceSearch = () => {
    if (recognition.current && !isListening) {
      setIsListening(true);
      recognition.current.start();
    }
  };

  const handleCameraSearch = () => {
    // Trigger camera for visual search (future implementation)
    navigator.mediaDevices?.getUserMedia({ video: true })
      .then(stream => {
        // Handle camera stream for visual search
        console.log('Camera search activated');
        // Future: Implement visual search functionality
        stream.getTracks().forEach(track => track.stop());
      })
      .catch(error => {
        console.log('Camera not available:', error);
      });
  };

  const clearSearch = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const selectSuggestion = (suggestion) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
          <Search className="w-5 h-5" />
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          onFocus={() => setShowSuggestions(query.length > 1 || recentSearches.length > 0)}
          placeholder={placeholder}
          className="w-full pl-10 pr-20 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
        />

        {/* Action Buttons */}
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
          {query && (
            <button
              onClick={clearSearch}
              className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          
          {/* Voice Search */}
          {recognition.current && (
            <button
              onClick={handleVoiceSearch}
              className={`p-1.5 rounded-full transition-colors ${
                isListening 
                  ? 'text-red-500 bg-red-100 dark:bg-red-900/30 animate-pulse' 
                  : 'text-gray-400 hover:text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30'
              }`}
            >
              <Mic className="w-4 h-4" />
            </button>
          )}

          {/* Camera Search */}
          <button
            onClick={handleCameraSearch}
            className="p-1.5 text-gray-400 hover:text-green-500 hover:bg-green-100 dark:hover:bg-green-900/30 rounded-full transition-colors"
          >
            <ScanLine className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search Suggestions Dropdown */}
      {showSuggestions && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto">
          {/* Recent Searches */}
          {recentSearches.length > 0 && query.length === 0 && (
            <div className="p-3 border-b border-gray-100 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Recent Searches</h4>
              {recentSearches.slice(0, 5).map((search, index) => (
                <button
                  key={index}
                  onClick={() => selectSuggestion(search)}
                  className="block w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {search}
                </button>
              ))}
            </div>
          )}

          {/* Search Suggestions */}
          {suggestions.length > 0 && (
            <div className="p-3">
              <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Suggestions</h4>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => selectSuggestion(suggestion)}
                  className="block w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <span className="font-medium">{suggestion.split(query.toLowerCase())[0]}</span>
                  <span className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">
                    {query}
                  </span>
                  <span>{suggestion.split(query.toLowerCase())[1]}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MobileSearchBar;