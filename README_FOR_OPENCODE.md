# Deployment Instructions for OpenCode (OpenCode 部署说明书)

> [!IMPORTANT]
> **To OpenCode Assistant:**
> This repository is a multi-service project (Student Front/Back, Admin Front/Back, PostgreSQL DB). Please follow these steps precisely to ensure a successful deployment on `campus.gzyichenai.com`.

## 1. Pre-deployment Checklist (重要检查)
- **Port Check**: Please run `netstat -tunlp` to check if ports **80** and **443** are available. 
  - If occupied by another Nginx, please merge the configuration in `./nginx.conf` into the host's Nginx configuration.
  - If ports are free, proceed with Docker deployment.
- **Sensitive Files**: The user will manually upload the `certs/` folder and the `.env` file to the project root. **Verify these files exist before starting.**

## 2. Directory Structure (项目结构)
- `/backend`: Core Python API (Student facing).
- `/admin/frontend`: Vue Admin Dashboard.
- `/admin/backend`: Admin API.
- `/fronted`: Student H5 App.
- `/nginx.conf`: Master Reverse Proxy configuration.
- `/docker-compose.yml`: Service orchestration.

## 3. Step-by-Step Deployment (操作流程)

1.  **Environment Preparation**:
    - Copy `.env.production` to `.env`.
    - Ensure SSL certificates are renamed to `campus.pem` and `campus.key` inside the `certs/` folder.
2.  **Container Launch**:
    - Run `docker-compose up -d --build`.
3.  **Data Initialization & Seeding (关键)**:
    - Once containers are running, execute the initialization script:
      ```bash
      chmod +x init_production_data.sh
      ./init_production_data.sh
      ```
    - This will create the database schema and inject initial exercise/course data.

## 4. Troubleshooting (常见问题)
- If SSL handshake fails, check if `certs/campus.pem` is a valid bundle.
- If frontend cannot connect to API, ensure `proxy_pass` targets in `nginx.conf` match the internal container names.
