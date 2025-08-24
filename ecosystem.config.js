module.exports = {
  apps: [{
    name: 'cataloro-backend',
    script: 'server.py',
    cwd: '/app/backend',
    interpreter: 'python3',
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
  }]
};