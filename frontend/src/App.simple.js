/**
 * CATALORO - Simplified App for Debugging
 */

import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold text-blue-600">
        🎉 Cataloro Marketplace - Debug Mode
      </h1>
      <p className="text-gray-600 mt-4">
        React app is working! Now testing full components...
      </p>
      
      <div className="bg-white p-6 rounded-lg shadow-md mt-8 max-w-md">
        <h2 className="text-xl font-semibold mb-4">Test Login Form</h2>
        <input 
          type="email" 
          name="email"
          placeholder="Email" 
          className="w-full p-3 border rounded mb-4"
        />
        <input 
          type="password"
          name="password" 
          placeholder="Password" 
          className="w-full p-3 border rounded mb-4"
        />
        <button 
          type="submit"
          className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700"
        >
          Test Button
        </button>
      </div>
    </div>
  );
}

export default App;