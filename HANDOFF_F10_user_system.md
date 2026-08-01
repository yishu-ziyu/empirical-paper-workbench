# Handoff: F10 - 用户体系（登录/注册/权限管理）

## 目标
为 econpaper 实现完整的用户体系，包括用户注册、登录认证、会话管理和权限控制，为多用户部署和后续功能（项目管理、Docker 部署）奠定基础。

## 背景
- PostgresSaver 持久化已完成 ✅（数据库连接已就绪）
- 当前无用户概念，所有 session 匿名
- 后端 config.py 已有数据库连接配置（`CHECKPOINT_DB_URL`）
- 需要新增用户表 + 认证路由 + 前端登录/注册页面

## 具体改动

### 1. 后端：用户模型与数据库迁移

在 `backend/models/` 下创建用户模型：

```python
# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

### 2. 后端：认证依赖

- 安装依赖：`pip install "passlib[bcrypt]" python-jose[cryptography] sqlalchemy asyncpg`
- 实现密码哈希（passlib bcrypt）
- 实现 JWT 令牌生成与验证（python-jose）
- 实现 `get_current_user` 依赖注入（从 Authorization header 解析 token）
- Token 有效期：24 小时

### 3. 后端：认证路由

创建 `backend/routers/auth.py`：

| 端点 | 方法 | 说明 |
|------|------|------|
| /auth/register | POST | 用户注册（email/username/password） |
| /auth/login | POST | 用户登录（返回 access_token） |
| /auth/me | GET | 获取当前用户信息 |
| /auth/refresh | POST | 刷新 access_token |
| /auth/logout | POST | 退出登录（可选：黑名单 token） |

### 4. 后端：Session 与用户关联

- 在 `facade.py` 中增加 `create_session` 的用户 ID 参数
- 新增 `GET /sessions` 端点：返回当前用户的所有 session
- 新增 `DELETE /sessions/{id}` 端点：删除 session
- 各 session 操作端点需验证 session 所有权

### 5. 后端：数据库初始化

在 `backend/config.py` 中添加数据库配置：
```python
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://mahaoxuan@localhost:5432/econpaper",
)
```

创建 `backend/database.py`：
- SQLAlchemy async engine + session factory
- 启动时自动创建表（`Base.metadata.create_all`）
- 提供 `get_db` 依赖注入

### 6. 前端：登录/注册页面

创建 `frontend/src/pages/` 目录：
- `LoginPage.tsx`：邮箱 + 密码登录表单
- `RegisterPage.tsx`：邮箱 + 用户名 + 密码 + 确认密码注册表单
- 使用 `react-router-dom` 路由（如果已安装）或条件渲染

在 `App.tsx` 中：
- 未登录时显示登录/注册页面
- 登录后 token 保存到 localStorage
- 所有 API 请求自动携带 Authorization header
- 登录状态过期时自动跳转到登录页

### 7. 前端：ProtectedRoute 组件

创建 `frontend/src/components/ProtectedRoute.tsx`：
- 检查 localStorage 中是否有 access_token
- 无 token 时重定向到登录页
- 有 token 但过期时尝试 refresh

### 8. 测试
- 后端测试：`cd agent && source .venv/bin/activate && python -m pytest tests/ -q`（357 passed）
- 后端新增测试：test_auth_register, test_auth_login, test_auth_me, test_session_ownership
- 前端测试：`cd frontend && npm test`（132 passed）
- 前端新增测试：LoginPage 渲染/登录流程/RegisterPage 验证

### 9. 环境变量
在 `backend/.env.example` 中添加：
```
JWT_SECRET_KEY=<生成随机密钥>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
DATABASE_URL=postgresql+asyncpg://mahaoxuan@localhost:5432/econpaper
```

## 依赖
- 前置：PostgresSaver ✅（数据库连接已就绪）
- 后置：F11（Docker 部署配置）依赖本任务
- 后置：F12（S3 文件存储）依赖本任务

## 验收标准
- [ ] `/auth/register` 端点可注册新用户
- [ ] `/auth/login` 端点返回 JWT access_token
- [ ] `/auth/me` 端点返回当前用户信息（需 Authorization header）
- [ ] 前端登录页面可提交登录请求并保存 token
- [ ] 前端注册页面有表单验证（密码确认/邮箱格式）
- [ ] 未登录时重定向到登录页
- [ ] Session 与用户关联，用户只能访问自己的 session
- [ ] 所有现有后端测试（357 passed）仍然通过
- [ ] 所有现有前端测试（132 passed）仍然通过