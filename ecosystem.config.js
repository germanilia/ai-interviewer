module.exports = {
  apps: [
    {
      name: 'ai-interviewer-backend',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 9000 --reload',
      cwd: './backend',
      interpreter: 'python3.11',
      env: {
        NODE_ENV: 'development',
        APP_ENV: 'development'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      log_file: './logs/backend.log',
      out_file: './logs/backend-out.log',
      error_file: './logs/backend-error.log',
      time: true
    },
    {
      name: 'ai-interviewer-client',
      script: 'npm',
      args: 'start',
      cwd: './client',
      env: {
        NODE_ENV: 'development'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      log_file: './logs/client.log',
      out_file: './logs/client-out.log',
      error_file: './logs/client-error.log',
      time: true
    }
  ]
};
