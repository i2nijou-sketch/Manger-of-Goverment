"""
认证相关工具函数
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from app.models import User, Role, SystemConfig, db

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': '请先登录'}), 401
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': '请先登录'}), 401
            return redirect(url_for('main.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.role or user.role.code != 'admin':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': '权限不足'}), 403
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前登录用户"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def init_default_data():
    """初始化默认数据"""
    # 创建默认角色
    admin_role = Role.query.filter_by(code='admin').first()
    if not admin_role:
        admin_role = Role(
            name='管理员',
            code='admin',
            description='拥有所有功能的权限',
            permissions='["*"]'
        )
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(code='user').first()
    if not user_role:
        user_role = Role(
            name='普通用户',
            code='user',
            description='登录后可以看到数据报表和最新的报告',
            permissions='["view_report", "view_dashboard"]'
        )
        db.session.add(user_role)
    
    # 创建默认管理员账户
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            real_name='系统管理员',
            email='admin@example.com',
            role_id=admin_role.id,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
    
    # 初始化系统配置
    app_name = SystemConfig.query.filter_by(key='app_name').first()
    if not app_name:
        app_name = SystemConfig(
            key='app_name',
            value='政企智能舆情分析报告生成智能体应用系统',
            description='应用名称',
            config_type='text'
        )
        db.session.add(app_name)
    
    db.session.commit()

