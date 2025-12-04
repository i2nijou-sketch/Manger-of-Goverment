"""
路由定义
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from datetime import datetime
from app.models import User, Role, SystemConfig, db
from app.auth import login_required, admin_required, get_current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """首页 - 重定向到登录页或后台"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            })
        
        # 查询用户
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # 登录成功
            session['user_id'] = user.id
            session['username'] = user.username
            session['role_code'] = user.role.code if user.role else 'user'
            
            if remember:
                session.permanent = True
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'redirect': '/dashboard',
                'user': {
                    'username': user.username,
                    'real_name': user.real_name,
                    'role': user.role.name if user.role else '普通用户'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            })
    
    # 如果已登录，重定向到后台
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    # 获取系统配置
    config = SystemConfig.query.filter_by(key='app_name').first()
    app_name = config.value if config else '政企智能舆情分析报告生成智能体应用系统'
    
    return render_template('login.html', app_name=app_name)

@bp.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """后台管理首页"""
    user = get_current_user()
    config = SystemConfig.query.filter_by(key='app_name').first()
    app_name = config.value if config else '政企智能舆情分析报告生成智能体应用系统'
    
    return render_template('dashboard.html', user=user, app_name=app_name)

# ==================== 用户管理 ====================

@bp.route('/admin/users')
@admin_required
def admin_users():
    """用户管理页面"""
    return render_template('admin/users.html')

@bp.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    """获取用户列表"""
    users = User.query.all()
    return jsonify({
        'success': True,
        'data': [user.to_dict() for user in users]
    })

@bp.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    """创建用户"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    role_id = data.get('role_id')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'})
    
    if not role_id:
        return jsonify({'success': False, 'message': '请选择角色'})
    
    user = User(
        username=username,
        real_name=real_name,
        email=email,
        phone=phone,
        role_id=role_id,
        is_active=True
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '创建成功', 'data': user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})

@bp.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def api_get_user(user_id):
    """获取用户信息"""
    user = User.query.get_or_404(user_id)
    return jsonify({'success': True, 'data': user.to_dict()})

@bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    """更新用户"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': '用户名已存在'})
        user.username = data['username']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    user.real_name = data.get('real_name', user.real_name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.role_id = data.get('role_id', user.role_id)
    user.is_active = data.get('is_active', user.is_active)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功', 'data': user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == session.get('user_id'):
        return jsonify({'success': False, 'message': '不能删除当前登录用户'})
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# ==================== 角色管理 ====================

@bp.route('/admin/roles')
@admin_required
def admin_roles():
    """角色管理页面"""
    return render_template('admin/roles.html')

@bp.route('/api/roles', methods=['GET'])
@admin_required
def api_get_roles():
    """获取角色列表"""
    roles = Role.query.all()
    return jsonify({
        'success': True,
        'data': [role.to_dict() for role in roles]
    })

@bp.route('/api/roles', methods=['POST'])
@admin_required
def api_create_role():
    """创建角色"""
    data = request.get_json()
    name = data.get('name', '').strip()
    code = data.get('code', '').strip()
    description = data.get('description', '')
    
    if not name or not code:
        return jsonify({'success': False, 'message': '角色名称和代码不能为空'})
    
    if Role.query.filter_by(code=code).first():
        return jsonify({'success': False, 'message': '角色代码已存在'})
    
    role = Role(
        name=name,
        code=code,
        description=description,
        permissions=data.get('permissions', '[]'),
        is_active=True
    )
    
    try:
        db.session.add(role)
        db.session.commit()
        return jsonify({'success': True, 'message': '创建成功', 'data': role.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})

@bp.route('/api/roles/<int:role_id>', methods=['PUT'])
@admin_required
def api_update_role(role_id):
    """更新角色"""
    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    
    if 'code' in data and data['code'] != role.code:
        if Role.query.filter_by(code=data['code']).first():
            return jsonify({'success': False, 'message': '角色代码已存在'})
        role.code = data['code']
    
    role.name = data.get('name', role.name)
    role.description = data.get('description', role.description)
    role.permissions = data.get('permissions', role.permissions)
    role.is_active = data.get('is_active', role.is_active)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功', 'data': role.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

@bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@admin_required
def api_delete_role(role_id):
    """删除角色"""
    role = Role.query.get_or_404(role_id)
    
    # 检查是否有用户使用该角色
    if role.users:
        return jsonify({'success': False, 'message': '该角色下还有用户，无法删除'})
    
    try:
        db.session.delete(role)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# ==================== 系统设置 ====================

@bp.route('/admin/settings')
@admin_required
def admin_settings():
    """系统设置页面"""
    return render_template('admin/settings.html')

@bp.route('/api/settings', methods=['GET'])
@admin_required
def api_get_settings():
    """获取系统设置"""
    settings = SystemConfig.query.all()
    result = {}
    for setting in settings:
        result[setting.key] = {
            'value': setting.value,
            'description': setting.description,
            'config_type': setting.config_type
        }
    return jsonify({'success': True, 'data': result})

@bp.route('/api/settings', methods=['PUT'])
@admin_required
def api_update_settings():
    """更新系统设置"""
    data = request.get_json()
    
    for key, value in data.items():
        setting = SystemConfig.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SystemConfig(key=key, value=value, config_type='text')
            db.session.add(setting)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

# ==================== 其他接口 ====================

@bp.route('/api/current_user', methods=['GET'])
@login_required
def api_current_user():
    """获取当前用户信息"""
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'data': user.to_dict()})
    return jsonify({'success': False, 'message': '用户不存在'})

@bp.route('/api/upload/logo', methods=['POST'])
@admin_required
def api_upload_logo():
    """上传LOGO"""
    from werkzeug.utils import secure_filename
    import os
    from pathlib import Path
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'})
    
    # 允许的文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'success': False, 'message': '不支持的文件类型'})
    
    # 保存文件
    filename = secure_filename(file.filename)
    upload_dir = Path(__file__).parent.parent / 'static' / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = upload_dir / filename
    file.save(str(filepath))
    
    # 保存到系统配置
    logo_url = f'/static/uploads/{filename}'
    setting = SystemConfig.query.filter_by(key='logo_url').first()
    if setting:
        setting.value = logo_url
    else:
        setting = SystemConfig(key='logo_url', value=logo_url, config_type='image')
        db.session.add(setting)
    db.session.commit()
    
    return jsonify({'success': True, 'url': logo_url, 'message': '上传成功'})

# ==================== 数据抓取 ====================

@bp.route('/crawler')
@login_required
def crawler_page():
    """数据抓取页面"""
    return render_template('crawler.html')

@bp.route('/api/crawler/search', methods=['POST'])
@login_required
def api_crawler_search():
    """数据抓取接口"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        max_results = data.get('max_results', 10)
        
        if not keyword:
            return jsonify({
                'success': False,
                'message': '请输入搜索关键字'
            })
        
        # 限制最大结果数
        max_results = min(int(max_results), 50)
        
        # 调用爬虫
        from app.crawler import crawl_news
        news_list = crawl_news(keyword, max_results)
        
        return jsonify({
            'success': True,
            'message': f'成功抓取 {len(news_list)} 条数据',
            'data': news_list,
            'count': len(news_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'抓取失败: {str(e)}'
        })

@bp.route('/api/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '系统运行正常'
    })

