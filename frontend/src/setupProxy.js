const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/uploads',
    createProxyMiddleware({
      target: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug'
    })
  );
};