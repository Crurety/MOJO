# AI创作平台

一个功能完整的AI创作平台，支持脚本生成、图像生成、视频生成和广告设计等功能。

## 项目结构

```
├── backend/        # 后端API服务
├── frontend/       # 前端用户界面
├── admin/          # 后台管理系统
├── .github/        # GitHub Actions配置
└── README.md       # 项目说明文档
```

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy
- MySQL/SQLite
- Redis
- MongoDB

### 前端
- React 18
- TypeScript
- Vite
- Zustand (状态管理)
- React Router

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+ (或SQLite)
- Redis 7.0+
- MongoDB 5.0+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ai-creation-platform
   ```

2. **安装后端依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **安装前端依赖**
   ```bash
   cd ../frontend
   npm install
   ```

4. **安装后台依赖**
   ```bash
   cd ../admin
   npm install
   ```

5. **配置环境变量**
   - 复制 `.env.example` 文件为 `.env`
   - 填写相关配置信息

6. **启动服务**
   - 启动后端服务
     ```bash
     cd backend
     uvicorn app.main:app --reload
     ```
   - 启动前端服务
     ```bash
     cd frontend
     npm run dev
     ```
   - 启动后台服务
     ```bash
     cd admin
     npm run dev
     ```

## API文档

后端服务启动后，可通过以下地址访问API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 功能特性

### 核心功能
- 用户认证与授权
- 脚本生成
- 图像生成
- 视频生成
- 广告设计
- 权限管理
- 订单管理
- 支付集成 (微信、支付宝、银联)

### 技术特性
- 类型安全 (TypeScript + Pydantic)
- API速率限制
- 结构化日志
- 数据验证
- CI/CD集成
- 备份与恢复

## 部署

### 生产环境部署
1. **构建前端和后台**
   ```bash
   cd frontend && npm run build
   cd ../admin && npm run build
   ```

2. **配置生产环境变量**
   - 修改 `.env` 文件，填写生产环境配置

3. **启动服务**
   - 使用 Gunicorn 启动后端服务
     ```bash
     cd backend
     gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
     ```
   - 使用 Nginx 或其他 web 服务器部署前端和后台静态文件

## 开发指南

### 代码风格
- 后端: 遵循 PEP 8 规范
- 前端: 遵循 ESLint 规范

### 测试
- 运行后端测试
  ```bash
  cd backend
  python -m pytest
  ```

### 日志
- 日志文件位于 `backend/logs/` 目录
- 日志同时存储在 MongoDB 中

### 备份
- 运行备份脚本
  ```bash
  cd backend
  python app/scripts/backup.py
  ```

- 运行恢复脚本
  ```bash
  cd backend
  python app/scripts/restore.py
  ```

## 许可证

MIT License
