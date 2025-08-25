import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));

// CRITICAL FIX: Only use StrictMode in development to prevent authentication race conditions
// StrictMode intentionally double-invokes effects which causes AuthProvider token loops
const AppWrapper = process.env.NODE_ENV === 'development' 
  ? () => (
      <React.StrictMode>
        <App />
      </React.StrictMode>
    )
  : () => <App />;

root.render(<AppWrapper />);
