/**
 * CATALORO - Deployment Configuration
 * Central configuration for all deployment operations
 */

const path = require('path');

const deploymentConfig = {
  // Project Information
  project: {
    name: 'Cataloro Marketplace',
    version: '1.0.0',
    description: 'Ultra-modern marketplace web application',
    author: 'Cataloro Team'
  },

  // Paths Configuration
  paths: {
    root: path.resolve(__dirname, '..'),
    frontend: path.resolve(__dirname, '../frontend'),
    backend: path.resolve(__dirname, '../backend'),
    build: path.resolve(__dirname, '../build'),
    dist: path.resolve(__dirname, '../dist'),
    deployment: path.resolve(__dirname, '.'),
    logs: path.resolve(__dirname, '../logs'),
    backups: path.resolve(__dirname, '../backups')
  },

  // GitHub Configuration
  github: {
    enabled: true,
    repository: {
      name: 'cataloro-marketplace',
      owner: 'your-github-username', // Replace with actual GitHub username
      url: 'https://github.com/your-github-username/cataloro-marketplace.git',
      branch: 'main'
    },
    excludeFiles: [
      'node_modules/',
      '.env',
      '.env.local',
      '.env.production',
      'build/',
      'dist/',
      'logs/',
      'backups/',
      '*.log',
      '.DS_Store',
      'Thumbs.db'
    ]
  },

  // SSH Server Configuration
  ssh: {
    enabled: true,
    server: {
      host: '217.154.0.82',
      port: 22,
      username: 'root', // Default, can be overridden
      deployPath: '/var/www',
      backupPath: '/var/www/backups'
    },
    options: {
      connectTimeout: 30000,
      readyTimeout: 30000,
      keepaliveInterval: 10000
    }
  },

  // Build Configuration
  build: {
    frontend: {
      enabled: true,
      command: 'yarn build',
      outputDir: 'build',
      envFile: '.env.production'
    },
    backend: {
      enabled: true,
      requirements: 'requirements.txt',
      excludeFiles: [
        '__pycache__/',
        '*.pyc',
        '.pytest_cache/',
        'venv/',
        '.venv/'
      ]
    }
  },

  // Environment Management
  environment: {
    production: {
      NODE_ENV: 'production',
      REACT_APP_ENV: 'production'
    },
    staging: {
      NODE_ENV: 'staging',
      REACT_APP_ENV: 'staging'
    }
  },

  // Deployment Steps
  deploymentSteps: {
    preDeployment: [
      'validateEnvironment',
      'checkDependencies',
      'runTests',
      'createBackup'
    ],
    build: [
      'buildFrontend',
      'prepareFrontend',
      'prepareBackend',
      'generateManifest'
    ],
    deployment: [
      'deployToGithub',
      'deployToServer',
      'updateDatabase',
      'restartServices'
    ],
    postDeployment: [
      'verifyDeployment',
      'runHealthChecks',
      'sendNotification',
      'cleanupTemporary'
    ]
  },

  // Health Check Configuration
  healthChecks: {
    enabled: true,
    endpoints: [
      '/api/health',
      '/api/status'
    ],
    timeout: 10000,
    retries: 3
  },

  // Backup Configuration
  backup: {
    enabled: true,
    retentionDays: 30,
    includeDatabase: true,
    includeLogs: false,
    compressionLevel: 6
  },

  // Notification Configuration
  notifications: {
    enabled: true,
    channels: {
      console: true,
      file: true,
      webhook: false // Can be configured later
    },
    webhookUrl: null // Set if using webhook notifications
  },

  // Security Configuration
  security: {
    validateChecksums: true,
    requireHttps: true,
    sanitizeEnvironment: true
  }
};

module.exports = deploymentConfig;