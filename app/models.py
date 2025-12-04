"""
数据库模型
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Role(BaseModel):
    """角色模型"""
    __tablename__ = 'roles'
    
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='角色代码')
    description = db.Column(db.String(200), comment='角色描述')
    permissions = db.Column(db.Text, comment='权限列表（JSON格式）')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 关系
    users = db.relationship('User', backref='role', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    real_name = db.Column(db.String(100), comment='真实姓名')
    email = db.Column(db.String(120), comment='邮箱')
    phone = db.Column(db.String(20), comment='手机号')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, comment='角色ID')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'is_active': self.is_active,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class SystemConfig(BaseModel):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    key = db.Column(db.String(100), unique=True, nullable=False, comment='配置键')
    value = db.Column(db.Text, comment='配置值')
    description = db.Column(db.String(200), comment='配置描述')
    config_type = db.Column(db.String(50), default='text', comment='配置类型（text/image等）')
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'config_type': self.config_type,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
