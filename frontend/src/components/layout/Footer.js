import React, { useState, useEffect } from 'react';

const Footer = () => {
  const [siteSettings, setSiteSettings] = useState({
    site_name: 'Cataloro',
    footer_text: 'Your trusted marketplace for amazing deals'
  });
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <footer className="mt-auto bg-slate-50 border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-center md:text-left">
            <p className="text-slate-600 font-light">
              © 2025 {siteSettings.site_name}. All rights reserved.
            </p>
            <p className="text-sm text-slate-500 font-light">
              {siteSettings.footer_text}
            </p>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-slate-500">
            <div className="flex items-center space-x-2">
              <span className="font-light">Version 1.6.5</span>
              <span className="w-1 h-1 bg-slate-400 rounded-full"></span>
              <span className="font-light">
                {currentTime.toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;