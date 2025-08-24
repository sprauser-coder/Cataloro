module.exports = {
  apps: [
    {
      name: 'cataloro-backend',
      script: 'server.py',
      cwd: '/var/www/cataloro/backend',
      interpreter: '/var/www/cataloro/venv/bin/python',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PORT: 8001,
        NODE_ENV: 'production'
      },
      error_file: '/var/log/pm2/cataloro-backend.err.log',
      out_file: '/var/log/pm2/cataloro-backend.out.log',
      log_file: '/var/log/pm2/cataloro-backend.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'cataloro-frontend',
      script: 'serve',
      args: '-s build -p 3000',
      cwd: '/var/www/cataloro/frontend',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '/var/log/pm2/cataloro-frontend.err.log',
      out_file: '/var/log/pm2/cataloro-frontend.out.log',
      log_file: '/var/log/pm2/cataloro-frontend.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};