# 政企智能舆情分析报告生成智能体应用系统

## 项目简介

政企智能舆情分析报告生成智能体应用系统是一个基于B/S架构的Web应用，提供用户认证、后台管理、角色权限管理等功能。

## 技术栈

- **前端**: B/S架构 + Ayu组件 + Layui
- **后端**: Python 3 + Flask
- **数据库**: SQLite
- **认证**: 基于Session的用户认证系统

## 目录结构

```
project/
├── app/                      # 应用主代码
│   ├── __init__.py           # Flask应用初始化
│   ├── models.py             # 数据库模型（User、Role、SystemConfig）
│   ├── routes.py             # 路由定义
│   └── auth.py               # 认证相关工具函数
├── migrations/               # 数据库迁移文件
├── tests/                    # 测试文件
├── static/                   # 静态文件（CSS、JS、图片等）
│   ├── layui/                # Layui组件
│   ├── ayu/                  # Ayu组件（需手动拷贝）
│   └── uploads/              # 上传文件目录
├── templates/                # 模板文件
│   ├── base.html             # 基础模板
│   ├── index.html            # 首页模板
│   ├── login.html            # 登录页面
│   ├── dashboard.html        # 后台管理首页
│   └── admin/                # 后台管理页面
│       ├── users.html        # 用户管理
│       ├── user_form.html    # 用户表单
│       ├── roles.html        # 角色管理
│       └── settings.html     # 系统设置
├── docs/                     # 文档
├── requirements/             # 依赖管理
├── tools/                    # 工具脚本
├── envs/                     # 环境配置
├── venv/                     # Python虚拟环境
├── config.py                 # 配置文件
├── run.py                    # 应用启动文件
├── requirements.txt          # Python依赖列表
├── test_app.py               # 测试脚本
├── start.bat                 # Windows启动脚本
├── start.ps1                 # PowerShell启动脚本
├── .gitignore                # Git忽略文件
├── data.db                   # SQLite数据库文件（自动生成）
└── README.md                 # 项目说明
```

## 安装

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用

### 启动应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动

### 默认账户

- **管理员账户**: `admin` / `admin123`
- **角色说明**:
  - **管理员(admin)**: 拥有所有功能的权限，包括用户管理、角色管理、系统设置
  - **普通用户(user)**: 登录后可以看到数据报表和最新的报告

### 功能模块

#### 1. 登录功能
- 用户名密码登录
- 密码加密存储
- 记住我功能
- Session会话管理

#### 2. 后台管理
- **Dashboard**: 系统概览、统计数据
- **用户管理**: 用户的增删改查
- **角色管理**: 角色的增删改查
- **系统设置**: 应用名称、LOGO设置

#### 3. 权限控制
- 基于角色的权限控制(RBAC)
- 路由级别的权限保护
- 管理员和普通用户权限区分

### 测试应用

运行测试脚本验证应用是否正常：

```bash
python test_app.py
```

### API接口

#### 认证相关
- `GET /` - 首页（自动重定向）
- `GET /login` - 登录页面
- `POST /login` - 登录接口
- `GET /logout` - 退出登录
- `GET /dashboard` - 后台管理首页（需登录）

#### 用户管理（需管理员权限）
- `GET /admin/users` - 用户管理页面
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `GET /api/users/<id>` - 获取用户信息
- `PUT /api/users/<id>` - 更新用户
- `DELETE /api/users/<id>` - 删除用户

#### 角色管理（需管理员权限）
- `GET /admin/roles` - 角色管理页面
- `GET /api/roles` - 获取角色列表
- `POST /api/roles` - 创建角色
- `PUT /api/roles/<id>` - 更新角色
- `DELETE /api/roles/<id>` - 删除角色

#### 系统设置（需管理员权限）
- `GET /admin/settings` - 系统设置页面
- `GET /api/settings` - 获取系统设置
- `PUT /api/settings` - 更新系统设置

#### 其他
- `GET /api/health` - 健康检查接口
- `GET /api/current_user` - 获取当前用户信息（需登录）

## 开发说明

### 添加新路由

在 `app/routes.py` 中添加新的路由函数：

```python
@bp.route('/your-route')
def your_function():
    return render_template('your_template.html')
```

### 添加数据库模型

在 `app/models.py` 中定义新的模型类：

```python
class YourModel(BaseModel):
    field1 = db.Column(db.String(80), nullable=False)
    field2 = db.Column(db.Integer)
```

### 使用Ayu组件

在模板中引用Ayu组件：

```html
<link rel="stylesheet" href="{{ url_for('static', filename='ayu/css/ayu.css') }}">
<script src="{{ url_for('static', filename='ayu/js/ayu.js') }}"></script>
```

## 贡献
