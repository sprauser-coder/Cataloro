module.exports = {
  apps: [
    {
      name: 'cataloro-backend',
      script: 'server.py',
      cwd: '/var/www/cataloro/backend',
      interpreter: '/usr/bin/python3.11',
      env: {
        PYTHONPATH: '/var/www/cataloro/backend',
        NODE_ENV: 'production'
      },
      restart_delay: 1000,
      max_restarts: 5,
      min_uptime: '10s',
      error_file: '/var/www/cataloro/logs/backend-error.log',
      out_file: '/var/www/cataloro/logs/backend-out.log',
      log_file: '/var/www/cataloro/logs/backend.log'
    },
    {
      name: 'cataloro-frontend',
      script: '/usr/bin/serve',
      args: '-s build -p 3000',
      cwd: '/var/www/cataloro/frontend',
      env: {
        NODE_ENV: 'production'
      },
      restart_delay: 1000,
      max_restarts: 5,
      min_uptime: '10s',
      error_file: '/var/www/cataloro/logs/frontend-error.log',
      out_file: '/var/www/cataloro/logs/frontend-out.log',
      log_file: '/var/www/cataloro/logs/frontend.log'
    }
  ]
};