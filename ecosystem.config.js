module.exports = {
    apps: [
        {
            name: 'cataloro-backend',
            script: 'server.py',
            interpreter: '/usr/bin/python3.11',
            cwd: '/var/www/cataloro/backend',
            env: {
                NODE_ENV: 'production',
                PYTHONPATH: '/var/www/cataloro/backend:/usr/local/lib/python3.11/site-packages'
            },
            autorestart: true,
            watch: false,
            max_memory_restart: '1G',
            error_file: '/var/www/cataloro/logs/backend-error.log',
            out_file: '/var/www/cataloro/logs/backend-out.log',
            log_file: '/var/www/cataloro/logs/backend.log'
        },
        {
            name: 'cataloro-frontend',
            script: 'serve',
            args: ['-s', 'build', '-l', '3000'],
            cwd: '/var/www/cataloro/frontend',
            env: {
                NODE_ENV: 'production'
            },
            autorestart: true,
            watch: false,
            max_memory_restart: '500M',
            error_file: '/var/www/cataloro/logs/frontend-error.log',
            out_file: '/var/www/cataloro/logs/frontend-out.log',
            log_file: '/var/www/cataloro/logs/frontend.log'
        }
    ]
};