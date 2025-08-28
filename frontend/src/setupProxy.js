const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/uploads',
    createProxyMiddleware({
      target: process.env.REACT_APP_BACKEND_URL || 'http://217.154.0.82',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug'
    })
  );
};